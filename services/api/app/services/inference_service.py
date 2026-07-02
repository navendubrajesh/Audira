"""Inference job orchestration."""

import hashlib
import json
import sys
import uuid
from datetime import UTC, datetime
from pathlib import Path
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.models.inference_job import InferenceBatch, InferenceJob

# Shared core on PYTHONPATH (see Dockerfiles / conftest)
SHARED = Path(__file__).resolve().parents[3] / "shared"
if str(SHARED) not in sys.path:
    sys.path.insert(0, str(SHARED))

from audira_core.cost import estimate_cost, would_exceed_cap
from audira_core.inference.types import JobStatus, Modality


def payload_hash(payload: dict, modality: str, model_id: str) -> str:
    canonical = json.dumps(
        {"modality": modality, "model_id": model_id, "payload": payload},
        sort_keys=True,
    )
    return hashlib.sha256(canonical.encode()).hexdigest()


async def tenant_monthly_spend(db: AsyncSession, tenant_id: UUID) -> float:
    now = datetime.now(UTC)
    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    stmt = select(func.coalesce(func.sum(InferenceJob.cost_usd), 0.0)).where(
        InferenceJob.tenant_id == tenant_id,
        InferenceJob.status.in_(["completed", "cached"]),
        InferenceJob.completed_at >= month_start,
    )
    result = await db.execute(stmt)
    return float(result.scalar_one())


async def find_cached_job(
    db: AsyncSession, tenant_id: UUID, phash: str
) -> InferenceJob | None:
    stmt = (
        select(InferenceJob)
        .where(
            InferenceJob.tenant_id == tenant_id,
            InferenceJob.payload_hash == phash,
            InferenceJob.status.in_(["completed", "cached"]),
        )
        .order_by(InferenceJob.completed_at.desc())
        .limit(1)
    )
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def create_job(
    db: AsyncSession,
    *,
    tenant_id: UUID,
    user_id: UUID,
    modality: Modality,
    payload: dict,
    model_id: str = "tribe-v2-stub",
    batch_id: UUID | None = None,
) -> InferenceJob:
    phash = payload_hash(payload, modality.value, model_id)

    spend = await tenant_monthly_spend(db, tenant_id)
    est = estimate_cost(modality)
    if would_exceed_cap(spend, est, settings.inference_monthly_cost_cap_usd):
        raise CostCapExceededError(spend, settings.inference_monthly_cost_cap_usd)

    cached = await find_cached_job(db, tenant_id, phash)
    if cached:
        job = InferenceJob(
            tenant_id=tenant_id,
            user_id=user_id,
            batch_id=batch_id,
            modality=modality.value,
            model_id=model_id,
            payload=payload,
            payload_hash=phash,
            status=JobStatus.CACHED.value,
            result=cached.result,
            latency_ms=0,
            sla_met=True,
            cost_usd=0.0,
            provider=cached.provider,
            cached_from_job_id=cached.id,
            completed_at=datetime.now(UTC),
        )
        db.add(job)
        await db.commit()
        await db.refresh(job)
        return job

    job = InferenceJob(
        tenant_id=tenant_id,
        user_id=user_id,
        batch_id=batch_id,
        modality=modality.value,
        model_id=model_id,
        payload=payload,
        payload_hash=phash,
        status=JobStatus.QUEUED.value,
    )
    db.add(job)
    await db.commit()
    await db.refresh(job)
    return job


async def create_batch(
    db: AsyncSession,
    *,
    tenant_id: UUID,
    user_id: UUID,
    items: list[dict],
    modality: Modality,
    model_id: str = "tribe-v2-stub",
) -> tuple[InferenceBatch, list[InferenceJob]]:
    batch = InferenceBatch(
        tenant_id=tenant_id,
        user_id=user_id,
        total_jobs=len(items),
        status="queued",
    )
    db.add(batch)
    await db.flush()

    jobs: list[InferenceJob] = []
    for item in items:
        job = await create_job(
            db,
            tenant_id=tenant_id,
            user_id=user_id,
            modality=modality,
            payload=item,
            model_id=model_id,
            batch_id=batch.id,
        )
        jobs.append(job)

    batch.status = "running" if any(j.status == JobStatus.QUEUED.value for j in jobs) else "completed"
    await db.commit()
    await db.refresh(batch)
    return batch, jobs


async def get_job(db: AsyncSession, job_id: UUID, tenant_id: UUID) -> InferenceJob | None:
    result = await db.execute(
        select(InferenceJob).where(InferenceJob.id == job_id, InferenceJob.tenant_id == tenant_id)
    )
    return result.scalar_one_or_none()


async def get_batch(db: AsyncSession, batch_id: UUID, tenant_id: UUID) -> InferenceBatch | None:
    result = await db.execute(
        select(InferenceBatch).where(
            InferenceBatch.id == batch_id, InferenceBatch.tenant_id == tenant_id
        )
    )
    return result.scalar_one_or_none()


class CostCapExceededError(Exception):
    def __init__(self, current_spend: float, cap: float) -> None:
        self.current_spend = current_spend
        self.cap = cap
        super().__init__(f"Monthly inference cost cap exceeded ({current_spend:.4f} / {cap:.2f} USD)")
