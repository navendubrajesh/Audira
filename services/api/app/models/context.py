"""E01 context models — artifact types, standards, brand (TCA-004, TCA-005, TCA-002)."""

import uuid
from datetime import UTC, datetime

from sqlalchemy import JSON, String, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class ArtifactType(Base):
    __tablename__ = "artifact_types"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False, index=True)
    code: Mapped[str] = mapped_column(String(64), nullable=False)
    label: Mapped[str] = mapped_column(String(255), nullable=False)
    checks: Mapped[list] = mapped_column(JSON, nullable=False, default=list)
    block_engineering: Mapped[bool] = mapped_column(default=False)
    is_active: Mapped[bool] = mapped_column(default=True)


class StandardsRule(Base):
    __tablename__ = "standards_rules"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False, index=True)
    version: Mapped[int] = mapped_column(default=1)
    status: Mapped[str] = mapped_column(String(32), default="draft")  # draft | published
    artifact_type_code: Mapped[str | None] = mapped_column(String(64), nullable=True)
    rule_type: Mapped[str] = mapped_column(String(64), nullable=False)
    pattern: Mapped[str] = mapped_column(String(512), nullable=False)
    replacement: Mapped[str | None] = mapped_column(String(512), nullable=True)
    metadata_: Mapped[dict] = mapped_column("metadata", JSON, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(UTC))


class BrandProfile(Base):
    __tablename__ = "brand_profiles"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False, index=True)
    version: Mapped[int] = mapped_column(default=1)
    status: Mapped[str] = mapped_column(String(32), default="published")
    voice_attributes: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    terminology_do: Mapped[list] = mapped_column(JSON, nullable=False, default=list)
    terminology_dont: Mapped[list] = mapped_column(JSON, nullable=False, default=list)
    messaging_pillars: Mapped[list] = mapped_column(JSON, nullable=False, default=list)
    target_tone: Mapped[str] = mapped_column(String(64), default="professional")
    created_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(UTC))
