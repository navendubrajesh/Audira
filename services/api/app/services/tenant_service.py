"""Tenant isolation and residency helpers."""

from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.tenant import Tenant
from app.residency.regions import (
    ENCRYPTION_AT_REST,
    PROCESSING_REGION_ENDPOINTS,
    REGION_LABELS,
    STORAGE_REGION_ENDPOINTS,
    TLS_MIN_VERSION,
    DataRegion,
)
from app.tenants import DEFAULT_TENANT_ID


class TenantIsolationError(Exception):
    pass


def assert_tenant_resource(resource_tenant_id: UUID, principal_tenant_id: UUID) -> None:
    if resource_tenant_id != principal_tenant_id:
        raise TenantIsolationError(
            "Access denied — resource belongs to another organisation."
        )


async def get_tenant(db: AsyncSession, tenant_id: UUID) -> Tenant | None:
    result = await db.execute(select(Tenant).where(Tenant.id == tenant_id))
    return result.scalar_one_or_none()


async def ensure_default_tenant(db: AsyncSession) -> Tenant:
    tenant = await get_tenant(db, DEFAULT_TENANT_ID)
    if tenant:
        return tenant
    tenant = Tenant(
        id=DEFAULT_TENANT_ID,
        name="Pilot Organisation",
        storage_region=DataRegion.IN.value,
        processing_region=DataRegion.IN.value,
        encryption_key_id="local-dev-key",
    )
    db.add(tenant)
    await db.commit()
    await db.refresh(tenant)
    return tenant


def residency_view(tenant: Tenant) -> dict:
    storage = DataRegion(tenant.storage_region)
    processing = DataRegion(tenant.processing_region)
    return {
        "tenant_id": str(tenant.id),
        "tenant_name": tenant.name,
        "storage_region": storage.value,
        "storage_region_label": REGION_LABELS[storage],
        "storage_cloud_region": STORAGE_REGION_ENDPOINTS[storage],
        "processing_region": processing.value,
        "processing_region_label": REGION_LABELS[processing],
        "processing_cloud_region": PROCESSING_REGION_ENDPOINTS[processing],
        "encryption_at_rest": tenant.encryption_at_rest or ENCRYPTION_AT_REST,
        "tls_min_version": tenant.tls_min_version or TLS_MIN_VERSION,
        "encryption_key_id": tenant.encryption_key_id,
        "tenant_isolation": True,
    }


async def update_tenant_residency(
    db: AsyncSession,
    tenant_id: UUID,
    *,
    storage_region: DataRegion | None = None,
    processing_region: DataRegion | None = None,
    encryption_key_id: str | None = None,
) -> Tenant:
    tenant = await get_tenant(db, tenant_id)
    if not tenant:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tenant not found")
    if storage_region:
        tenant.storage_region = storage_region.value
    if processing_region:
        tenant.processing_region = processing_region.value
    if encryption_key_id is not None:
        tenant.encryption_key_id = encryption_key_id
    await db.commit()
    await db.refresh(tenant)
    return tenant
