"""Tenant registry — residency and isolation."""

import uuid
from datetime import UTC, datetime

from sqlalchemy import String, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.residency.regions import ENCRYPTION_AT_REST, TLS_MIN_VERSION, DataRegion


class Tenant(Base):
    __tablename__ = "tenants"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    storage_region: Mapped[str] = mapped_column(String(8), nullable=False, default=DataRegion.IN.value)
    processing_region: Mapped[str] = mapped_column(String(8), nullable=False, default=DataRegion.IN.value)
    encryption_at_rest: Mapped[str] = mapped_column(String(32), nullable=False, default=ENCRYPTION_AT_REST)
    tls_min_version: Mapped[str] = mapped_column(String(8), nullable=False, default=TLS_MIN_VERSION)
    encryption_key_id: Mapped[str | None] = mapped_column(String(512), nullable=True)
    is_active: Mapped[bool] = mapped_column(default=True)
    created_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(UTC))
    updated_at: Mapped[datetime] = mapped_column(
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
    )
