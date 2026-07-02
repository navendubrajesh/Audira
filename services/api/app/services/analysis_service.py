"""Analysis orchestration — fast lane, full neuro path, heatmaps, PII."""

from __future__ import annotations

import hashlib
import sys
import time
from pathlib import Path
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.analysis import AnalysisRun
from app.models.audience import Audience
from app.models.context import ArtifactType, BrandProfile, StandardsRule
from app.models.governance import ModelRegistryEntry, TenantPrivacySettings
from app.services.heatmap import generate_attention_heatmap
from app.services.scoring.brand import score_brand_alignment
from app.services.scoring.composite import composite_score, quality_verdict, weights_for_objective
from app.services.scoring.inclusive import score_inclusive_language
from app.services.scoring.jargon import score_jargon_density
from app.services.scoring.pii import detect_pii, redact_pii
from app.services.scoring.readability import score_readability
from app.services.scoring.structure import score_structure
from app.services.scoring.tone import score_tone
from app.services.tenant_service import TenantIsolationError, assert_tenant_resource

SHARED = Path(__file__).resolve().parents[3] / "shared"
if str(SHARED) not in sys.path:
    sys.path.insert(0, str(SHARED))

from audira_core.inference.factory import build_provider
from audira_core.inference.types import InferenceRequest, Modality
from audira_core.mapping.metrics import MAPPING_VERSION, map_tribe_output

from app.config import settings

ALL_CHECKS = frozenset(
    {"readability", "jargon", "inclusive", "brand", "tone", "structure", "engagement", "heatmap"}
)


async def _latest_brand(db: AsyncSession, tenant_id: UUID) -> BrandProfile | None:
    result = await db.execute(
        select(BrandProfile)
        .where(BrandProfile.tenant_id == tenant_id, BrandProfile.status == "published")
        .order_by(BrandProfile.version.desc())
        .limit(1)
    )
    return result.scalar_one_or_none()


async def _standards_by_type(db: AsyncSession, tenant_id: UUID) -> dict[str, list[StandardsRule]]:
    result = await db.execute(
        select(StandardsRule).where(
            StandardsRule.tenant_id == tenant_id,
            StandardsRule.status == "published",
        )
    )
    grouped: dict[str, list[StandardsRule]] = {"inclusive": [], "jargon": []}
    for rule in result.scalars().all():
        grouped.setdefault(rule.rule_type, []).append(rule)
    return grouped


async def _artifact_checks(
    db: AsyncSession, tenant_id: UUID, artifact_type_code: str | None
) -> list[str]:
    if not artifact_type_code:
        return list(ALL_CHECKS)
    result = await db.execute(
        select(ArtifactType).where(
            ArtifactType.tenant_id == tenant_id,
            ArtifactType.code == artifact_type_code,
        )
    )
    artifact = result.scalar_one_or_none()
    if not artifact or not artifact.checks:
        return list(ALL_CHECKS)
    checks = set(artifact.checks) & ALL_CHECKS
    return list(checks) if checks else list(ALL_CHECKS)


async def _validate_model_licence(db: AsyncSession, model_id: str) -> None:
    if model_id in ("tribe-v2-stub", "mock-gpu"):
        return
    result = await db.execute(
        select(ModelRegistryEntry).where(ModelRegistryEntry.model_id == model_id)
    )
    entry = result.scalar_one_or_none()
    if not entry:
        raise HTTPException(status_code=400, detail=f"Unknown model: {model_id}")
    if not entry.commercial_ok and settings.environment == "production":
        raise HTTPException(
            status_code=403,
            detail=f"Model {model_id} is not approved for commercial use (licence: {entry.licence}).",
        )


async def _apply_privacy(db: AsyncSession, tenant_id: UUID, text: str) -> tuple[str, dict]:
    settings_row = await db.get(TenantPrivacySettings, tenant_id)
    pii_findings = detect_pii(text)
    meta: dict = {"pii_detected": len(pii_findings), "redacted": False}
    if settings_row and settings_row.pii_redaction and pii_findings:
        text, _ = redact_pii(text)
        meta["redacted"] = True
    elif pii_findings:
        meta["findings"] = pii_findings[:10]
    return text, meta


def _rewrite_suggestions(metrics: dict, text: str) -> list[dict]:
    """TCA-020 / TCA-042 — prioritized rewrite hints."""
    suggestions: list[dict] = []
    for flag in metrics.get("inclusive", {}).get("flags", []):
        suggestions.append(
            {
                "type": "inclusive",
                "priority": "high",
                "original": flag.get("term"),
                "suggestion": flag.get("suggestion"),
            }
        )
    for term in metrics.get("brand", {}).get("prohibited_terms", []):
        suggestions.append(
            {
                "type": "brand",
                "priority": "high",
                "original": term,
                "suggestion": "Remove or replace per brand guide.",
            }
        )
    for item in metrics.get("jargon", {}).get("flagged_terms", []):
        suggestions.append(
            {
                "type": "jargon",
                "priority": "medium",
                "original": item.get("term"),
                "suggestion": item.get("alternative"),
            }
        )
    for flag in metrics.get("readability", {}).get("flags", []):
        suggestions.append(
            {
                "type": "readability",
                "priority": "medium",
                "original": flag.get("text"),
                "suggestion": flag.get("suggestion"),
            }
        )
    suggestions.sort(key=lambda x: 0 if x.get("priority") == "high" else 1)
    return suggestions[:15]


async def run_text_analysis(
    db: AsyncSession,
    *,
    tenant_id: UUID,
    user_id: UUID,
    text: str,
    audience_id: UUID | None = None,
    artifact_type_code: str | None = None,
    objective: str | None = None,
    channel: str | None = None,
    model_id: str = "tribe-v2-stub",
    fast_lane: bool = True,
    full_analysis: bool = False,
) -> AnalysisRun:
    await _validate_model_licence(db, model_id)

    audience: Audience | None = None
    if audience_id:
        audience = await db.get(Audience, audience_id)
        if audience:
            try:
                assert_tenant_resource(audience.tenant_id, tenant_id)
            except TenantIsolationError:
                audience = None

    text, privacy_meta = await _apply_privacy(db, tenant_id, text)
    brand = await _latest_brand(db, tenant_id)
    standards = await _standards_by_type(db, tenant_id)
    checks = await _artifact_checks(db, tenant_id, artifact_type_code)

    inclusive_rules = [
        {"pattern": r.pattern, "replacement": r.replacement, "metadata": r.metadata_}
        for r in standards.get("inclusive", [])
    ]
    banned_jargon = [r.pattern for r in standards.get("jargon", [])]
    jargon_replacements = {
        r.pattern.lower(): r.replacement or ""
        for r in standards.get("jargon", [])
        if r.replacement
    }

    started = time.perf_counter()
    metrics: dict = {}

    if "readability" in checks:
        metrics["readability"] = score_readability(text)
    if "jargon" in checks:
        metrics["jargon"] = score_jargon_density(
            text, banned_terms=banned_jargon, replacements=jargon_replacements
        )
    if "inclusive" in checks:
        metrics["inclusive"] = score_inclusive_language(
            text,
            inclusive_rules,
            region=(audience.region if audience else None),
        )
    if "brand" in checks:
        metrics["brand"] = score_brand_alignment(
            text,
            terminology_do=brand.terminology_do if brand else [],
            terminology_dont=brand.terminology_dont if brand else [],
            messaging_pillars=brand.messaging_pillars if brand else [],
        )
    if "tone" in checks:
        metrics["tone"] = score_tone(text, target_tone=brand.target_tone if brand else "professional")
    if "structure" in checks:
        metrics["structure"] = score_structure(text, channel=channel or artifact_type_code)

    inference_meta: dict = {"skipped": True, "reason": "fast_lane"}
    run_full = full_analysis or (not fast_lane)

    if run_full and "engagement" in checks:
        provider = build_provider(
            model_id=model_id,
            inference_base_url=settings.inference_base_url,
            inference_api_key=settings.inference_api_key,
        )
        inference = await provider.run(
            InferenceRequest(
                modality=Modality.TEXT,
                payload={"text": text, "artifact_type": artifact_type_code},
                model_id=model_id,
            )
        )
        neuro = map_tribe_output(
            inference.output,
            audience_attributes=audience.attributes if audience else {},
            objective=objective,
            channel=channel or artifact_type_code,
        )
        metrics["engagement"] = {"score": neuro["engagement"]}
        metrics["clarity"] = {"score": neuro["clarity"]}
        metrics["trust"] = {"score": neuro["trust"]}
        metrics["action_intent"] = {"score": neuro["action_intent"]}
        metrics["neuro"] = neuro
        inference_meta = {
            "skipped": False,
            "provider": inference.provider,
            "latency_ms": inference.latency_ms,
            "cost_usd": inference.cost_usd,
        }
    elif "engagement" in checks:
        metrics["engagement"] = {"score": 68.0, "proxy": True}
        metrics["clarity"] = {"score": 65.0, "proxy": True}
        metrics["trust"] = {"score": 66.0, "proxy": True}
        metrics["action_intent"] = {"score": 62.0, "proxy": True}

    if "heatmap" in checks or run_full:
        metrics["heatmap"] = generate_attention_heatmap(text)

    weight_profile = weights_for_objective(objective)
    composite = composite_score(metrics, objective=objective, weights=weight_profile)
    verdict = quality_verdict(composite)
    suggestions = _rewrite_suggestions(metrics, text)
    latency_ms = int((time.perf_counter() - started) * 1000)
    if not inference_meta.get("skipped"):
        latency_ms += inference_meta.get("latency_ms", 0)

    run = AnalysisRun(
        tenant_id=tenant_id,
        user_id=user_id,
        audience_id=audience.id if audience else None,
        artifact_type_code=artifact_type_code,
        objective=objective,
        channel=channel,
        input_text=text,
        input_hash=hashlib.sha256(text.encode()).hexdigest(),
        model_id=model_id if run_full else "fast-lane",
        model_version="1.0.0",
        mapping_version=MAPPING_VERSION if run_full else "fast-lane",
        composite_score=composite,
        latency_ms=latency_ms,
        result={
            "metrics": metrics,
            "composite_score": composite,
            "verdict": verdict,
            "weight_profile": weight_profile,
            "checks_run": checks,
            "rewrite_suggestions": suggestions,
            "inference": inference_meta,
            "privacy": privacy_meta,
            "personalization": {
                "audience": audience.name if audience else None,
                "objective": objective,
                "channel": channel,
            },
            "can_upgrade": fast_lane and not full_analysis,
        },
    )
    db.add(run)
    await db.commit()
    await db.refresh(run)
    return run


async def rerun_analysis(db: AsyncSession, run_id: UUID, tenant_id: UUID, user_id: UUID) -> AnalysisRun:
    """TCA-019 — reproduce analysis from stored inputs."""
    original = await db.get(AnalysisRun, run_id)
    if not original:
        raise HTTPException(status_code=404, detail="Analysis not found")
    try:
        assert_tenant_resource(original.tenant_id, tenant_id)
    except TenantIsolationError:
        raise HTTPException(status_code=404, detail="Analysis not found") from None
    if not original.input_text:
        raise HTTPException(status_code=400, detail="No input text to replay")
    full = original.model_id not in ("fast-lane",)
    return await run_text_analysis(
        db,
        tenant_id=tenant_id,
        user_id=user_id,
        text=original.input_text,
        audience_id=original.audience_id,
        artifact_type_code=original.artifact_type_code,
        objective=original.objective,
        channel=original.channel,
        model_id=original.model_id if full else "tribe-v2-stub",
        fast_lane=not full,
        full_analysis=full,
    )
