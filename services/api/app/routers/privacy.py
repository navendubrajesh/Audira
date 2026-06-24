"""Privacy & data handling settings (TCA-061, TCA-070)."""

from typing import Annotated

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import get_current_user, require_roles
from app.auth.principal import Principal
from app.auth.roles import Role
from app.db.session import get_db
from app.models.governance import TenantPrivacySettings
from app.services.seed_defaults import seed_tenant_defaults

router = APIRouter(prefix="/privacy", tags=["privacy"])


class PrivacySettingsBody(BaseModel):
    no_train: bool | None = None
    zero_retention: bool | None = None
    consent_basis: str | None = None
    retention_days: int | None = None
    pii_redaction: bool | None = None


@router.get("")
async def get_privacy(
    principal: Annotated[Principal, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    await seed_tenant_defaults(db, principal.tenant_id)
    settings = await db.get(TenantPrivacySettings, principal.tenant_id)
    return {
        "tenant_id": str(principal.tenant_id),
        "no_train": settings.no_train if settings else True,
        "zero_retention": settings.zero_retention if settings else False,
        "consent_basis": settings.consent_basis if settings else "legitimate_interest",
        "retention_days": settings.retention_days if settings else 90,
        "pii_redaction": settings.pii_redaction if settings else False,
    }


@router.patch("")
async def update_privacy(
    body: PrivacySettingsBody,
    principal: Annotated[Principal, Depends(require_roles(Role.SECURITY, Role.ADMIN, Role.OWNER))],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    settings = await db.get(TenantPrivacySettings, principal.tenant_id)
    if not settings:
        settings = TenantPrivacySettings(tenant_id=principal.tenant_id)
        db.add(settings)
    for key, value in body.model_dump(exclude_unset=True).items():
        setattr(settings, key, value)
    await db.commit()
    return await get_privacy(principal, db)
