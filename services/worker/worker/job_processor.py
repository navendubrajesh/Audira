"""Process inference jobs — Arq worker entrypoint."""

import sys
import uuid
from pathlib import Path

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import JSON, Float, Integer, String, Uuid
import uuid as uuid_mod
from datetime import datetime

SHARED = Path(__file__).resolve().parents[2] / "shared"
if str(SHARED) not in sys.path:
    sys.path.insert(0, str(SHARED))

from audira_core.process_job import execute_inference_job
from worker.settings import settings


class Base(DeclarativeBase):
    pass


class InferenceJob(Base):
    __tablename__ = "inference_jobs"

    id: Mapped[uuid_mod.UUID] = mapped_column(Uuid, primary_key=True)
    batch_id: Mapped[uuid_mod.UUID | None] = mapped_column(Uuid, nullable=True)
    modality: Mapped[str] = mapped_column(String(32), nullable=False)
    model_id: Mapped[str] = mapped_column(String(128), nullable=False)
    payload: Mapped[dict] = mapped_column(JSON, nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    result: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    error: Mapped[str | None] = mapped_column(String(512), nullable=True)
    latency_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)
    sla_met: Mapped[bool | None] = mapped_column(nullable=True)
    cost_usd: Mapped[float | None] = mapped_column(Float, nullable=True)
    provider: Mapped[str | None] = mapped_column(String(64), nullable=True)
    started_at: Mapped[datetime | None] = mapped_column(nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(nullable=True)


class InferenceBatch(Base):
    __tablename__ = "inference_batches"

    id: Mapped[uuid_mod.UUID] = mapped_column(Uuid, primary_key=True)
    total_jobs: Mapped[int] = mapped_column(Integer, nullable=False)
    completed_jobs: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    failed_jobs: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    completed_at: Mapped[datetime | None] = mapped_column(nullable=True)


async def process_inference_job(job_id: str) -> dict:
    engine = create_async_engine(settings.database_url)
    session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    try:
        async with session_factory() as session:
            return await execute_inference_job(
                session,
                InferenceJob,
                InferenceBatch,
                uuid.UUID(job_id),
                inference_base_url=settings.inference_base_url,
                inference_api_key=settings.inference_api_key,
            )
    finally:
        await engine.dispose()
