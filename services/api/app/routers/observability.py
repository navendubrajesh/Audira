"""Observability endpoints (TCA-075)."""

from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import get_current_user, require_roles
from app.auth.principal import Principal
from app.auth.roles import Role
from app.config import settings
from app.db.session import get_db
from app.models.analysis import AnalysisRun
from app.models.inference_job import InferenceJob

router = APIRouter(prefix="/observability", tags=["observability"])


@router.get("/health-detail")
async def health_detail(
    principal: Annotated[
        Principal, Depends(require_roles(Role.ML_PLATFORM_ENG, Role.ADMIN, Role.SECURITY))
    ],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    jobs_completed = await db.scalar(
        select(func.count())
        .select_from(InferenceJob)
        .where(
            InferenceJob.tenant_id == principal.tenant_id,
            InferenceJob.status.in_(["completed", "cached"]),
        )
    )
    analyses = await db.scalar(
        select(func.count())
        .select_from(AnalysisRun)
        .where(AnalysisRun.tenant_id == principal.tenant_id)
    )
    avg_latency = await db.scalar(
        select(func.avg(AnalysisRun.latency_ms)).where(
            AnalysisRun.tenant_id == principal.tenant_id
        )
    )
    return {
        "environment": settings.environment,
        "inference_tier_configured": bool(settings.inference_base_url),
        "huggingface_token_configured": bool(settings.hf_token),
        "otel_endpoint": settings.otel_exporter_otlp_endpoint or None,
        "sentry_configured": bool(settings.sentry_dsn),
        "tenant_id": str(principal.tenant_id),
        "inference_jobs_completed": jobs_completed or 0,
        "analysis_runs": analyses or 0,
        "avg_analysis_latency_ms": round(float(avg_latency or 0), 1),
    }
