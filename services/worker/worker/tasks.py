"""Arq background worker — inference jobs on decoupled GPU tier."""

from arq.connections import RedisSettings

from worker.job_processor import process_inference_job
from worker.settings import settings


async def ping(ctx: dict) -> str:
    return "pong"


async def run_inference_job(ctx: dict, job_id: str) -> dict:
    return await process_inference_job(job_id)


class WorkerSettings:
    functions = [ping, run_inference_job]
    redis_settings = RedisSettings.from_dsn(settings.redis_url)
    max_jobs = settings.worker_max_jobs
