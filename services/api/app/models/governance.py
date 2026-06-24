"""Model governance (TCA-016, TCA-019, TCA-063, TCA-070)."""

import uuid
from datetime import UTC, datetime

from sqlalchemy import JSON, Float, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class ModelRegistryEntry(Base):
    __tablename__ = "model_registry"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    model_id: Mapped[str] = mapped_column(String(128), unique=True, nullable=False)
    version: Mapped[str] = mapped_column(String(64), nullable=False)
    licence: Mapped[str] = mapped_column(String(128), nullable=False)
    commercial_ok: Mapped[bool] = mapped_column(default=False)
    status: Mapped[str] = mapped_column(String(32), default="active")
    modalities: Mapped[list] = mapped_column(JSON, nullable=False, default=list)
    legal_signoff: Mapped[str | None] = mapped_column(String(255), nullable=True)
    changelog: Mapped[list] = mapped_column(JSON, nullable=False, default=list)
    updated_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(UTC))


class ValidationMetric(Base):
    __tablename__ = "validation_metrics"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    metric_name: Mapped[str] = mapped_column(String(64), nullable=False)
    accuracy: Mapped[float] = mapped_column(Float, nullable=False)
    sample_size: Mapped[int] = mapped_column(default=0)
    methodology: Mapped[str] = mapped_column(String(512), default="held-out human agreement")
    updated_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(UTC))


class TenantPrivacySettings(Base):
    __tablename__ = "tenant_privacy_settings"

    tenant_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True)
    no_train: Mapped[bool] = mapped_column(default=True)
    zero_retention: Mapped[bool] = mapped_column(default=False)
    consent_basis: Mapped[str] = mapped_column(String(64), default="legitimate_interest")
    retention_days: Mapped[int] = mapped_column(default=90)
    pii_redaction: Mapped[bool] = mapped_column(default=False)
