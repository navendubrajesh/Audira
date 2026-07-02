"""Arq background worker — inference jobs on decoupled GPU tier."""

from arq.connections import RedisSettings

from worker.job_processor import process_inference_job
from worker.settings import settings


async def ping(ctx: dict) -> str:
    return "pong"


async def run_inference_job(ctx: dict, job_id: str) -> dict:
    return await process_inference_job(job_id)


async def on_startup(ctx: dict) -> None:
    if settings.hf_token:
        from audira_core.huggingface import apply_hf_token_env

        apply_hf_token_env(settings.hf_token)


class WorkerSettings:
    functions = [ping, run_inference_job]
    on_startup = on_startup
    redis_settings = RedisSettings.from_dsn(settings.redis_url)
    max_jobs = settings.worker_max_jobs
