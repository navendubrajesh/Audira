"""Enqueue inference jobs to Arq worker."""

import sys
from pathlib import Path
from uuid import UUID

from arq import create_pool
from arq.connections import RedisSettings

from app.config import settings

SHARED = Path(__file__).resolve().parents[3] / "shared"
if str(SHARED) not in sys.path:
    sys.path.insert(0, str(SHARED))


async def enqueue_inference_job(job_id: UUID) -> None:
    redis = await create_pool(RedisSettings.from_dsn(settings.redis_url))
    try:
        await redis.enqueue_job("run_inference_job", str(job_id))
    finally:
        await redis.aclose()


async def enqueue_batch_jobs(job_ids: list[UUID]) -> None:
    redis = await create_pool(RedisSettings.from_dsn(settings.redis_url))
    try:
        for job_id in job_ids:
            if job_id:
                await redis.enqueue_job("run_inference_job", str(job_id))
    finally:
        await redis.aclose()
