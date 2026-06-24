"""Audience library API (TCA-001)."""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import get_current_user, require_permission
from app.auth.principal import Principal
from app.db.session import get_db
from app.models.audience import Audience
from app.services.seed_defaults import seed_tenant_defaults
from app.services.tenant_service import assert_tenant_resource, TenantIsolationError

router = APIRouter(prefix="/audiences", tags=["audiences"])


class AudienceBody(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    role: str | None = None
    region: str | None = None
    language: str | None = "en"
    seniority: str | None = None
    attributes: dict = Field(default_factory=dict)
    is_default: bool = False


class AudienceResponse(BaseModel):
    id: str
    name: str
    role: str | None
    region: str | None
    language: str | None
    seniority: str | None
    attributes: dict
    is_default: bool


def _to_response(a: Audience) -> AudienceResponse:
    return AudienceResponse(
        id=str(a.id),
        name=a.name,
        role=a.role,
        region=a.region,
        language=a.language,
        seniority=a.seniority,
        attributes=a.attributes,
        is_default=a.is_default,
    )


@router.get("", response_model=list[AudienceResponse])
async def list_audiences(
    principal: Annotated[Principal, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    await seed_tenant_defaults(db, principal.tenant_id)
    result = await db.execute(
        select(Audience).where(Audience.tenant_id == principal.tenant_id).order_by(Audience.name)
    )
    return [_to_response(a) for a in result.scalars().all()]


@router.post("", response_model=AudienceResponse, status_code=status.HTTP_201_CREATED)
async def create_audience(
    body: AudienceBody,
    principal: Annotated[Principal, Depends(require_permission("audiences.manage"))],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    audience = Audience(tenant_id=principal.tenant_id, **body.model_dump())
    db.add(audience)
    await db.commit()
    await db.refresh(audience)
    return _to_response(audience)


@router.patch("/{audience_id}", response_model=AudienceResponse)
async def update_audience(
    audience_id: UUID,
    body: AudienceBody,
    principal: Annotated[Principal, Depends(require_permission("audiences.manage"))],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    audience = await db.get(Audience, audience_id)
    if not audience:
        raise HTTPException(status_code=404, detail="Audience not found")
    try:
        assert_tenant_resource(audience.tenant_id, principal.tenant_id)
    except TenantIsolationError:
        raise HTTPException(status_code=404, detail="Audience not found") from None
    for key, value in body.model_dump().items():
        setattr(audience, key, value)
    await db.commit()
    await db.refresh(audience)
    return _to_response(audience)


@router.delete("/{audience_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_audience(
    audience_id: UUID,
    principal: Annotated[Principal, Depends(require_permission("audiences.manage"))],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    audience = await db.get(Audience, audience_id)
    if not audience:
        raise HTTPException(status_code=404, detail="Audience not found")
    try:
        assert_tenant_resource(audience.tenant_id, principal.tenant_id)
    except TenantIsolationError:
        raise HTTPException(status_code=404, detail="Audience not found") from None
    await db.delete(audience)
    await db.commit()
