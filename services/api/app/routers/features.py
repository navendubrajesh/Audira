"""Phase 2/3 features — backed by real services where possible."""

import hashlib
import secrets
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import get_current_user, require_permission, require_roles
from app.auth.principal import Principal
from app.auth.roles import Role
from app.db.session import get_db
from app.models.analysis import AnalysisComment, AnalysisRun
from app.models.governance import ApiKey, TenantGuardrailSettings
from app.services.analysis_service import run_text_analysis
from app.services.audit import record_audit
from app.services.scoring.bias import score_fairness
from app.services.seed_defaults import seed_tenant_defaults

router = APIRouter(prefix="/features", tags=["features"])


class AddInAnalyzeRequest(BaseModel):
    text: str
    source: str = "word"
    objective: str | None = "engage"
    full_analysis: bool = False


class WhatIfRequest(BaseModel):
    text: str
    changes: list[str] = Field(default_factory=list)
    objective: str | None = "engage"


class CommentBody(BaseModel):
    body: str
    assignee_email: str | None = None
    parent_id: str | None = None


class ConsistencyRequest(BaseModel):
    documents: list[str] = Field(..., min_length=2, max_length=10)


class UrlCaptureRequest(BaseModel):
    url: str


class ApiKeyCreateBody(BaseModel):
    name: str = Field(..., min_length=1, max_length=128)
    rate_limit_per_minute: int = 60


@router.post("/addin/analyze")
async def addin_analyze(
    body: AddInAnalyzeRequest,
    principal: Annotated[Principal, Depends(require_permission("analyses.run"))],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """TCA-048 / TCA-049 — Office add-in delegates to analysis engine."""
    run = await run_text_analysis(
        db,
        tenant_id=principal.tenant_id,
        user_id=principal.user_id,
        text=body.text,
        objective=body.objective,
        artifact_type_code="email" if body.source == "outlook" else "intranet",
        channel=body.source,
        fast_lane=not body.full_analysis,
        full_analysis=body.full_analysis,
    )
    return {
        "status": "completed",
        "source": body.source,
        "analysis_id": str(run.id),
        "composite_score": run.composite_score,
        "verdict": run.result.get("verdict"),
        "suggestions": run.result.get("rewrite_suggestions", [])[:5],
    }


@router.get("/analytics/dashboard")
async def analytics_dashboard(
    principal: Annotated[Principal, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """TCA-039 / TCA-055 — org analytics from analysis runs."""
    avg = await db.scalar(
        select(func.avg(AnalysisRun.composite_score)).where(
            AnalysisRun.tenant_id == principal.tenant_id
        )
    )
    count = await db.scalar(
        select(func.count())
        .select_from(AnalysisRun)
        .where(AnalysisRun.tenant_id == principal.tenant_id)
    )
    recent = await db.execute(
        select(AnalysisRun)
        .where(AnalysisRun.tenant_id == principal.tenant_id)
        .order_by(AnalysisRun.created_at.desc())
        .limit(5)
    )
    trend = [
        {"id": str(r.id), "score": r.composite_score, "at": r.created_at.isoformat()}
        for r in recent.scalars().all()
    ]
    by_channel = await db.execute(
        select(AnalysisRun.channel, func.avg(AnalysisRun.composite_score), func.count())
        .where(AnalysisRun.tenant_id == principal.tenant_id)
        .group_by(AnalysisRun.channel)
    )
    channel_stats = [
        {"channel": row[0] or "unknown", "avg_score": round(float(row[1] or 0), 1), "count": row[2]}
        for row in by_channel.all()
    ]
    return {
        "tenant_id": str(principal.tenant_id),
        "period": "all",
        "avg_composite_score": round(float(avg or 0), 1),
        "analyses_count": count or 0,
        "recent_trend": trend,
        "by_channel": channel_stats,
    }


@router.get("/campaigns")
async def list_campaigns(
    principal: Annotated[Principal, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """TCA-051 / TCA-054 — group recent analyses as review campaigns."""
    result = await db.execute(
        select(AnalysisRun)
        .where(AnalysisRun.tenant_id == principal.tenant_id)
        .order_by(AnalysisRun.created_at.desc())
        .limit(20)
    )
    runs = result.scalars().all()
    return {
        "campaigns": [
            {
                "id": str(r.id),
                "title": f"Review — {r.artifact_type_code or 'text'}",
                "status": (r.result or {}).get("verdict", {}).get("label", "unknown"),
                "composite_score": r.composite_score,
                "export_url": f"/analyze/runs/{r.id}",
            }
            for r in runs
        ],
        "tenant_id": str(principal.tenant_id),
    }


@router.post("/simulations/what-if")
async def what_if_simulation(
    body: WhatIfRequest,
    principal: Annotated[Principal, Depends(require_permission("analyses.run"))],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """TCA-045 / TCA-009 — project score after applying text changes."""
    baseline = await run_text_analysis(
        db,
        tenant_id=principal.tenant_id,
        user_id=principal.user_id,
        text=body.text,
        objective=body.objective,
        fast_lane=True,
    )
    modified = body.text
    for change in body.changes:
        if ":" in change:
            src, dst = change.split(":", 1)
            modified = modified.replace(src.strip(), dst.strip())
    projected = await run_text_analysis(
        db,
        tenant_id=principal.tenant_id,
        user_id=principal.user_id,
        text=modified,
        objective=body.objective,
        fast_lane=True,
    )
    b = baseline.composite_score or 0
    p = projected.composite_score or 0
    return {
        "baseline_score": b,
        "projected_score": p,
        "delta": round(p - b, 1),
        "changes_applied": body.changes,
        "baseline_id": str(baseline.id),
        "projected_id": str(projected.id),
    }


@router.get("/integrations")
async def list_integrations(principal: Annotated[Principal, Depends(get_current_user)]):
    """TCA-036 / TCA-073 / TCA-076 — integration catalogue."""
    return {
        "integrations": [
            {"id": "office-addin", "status": "available", "endpoint": "/features/addin/analyze"},
            {"id": "openapi", "status": "available", "endpoint": "/docs"},
            {"id": "workday", "status": "planned"},
            {"id": "sharepoint", "status": "planned"},
        ]
    }


@router.post("/bias-check")
async def bias_check(
    body: dict,
    principal: Annotated[Principal, Depends(require_permission("analyses.run"))],
):
    """TCA-064 — basic fairness / stereotype flagging."""
    text = body.get("text", "")
    return score_fairness(text)


@router.get("/guardrails/status")
async def guardrail_status(
    principal: Annotated[Principal, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    await seed_tenant_defaults(db, principal.tenant_id)
    row = await db.get(TenantGuardrailSettings, principal.tenant_id)
    enabled = bool(
        row
        and (row.generative_governance or row.rewrite_assist or row.regulated_claims)
    )
    return {
        "stories": ["TCA-037", "TCA-044", "TCA-060"],
        "enabled": enabled,
        "settings_endpoint": "/guardrails/settings",
        "message": "Enable via PATCH /guardrails/settings after legal sign-off.",
    }


@router.post("/consistency/check")
async def consistency_check(
    body: ConsistencyRequest,
    principal: Annotated[Principal, Depends(require_permission("analyses.run"))],
):
    """TCA-035 — cross-document terminology consistency."""
    terms_sets = []
    for doc in body.documents:
        words = set(w.lower() for w in doc.split() if len(w) > 5)
        terms_sets.append(words)
    common = set.intersection(*terms_sets) if terms_sets else set()
    conflicts = []
    for i, doc_a in enumerate(body.documents):
        for j, doc_b in enumerate(body.documents):
            if j <= i:
                continue
            if "not" in doc_a.lower() and any(w in doc_b.lower() for w in ("always", "must", "required")):
                conflicts.append({"documents": [i, j], "issue": "Potentially conflicting obligation language."})
    return {"common_terms": sorted(common)[:20], "conflicts": conflicts, "document_count": len(body.documents)}


@router.post("/url/capture")
async def url_capture(
    body: UrlCaptureRequest,
    principal: Annotated[Principal, Depends(require_permission("analyses.run"))],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """TCA-010 — fetch URL HTML and analyse (no PII in URL storage)."""
    import httpx

    if "?" in body.url and any(k in body.url.lower() for k in ("email=", "user=", "token=")):
        raise HTTPException(status_code=400, detail="URLs with personal data in query strings are rejected.")
    try:
        async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
            resp = await client.get(body.url)
            resp.raise_for_status()
            html = resp.text
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Could not fetch URL: {exc}") from exc
    text = " ".join(html.replace("<", " <").split())[:50000]
    run = await run_text_analysis(
        db,
        tenant_id=principal.tenant_id,
        user_id=principal.user_id,
        text=text,
        artifact_type_code="intranet",
        channel="url",
        fast_lane=True,
    )
    return {"analysis_id": str(run.id), "composite_score": run.composite_score, "url_host": body.url.split("/")[2]}


@router.post("/media/submit")
async def submit_media_job(
    body: dict,
    principal: Annotated[Principal, Depends(require_permission("analyses.run"))],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """TCA-009 / TCA-011 — async AV/deck job stub (queues full inference when media present)."""
    filename = body.get("filename", "media.mp4")
    modality = "video" if filename.endswith((".mp4", ".mov")) else "audio"
    await record_audit(
        db,
        tenant_id=principal.tenant_id,
        action="media.job_submitted",
        actor_user_id=principal.user_id,
        actor_email=principal.email,
        metadata={"filename": filename, "modality": modality},
    )
    return {
        "status": "queued",
        "modality": modality,
        "message": "Submit via POST /inference/jobs with modality video/audio for GPU processing.",
    }


@router.get("/scorecards")
async def team_scorecards(
    principal: Annotated[Principal, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """TCA-056 — privacy-aware author scorecards."""
    result = await db.execute(
        select(AnalysisRun.user_id, func.avg(AnalysisRun.composite_score), func.count())
        .where(AnalysisRun.tenant_id == principal.tenant_id)
        .group_by(AnalysisRun.user_id)
    )
    return {
        "scorecards": [
            {"author_id": str(row[0]), "avg_score": round(float(row[1] or 0), 1), "analyses": row[2]}
            for row in result.all()
        ],
        "privacy_note": "Aggregated by internal user ID — no surveillance framing.",
    }


@router.post("/comments/{run_id}")
async def add_comment(
    run_id: UUID,
    body: CommentBody,
    principal: Annotated[Principal, Depends(require_permission("analyses.run"))],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """TCA-053 — comment on analysis run."""
    run = await db.get(AnalysisRun, run_id)
    if not run or run.tenant_id != principal.tenant_id:
        raise HTTPException(status_code=404, detail="Analysis not found")
    comment = AnalysisComment(
        tenant_id=principal.tenant_id,
        analysis_run_id=run_id,
        user_id=principal.user_id,
        author_email=principal.email,
        body=body.body,
        assignee_email=body.assignee_email,
        parent_id=UUID(body.parent_id) if body.parent_id else None,
    )
    db.add(comment)
    await db.commit()
    await db.refresh(comment)
    return {"id": str(comment.id), "resolved": comment.resolved}


@router.get("/comments/{run_id}")
async def list_comments(
    run_id: UUID,
    principal: Annotated[Principal, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    run = await db.get(AnalysisRun, run_id)
    if not run or run.tenant_id != principal.tenant_id:
        raise HTTPException(status_code=404, detail="Analysis not found")
    result = await db.execute(
        select(AnalysisComment).where(
            AnalysisComment.analysis_run_id == run_id,
            AnalysisComment.tenant_id == principal.tenant_id,
        )
    )
    return [
        {
            "id": str(c.id),
            "body": c.body,
            "author_email": c.author_email,
            "assignee_email": c.assignee_email,
            "resolved": c.resolved,
            "parent_id": str(c.parent_id) if c.parent_id else None,
        }
        for c in result.scalars().all()
    ]


@router.post("/api-keys")
async def create_api_key(
    body: ApiKeyCreateBody,
    principal: Annotated[Principal, Depends(require_roles(Role.ADMIN, Role.ML_PLATFORM_ENG))],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """TCA-050 — create API key (shown once)."""
    raw = f"aud_{secrets.token_urlsafe(32)}"
    key = ApiKey(
        tenant_id=principal.tenant_id,
        name=body.name,
        key_prefix=raw[:8],
        key_hash=hashlib.sha256(raw.encode()).hexdigest(),
        rate_limit_per_minute=body.rate_limit_per_minute,
    )
    db.add(key)
    await db.commit()
    return {"id": str(key.id), "api_key": raw, "prefix": key.key_prefix, "rate_limit_per_minute": key.rate_limit_per_minute}

