"""API-side inference job execution (tests + inline fallback)."""

import sys
from pathlib import Path
from uuid import UUID

from app.config import settings
from app.db.session import async_session_factory
from app.models.inference_job import InferenceBatch, InferenceJob

SHARED = Path(__file__).resolve().parents[3] / "shared"
if str(SHARED) not in sys.path:
    sys.path.insert(0, str(SHARED))

from audira_core.process_job import execute_inference_job


async def run_inference_job_by_id(job_id: UUID) -> dict:
    async with async_session_factory() as session:
        return await execute_inference_job(
            session,
            InferenceJob,
            InferenceBatch,
            job_id,
            inference_base_url=settings.inference_base_url,
            inference_api_key=settings.inference_api_key,
        )
