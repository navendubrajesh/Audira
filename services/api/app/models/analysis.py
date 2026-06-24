"""Analysis runs and scores (TCA-008, TCA-019, TCA-038, etc.)."""

import uuid
from datetime import UTC, datetime

from sqlalchemy import JSON, Float, Integer, String, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class AnalysisRun(Base):
    __tablename__ = "analysis_runs"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False, index=True)
    user_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    audience_id: Mapped[uuid.UUID | None] = mapped_column(Uuid, nullable=True)
    artifact_type_code: Mapped[str | None] = mapped_column(String(64), nullable=True)
    objective: Mapped[str | None] = mapped_column(String(64), nullable=True)
    channel: Mapped[str | None] = mapped_column(String(64), nullable=True)
    input_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    input_hash: Mapped[str | None] = mapped_column(String(64), nullable=True)
    status: Mapped[str] = mapped_column(String(32), default="completed")
    model_id: Mapped[str] = mapped_column(String(128), default="facebook/tribev2")
    model_version: Mapped[str] = mapped_column(String(64), default="1.0.0")
    mapping_version: Mapped[str] = mapped_column(String(64), default="1.0.0")
    composite_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    result: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    latency_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(UTC))


class ArtifactUpload(Base):
    __tablename__ = "artifact_uploads"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False, index=True)
    filename: Mapped[str] = mapped_column(String(512), nullable=False)
    content_type: Mapped[str] = mapped_column(String(128), nullable=False)
    storage_key: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    parsed: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    is_engineering: Mapped[bool] = mapped_column(default=False)
    created_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(UTC))
