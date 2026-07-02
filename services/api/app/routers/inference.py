"""Inference API — submit, poll, batch, metrics."""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import get_current_user, require_permission
from app.auth.principal import Principal
from app.db.session import get_db
from app.models.inference_job import InferenceBatch, InferenceJob
from app.services.inference_service import (
    CostCapExceededError,
    create_batch,
    create_job,
    get_batch,
    get_job,
    tenant_monthly_spend,
)
from app.services.job_queue import enqueue_batch_jobs, enqueue_inference_job

import sys
from pathlib import Path

SHARED = Path(__file__).resolve().parents[3] / "shared"
if str(SHARED) not in sys.path:
    sys.path.insert(0, str(SHARED))

from audira_core.inference.types import Modality
from audira_core.sla import sla_target_ms

router = APIRouter(prefix="/inference", tags=["inference"])


class SubmitJobRequest(BaseModel):
    modality: Modality = Modality.TEXT
    payload: dict = Field(default_factory=dict)
    model_id: str = "tribe-v2-stub"


class JobResponse(BaseModel):
    id: str
    status: str
    modality: str
    model_id: str
    batch_id: str | None
    latency_ms: int | None
    sla_met: bool | None
    sla_target_ms: int
    cost_usd: float | None
    provider: str | None
    cached: bool
    result: dict | None
    error: str | None
    poll_url: str


class SubmitBatchRequest(BaseModel):
    modality: Modality = Modality.TEXT
    items: list[dict] = Field(..., min_length=1, max_length=100)
    model_id: str = "tribe-v2-stub"


class BatchResponse(BaseModel):
    id: str
    status: str
    total_jobs: int
    completed_jobs: int
    failed_jobs: int
    job_ids: list[str]


class MetricsResponse(BaseModel):
    tenant_id: str
    monthly_spend_usd: float
    monthly_cap_usd: float
    jobs_completed: int
    jobs_sla_breach: int
    p95_latency_ms: int | None


def _job_response(job: InferenceJob) -> JobResponse:
    modality = Modality(job.modality)
    return JobResponse(
        id=str(job.id),
        status=job.status,
        modality=job.modality,
        model_id=job.model_id,
        batch_id=str(job.batch_id) if job.batch_id else None,
        latency_ms=job.latency_ms,
        sla_met=job.sla_met,
        sla_target_ms=sla_target_ms(modality),
        cost_usd=job.cost_usd,
        provider=job.provider,
        cached=job.status == "cached",
        result=job.result,
        error=job.error,
        poll_url=f"/inference/jobs/{job.id}",
    )


@router.post("/jobs", response_model=JobResponse, status_code=status.HTTP_202_ACCEPTED)
async def submit_job(
    body: SubmitJobRequest,
    principal: Annotated[Principal, Depends(require_permission("analyses.run"))],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> JobResponse:
    try:
        job = await create_job(
            db,
            tenant_id=principal.tenant_id,
            user_id=principal.user_id,
            modality=body.modality,
            payload=body.payload,
            model_id=body.model_id,
        )
    except CostCapExceededError as exc:
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail=(
                "Your organisation has reached its monthly inference budget. "
                "Contact your administrator to increase the limit."
            ),
        ) from exc

    if job.status == "queued":
        await enqueue_inference_job(job.id)

    return _job_response(job)


@router.get("/jobs/{job_id}", response_model=JobResponse)
async def poll_job(
    job_id: UUID,
    principal: Annotated[Principal, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> JobResponse:
    job = await get_job(db, job_id, principal.tenant_id)
    if not job:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")
    return _job_response(job)


@router.post("/batches", response_model=BatchResponse, status_code=status.HTTP_202_ACCEPTED)
async def submit_batch(
    body: SubmitBatchRequest,
    principal: Annotated[Principal, Depends(require_permission("analyses.run"))],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> BatchResponse:
    try:
        batch, jobs = await create_batch(
            db,
            tenant_id=principal.tenant_id,
            user_id=principal.user_id,
            items=body.items,
            modality=body.modality,
            model_id=body.model_id,
        )
    except CostCapExceededError as exc:
        raise HTTPException(status_code=status.HTTP_402_PAYMENT_REQUIRED, detail=str(exc)) from exc

    queued_ids = [j.id for j in jobs if j.status == "queued"]
    if queued_ids:
        await enqueue_batch_jobs(queued_ids)

    return BatchResponse(
        id=str(batch.id),
        status=batch.status,
        total_jobs=batch.total_jobs,
        completed_jobs=batch.completed_jobs,
        failed_jobs=batch.failed_jobs,
        job_ids=[str(j.id) for j in jobs],
    )


@router.get("/batches/{batch_id}", response_model=BatchResponse)
async def poll_batch(
    batch_id: UUID,
    principal: Annotated[Principal, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> BatchResponse:
    batch = await get_batch(db, batch_id, principal.tenant_id)
    if not batch:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Batch not found")

    jobs_result = await db.execute(
        select(InferenceJob).where(InferenceJob.batch_id == batch_id)
    )
    jobs = jobs_result.scalars().all()

    return BatchResponse(
        id=str(batch.id),
        status=batch.status,
        total_jobs=batch.total_jobs,
        completed_jobs=batch.completed_jobs,
        failed_jobs=batch.failed_jobs,
        job_ids=[str(j.id) for j in jobs],
    )


@router.get("/metrics", response_model=MetricsResponse)
async def inference_metrics(
    principal: Annotated[Principal, Depends(require_permission("audit.view"))],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> MetricsResponse:
    from app.config import settings

    spend = await tenant_monthly_spend(db, principal.tenant_id)

    completed_stmt = select(func.count()).where(
        InferenceJob.tenant_id == principal.tenant_id,
        InferenceJob.status.in_(["completed", "cached"]),
    )
    completed = (await db.execute(completed_stmt)).scalar_one()

    breach_stmt = select(func.count()).where(
        InferenceJob.tenant_id == principal.tenant_id,
        InferenceJob.sla_met.is_(False),
    )
    breaches = (await db.execute(breach_stmt)).scalar_one()

    latencies = await db.execute(
        select(InferenceJob.latency_ms)
        .where(
            InferenceJob.tenant_id == principal.tenant_id,
            InferenceJob.latency_ms.isnot(None),
        )
        .order_by(InferenceJob.latency_ms)
    )
    values = [r for r in latencies.scalars().all() if r is not None]
    p95 = None
    if values:
        idx = min(len(values) - 1, int(len(values) * 0.95))
        p95 = values[idx]

    return MetricsResponse(
        tenant_id=str(principal.tenant_id),
        monthly_spend_usd=spend,
        monthly_cap_usd=settings.inference_monthly_cost_cap_usd,
        jobs_completed=completed,
        jobs_sla_breach=breaches,
        p95_latency_ms=p95,
    )
