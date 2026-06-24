"""Run inference job against DB session — shared by API tests and Arq worker."""

import uuid
from datetime import UTC, datetime

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from resonode_core.inference.factory import build_provider
from resonode_core.inference.types import InferenceRequest, Modality
from resonode_core.sla import check_sla


async def refresh_batch_counts(session: AsyncSession, batch_model, job_model, batch_id: uuid.UUID) -> None:
    completed = await session.scalar(
        select(func.count())
        .select_from(job_model)
        .where(job_model.batch_id == batch_id, job_model.status.in_(["completed", "cached"]))
    )
    failed = await session.scalar(
        select(func.count())
        .select_from(job_model)
        .where(job_model.batch_id == batch_id, job_model.status == "failed")
    )
    batch = await session.get(batch_model, batch_id)
    if not batch:
        return
    batch.completed_jobs = completed or 0
    batch.failed_jobs = failed or 0
    if batch.completed_jobs + batch.failed_jobs >= batch.total_jobs:
        batch.status = "failed" if batch.failed_jobs == batch.total_jobs else "completed"
        batch.completed_at = datetime.now(UTC)
    session.add(batch)


async def execute_inference_job(
    session: AsyncSession,
    job_model,
    batch_model,
    job_id: uuid.UUID,
    *,
    inference_base_url: str = "",
    inference_api_key: str = "",
) -> dict:
    job = await session.get(job_model, job_id)
    if not job or job.status not in ("queued",):
        return {"skipped": True, "job_id": str(job_id)}

    provider = build_provider(
        model_id=job.model_id,
        inference_base_url=inference_base_url,
        inference_api_key=inference_api_key,
    )
    job.status = "running"
    job.started_at = datetime.now(UTC)
    await session.commit()

    try:
        result = await provider.run(
            InferenceRequest(
                modality=Modality(job.modality),
                payload=job.payload,
                model_id=job.model_id,
            )
        )
        job.status = "completed"
        job.result = result.output
        job.latency_ms = result.latency_ms
        job.sla_met = check_sla(Modality(job.modality), result.latency_ms)
        job.cost_usd = result.cost_usd
        job.provider = result.provider
        job.completed_at = datetime.now(UTC)
    except Exception as exc:
        job.status = "failed"
        job.error = str(exc)[:500]
        job.completed_at = datetime.now(UTC)

    await session.commit()

    if job.batch_id and batch_model is not None:
        await refresh_batch_counts(session, batch_model, job_model, job.batch_id)
        await session.commit()

    return {"job_id": str(job_id), "status": job.status}
