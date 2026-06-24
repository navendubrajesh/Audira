"""Analysis orchestration — fast lane text scoring + neuro mapping."""

from __future__ import annotations

import hashlib
import sys
import time
from pathlib import Path
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.analysis import AnalysisRun
from app.models.audience import Audience
from app.models.context import BrandProfile, StandardsRule
from app.services.scoring.brand import score_brand_alignment
from app.services.scoring.composite import composite_score
from app.services.scoring.inclusive import score_inclusive_language
from app.services.scoring.jargon import score_jargon_density
from app.services.scoring.readability import score_readability
from app.services.scoring.tone import score_tone
from app.services.tenant_service import assert_tenant_resource, TenantIsolationError

SHARED = Path(__file__).resolve().parents[3] / "shared"
if str(SHARED) not in sys.path:
    sys.path.insert(0, str(SHARED))

from resonode_core.inference.factory import build_provider
from resonode_core.inference.types import InferenceRequest, Modality
from resonode_core.mapping.metrics import MAPPING_VERSION, map_tribe_output

from app.config import settings


async def _latest_brand(db: AsyncSession, tenant_id: UUID) -> BrandProfile | None:
    result = await db.execute(
        select(BrandProfile)
        .where(BrandProfile.tenant_id == tenant_id, BrandProfile.status == "published")
        .order_by(BrandProfile.version.desc())
        .limit(1)
    )
    return result.scalar_one_or_none()


async def _standards_rules(db: AsyncSession, tenant_id: UUID) -> list[dict]:
    result = await db.execute(
        select(StandardsRule).where(
            StandardsRule.tenant_id == tenant_id,
            StandardsRule.status == "published",
            StandardsRule.rule_type == "inclusive",
        )
    )
    rules = result.scalars().all()
    return [
        {"pattern": r.pattern, "replacement": r.replacement, "metadata": r.metadata_}
        for r in rules
    ]


def _rewrite_suggestions(metrics: dict, text: str) -> list[dict]:
    """TCA-020 — lightweight rewrite hints from flagged issues."""
    suggestions: list[dict] = []
    for flag in metrics.get("inclusive", {}).get("flags", []):
        suggestions.append(
            {
                "type": "inclusive",
                "original": flag.get("term"),
                "suggestion": flag.get("suggestion"),
            }
        )
    for term in metrics.get("brand", {}).get("prohibited_terms", []):
        suggestions.append(
            {"type": "brand", "original": term, "suggestion": "Remove or replace per brand guide."}
        )
    if metrics.get("readability", {}).get("grade_level", 0) > 14:
        suggestions.append(
            {
                "type": "readability",
                "original": text[:80] + ("…" if len(text) > 80 else ""),
                "suggestion": "Shorten sentences and reduce grade level for broader audiences.",
            }
        )
    return suggestions[:10]


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
) -> AnalysisRun:
    audience: Audience | None = None
    if audience_id:
        audience = await db.get(Audience, audience_id)
        if audience:
            try:
                assert_tenant_resource(audience.tenant_id, tenant_id)
            except TenantIsolationError:
                audience = None

    brand = await _latest_brand(db, tenant_id)
    standards = await _standards_rules(db, tenant_id)

    started = time.perf_counter()
    readability = score_readability(text)
    jargon = score_jargon_density(text)
    inclusive = score_inclusive_language(text, standards)
    brand_score = score_brand_alignment(
        text,
        terminology_do=brand.terminology_do if brand else [],
        terminology_dont=brand.terminology_dont if brand else [],
        messaging_pillars=brand.messaging_pillars if brand else [],
    )
    tone = score_tone(text, target_tone=brand.target_tone if brand else "professional")

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

    metrics = {
        "readability": readability,
        "jargon": jargon,
        "inclusive": inclusive,
        "brand": brand_score,
        "tone": tone,
        "engagement": {"score": neuro["engagement"]},
        "clarity": {"score": neuro["clarity"]},
        "trust": {"score": neuro["trust"]},
        "action_intent": {"score": neuro["action_intent"]},
        "neuro": neuro,
    }
    composite = composite_score(metrics)
    suggestions = _rewrite_suggestions(metrics, text)
    latency_ms = int((time.perf_counter() - started) * 1000) + inference.latency_ms

    run = AnalysisRun(
        tenant_id=tenant_id,
        user_id=user_id,
        audience_id=audience.id if audience else None,
        artifact_type_code=artifact_type_code,
        objective=objective,
        channel=channel,
        input_text=text,
        input_hash=hashlib.sha256(text.encode()).hexdigest(),
        model_id=model_id,
        model_version="1.0.0",
        mapping_version=MAPPING_VERSION,
        composite_score=composite,
        latency_ms=latency_ms,
        result={
            "metrics": metrics,
            "composite_score": composite,
            "rewrite_suggestions": suggestions,
            "inference": {
                "provider": inference.provider,
                "latency_ms": inference.latency_ms,
                "cost_usd": inference.cost_usd,
            },
            "personalization": {
                "audience": audience.name if audience else None,
                "objective": objective,
                "channel": channel,
            },
        },
    )
    db.add(run)
    await db.commit()
    await db.refresh(run)
    return run
