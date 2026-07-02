"""Phase 2/3 features — backed by real services where possible."""

from typing import Annotated

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import get_current_user, require_permission
from app.auth.principal import Principal
from app.db.session import get_db
from app.models.analysis import AnalysisRun
from app.services.analysis_service import run_text_analysis
from app.services.scoring.bias import score_fairness

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
    return {
        "tenant_id": str(principal.tenant_id),
        "period": "all",
        "avg_composite_score": round(float(avg or 0), 1),
        "analyses_count": count or 0,
        "recent_trend": trend,
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
async def guardrail_status(principal: Annotated[Principal, Depends(get_current_user)]):
    return {
        "stories": ["TCA-037", "TCA-044", "TCA-060"],
        "enabled": False,
        "message": "Guardrail stories require product/legal sign-off before activation.",
    }
