"""Seed default audiences, artifact types, brand, governance (TCA-001, TCA-004, TCA-016)."""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.audience import Audience
from app.models.context import ArtifactType, BrandProfile, StandardsRule
from app.models.governance import (
    ModelRegistryEntry,
    TenantGuardrailSettings,
    TenantPrivacySettings,
    TenantQualityGates,
    ValidationMetric,
)

DEFAULT_AUDIENCES = [
    {
        "name": "All employees",
        "role": "employee",
        "region": "Global",
        "language": "en",
        "seniority": "all",
        "is_default": True,
    },
    {
        "name": "Leadership",
        "role": "executive",
        "region": "Global",
        "language": "en",
        "seniority": "executive",
    },
    {
        "name": "External clients",
        "role": "client",
        "region": "Global",
        "language": "en",
        "seniority": "external",
    },
    {
        "name": "Press & media",
        "role": "press",
        "region": "Global",
        "language": "en",
        "seniority": "external",
    },
    {
        "name": "Regulators",
        "role": "regulator",
        "region": "EU",
        "language": "en",
        "seniority": "external",
    },
]

DEFAULT_ARTIFACT_TYPES = [
    {
        "code": "email",
        "label": "Email / memo",
        "checks": ["readability", "tone", "brand", "inclusive", "structure"],
        "block_engineering": False,
    },
    {
        "code": "intranet",
        "label": "Intranet article",
        "checks": ["readability", "jargon", "inclusive", "engagement", "structure"],
        "block_engineering": False,
    },
    {
        "code": "town_hall",
        "label": "Town hall script",
        "checks": ["tone", "engagement", "clarity"],
        "block_engineering": False,
    },
    {
        "code": "press_release",
        "label": "Press release",
        "checks": ["brand", "clarity", "trust"],
        "block_engineering": False,
    },
    {
        "code": "policy",
        "label": "Policy notice",
        "checks": ["readability", "inclusive", "trust"],
        "block_engineering": False,
    },
    {
        "code": "engineering_spec",
        "label": "Engineering specification",
        "checks": [],
        "block_engineering": True,
    },
]

DEFAULT_BRAND = {
    "voice_attributes": {"formality": "professional", "warmth": "moderate"},
    "terminology_do": ["customers", "team members", "our organisation"],
    "terminology_dont": ["guys", "resource" ],
    "messaging_pillars": ["trust", "innovation", "people first"],
    "target_tone": "professional",
}

MODEL_REGISTRY = [
    {
        "model_id": "facebook/tribev2",
        "version": "1.0.0",
        "licence": "CC-BY-NC-4.0",
        "commercial_ok": False,
        "modalities": ["text", "image", "video"],
        "legal_signoff": None,
        "changelog": [{"version": "1.0.0", "note": "Initial TRIBE v2 registration"}],
    },
    {
        "model_id": "tribe-v2-stub",
        "version": "1.0.0",
        "licence": "internal-dev",
        "commercial_ok": True,
        "modalities": ["text"],
        "legal_signoff": "dev-only",
        "changelog": [{"version": "1.0.0", "note": "Development stub provider"}],
    },
]

VALIDATION_METRICS = [
    {"metric_name": "engagement", "accuracy": 0.78, "sample_size": 120},
    {"metric_name": "clarity", "accuracy": 0.81, "sample_size": 120},
    {"metric_name": "trust", "accuracy": 0.74, "sample_size": 95},
]

DEFAULT_STANDARDS = [
    {
        "rule_type": "inclusive",
        "pattern": "guys",
        "replacement": "team / everyone",
        "status": "published",
    },
    {
        "rule_type": "inclusive",
        "pattern": "blacklist",
        "replacement": "blocklist",
        "status": "published",
    },
    {
        "rule_type": "jargon",
        "pattern": "synergize",
        "replacement": "work together",
        "status": "published",
    },
    {
        "rule_type": "jargon",
        "pattern": "leverage",
        "replacement": "use",
        "status": "published",
    },
]


async def seed_tenant_defaults(db: AsyncSession, tenant_id: UUID) -> None:
    existing_audience = await db.scalar(
        select(Audience.id).where(Audience.tenant_id == tenant_id).limit(1)
    )
    if not existing_audience:
        for row in DEFAULT_AUDIENCES:
            db.add(Audience(tenant_id=tenant_id, attributes={}, **row))

        for row in DEFAULT_ARTIFACT_TYPES:
            db.add(ArtifactType(tenant_id=tenant_id, is_active=True, **row))

        db.add(BrandProfile(tenant_id=tenant_id, status="published", **DEFAULT_BRAND))

    privacy = await db.get(TenantPrivacySettings, tenant_id)
    if not privacy:
        db.add(TenantPrivacySettings(tenant_id=tenant_id))

    if not await db.get(TenantGuardrailSettings, tenant_id):
        db.add(TenantGuardrailSettings(tenant_id=tenant_id))

    if not await db.get(TenantQualityGates, tenant_id):
        db.add(TenantQualityGates(tenant_id=tenant_id))

    for row in DEFAULT_STANDARDS:
        exists = await db.scalar(
            select(StandardsRule.id).where(
                StandardsRule.tenant_id == tenant_id,
                StandardsRule.pattern == row["pattern"],
            )
        )
        if not exists:
            db.add(StandardsRule(tenant_id=tenant_id, **row))

    for row in MODEL_REGISTRY:
        exists = await db.scalar(
            select(ModelRegistryEntry.id).where(ModelRegistryEntry.model_id == row["model_id"])
        )
        if not exists:
            db.add(ModelRegistryEntry(status="active", **row))

    for row in VALIDATION_METRICS:
        exists = await db.scalar(
            select(ValidationMetric.id).where(ValidationMetric.metric_name == row["metric_name"])
        )
        if not exists:
            db.add(ValidationMetric(**row))

    await db.commit()


async def seed_global_governance(db: AsyncSession) -> None:
    for row in MODEL_REGISTRY:
        exists = await db.scalar(
            select(ModelRegistryEntry.id).where(ModelRegistryEntry.model_id == row["model_id"])
        )
        if not exists:
            db.add(ModelRegistryEntry(status="active", **row))
    for row in VALIDATION_METRICS:
        exists = await db.scalar(
            select(ValidationMetric.id).where(ValidationMetric.metric_name == row["metric_name"])
        )
        if not exists:
            db.add(ValidationMetric(**row))
    await db.commit()
