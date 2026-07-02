"""Tenant residency and isolation API."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import get_current_user, require_permission
from app.auth.principal import Principal
from app.db.session import get_db
from app.residency.regions import DataRegion
from app.services.audit import record_audit
from app.services.tenant_service import (
    TenantIsolationError,
    assert_tenant_resource,
    ensure_default_tenant,
    get_tenant,
    residency_view,
    update_tenant_residency,
)

router = APIRouter(prefix="/tenant", tags=["tenant"])


class ResidencyResponse(BaseModel):
    tenant_id: str
    tenant_name: str
    storage_region: str
    storage_region_label: str
    storage_cloud_region: str
    processing_region: str
    processing_region_label: str
    processing_cloud_region: str
    encryption_at_rest: str
    tls_min_version: str
    encryption_key_id: str | None
    tenant_isolation: bool


class UpdateResidencyRequest(BaseModel):
    storage_region: DataRegion | None = None
    processing_region: DataRegion | None = None
    encryption_key_id: str | None = Field(default=None, max_length=512)


class IsolationVerifyResponse(BaseModel):
    status: str
    tenant_id: str
    cross_tenant_access_blocked: bool


@router.get("/residency", response_model=ResidencyResponse)
async def get_residency(
    principal: Annotated[Principal, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> ResidencyResponse:
    tenant = await get_tenant(db, principal.tenant_id)
    if not tenant:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tenant not found")
    return ResidencyResponse(**residency_view(tenant))


@router.patch("/residency", response_model=ResidencyResponse)
async def patch_residency(
    body: UpdateResidencyRequest,
    principal: Annotated[Principal, Depends(require_permission("users.manage"))],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> ResidencyResponse:
    tenant = await update_tenant_residency(
        db,
        principal.tenant_id,
        storage_region=body.storage_region,
        processing_region=body.processing_region,
        encryption_key_id=body.encryption_key_id,
    )
    await record_audit(
        db,
        tenant_id=principal.tenant_id,
        action="tenant.residency_updated",
        actor_user_id=principal.user_id,
        actor_email=principal.email,
        metadata={
            "storage_region": tenant.storage_region,
            "processing_region": tenant.processing_region,
        },
    )
    return ResidencyResponse(**residency_view(tenant))


@router.get("/residency/verify", response_model=IsolationVerifyResponse)
async def verify_isolation(
    principal: Annotated[Principal, Depends(require_permission("audit.view"))],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> IsolationVerifyResponse:
    """Self-check that tenant isolation enforcement is active."""
    tenant = await ensure_default_tenant(db)
    blocked = False
    try:
        import uuid

        other = uuid.UUID("00000000-0000-4000-8000-000000000099")
        assert_tenant_resource(other, principal.tenant_id)
    except TenantIsolationError:
        blocked = True

    return IsolationVerifyResponse(
        status="ok",
        tenant_id=str(tenant.id),
        cross_tenant_access_blocked=blocked,
    )
