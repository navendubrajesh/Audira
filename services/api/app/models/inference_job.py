"""Inference job persistence."""

import uuid
from datetime import UTC, datetime

from sqlalchemy import JSON, Float, Integer, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class InferenceJob(Base):
    __tablename__ = "inference_jobs"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False, index=True)
    user_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False, index=True)
    batch_id: Mapped[uuid.UUID | None] = mapped_column(Uuid, nullable=True, index=True)
    modality: Mapped[str] = mapped_column(String(32), nullable=False)
    model_id: Mapped[str] = mapped_column(String(128), nullable=False, default="tribe-v2-stub")
    payload: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    payload_hash: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="queued", index=True)
    result: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    error: Mapped[str | None] = mapped_column(String(512), nullable=True)
    latency_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)
    sla_met: Mapped[bool | None] = mapped_column(nullable=True)
    cost_usd: Mapped[float | None] = mapped_column(Float, nullable=True)
    provider: Mapped[str | None] = mapped_column(String(64), nullable=True)
    cached_from_job_id: Mapped[uuid.UUID | None] = mapped_column(Uuid, nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(UTC))
    started_at: Mapped[datetime | None] = mapped_column(nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(nullable=True)


class InferenceBatch(Base):
    __tablename__ = "inference_batches"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False, index=True)
    user_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    total_jobs: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    completed_jobs: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    failed_jobs: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="queued")
    created_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(UTC))
    completed_at: Mapped[datetime | None] = mapped_column(nullable=True)
