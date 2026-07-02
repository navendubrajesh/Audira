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


class TenantGuardrailSettings(Base):
    """TCA-037 / TCA-044 / TCA-060 — per-tenant guardrail toggles."""

    __tablename__ = "tenant_guardrail_settings"

    tenant_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True)
    generative_governance: Mapped[bool] = mapped_column(default=False)
    rewrite_assist: Mapped[bool] = mapped_column(default=False)
    regulated_claims: Mapped[bool] = mapped_column(default=False)
    block_on_fail: Mapped[bool] = mapped_column(default=False)


class TenantQualityGates(Base):
    """TCA-052 — configurable quality thresholds."""

    __tablename__ = "tenant_quality_gates"

    tenant_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True)
    pass_threshold: Mapped[float] = mapped_column(Float, default=70.0)
    needs_work_threshold: Mapped[float] = mapped_column(Float, default=55.0)
    block_publish_on_fail: Mapped[bool] = mapped_column(default=False)


class ApiKey(Base):
    """TCA-050 — API keys for embeddable SDK access."""

    __tablename__ = "api_keys"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    key_prefix: Mapped[str] = mapped_column(String(16), nullable=False)
    key_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    rate_limit_per_minute: Mapped[int] = mapped_column(default=60)
    is_active: Mapped[bool] = mapped_column(default=True)
    created_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(UTC))


