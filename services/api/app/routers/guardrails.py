"""Guardrail configuration and checks (TCA-037, TCA-044, TCA-060)."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import get_current_user, require_roles
from app.auth.principal import Principal
from app.auth.roles import Role
from app.db.session import get_db
from app.models.governance import TenantGuardrailSettings
from app.services.audit import record_audit
from app.services.guardrails import (
    check_generative_governance,
    check_regulated_claims,
    guardrailed_rewrite,
)
from app.services.seed_defaults import seed_tenant_defaults

router = APIRouter(prefix="/guardrails", tags=["guardrails"])


class GuardrailSettingsBody(BaseModel):
    generative_governance: bool | None = None
    rewrite_assist: bool | None = None
    regulated_claims: bool | None = None
    block_on_fail: bool | None = None


class GuardrailCheckRequest(BaseModel):
    text: str


class RewriteRequest(BaseModel):
    text: str
    suggestion: str


@router.get("/settings")
async def get_settings(
    principal: Annotated[Principal, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    await seed_tenant_defaults(db, principal.tenant_id)
    row = await db.get(TenantGuardrailSettings, principal.tenant_id)
    return {
        "tenant_id": str(principal.tenant_id),
        "generative_governance": row.generative_governance if row else False,
        "rewrite_assist": row.rewrite_assist if row else False,
        "regulated_claims": row.regulated_claims if row else False,
        "block_on_fail": row.block_on_fail if row else False,
        "stories": ["TCA-037", "TCA-044", "TCA-060"],
    }


@router.patch("/settings")
async def update_settings(
    body: GuardrailSettingsBody,
    principal: Annotated[Principal, Depends(require_roles(Role.ADMIN, Role.OWNER, Role.SECURITY))],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    row = await db.get(TenantGuardrailSettings, principal.tenant_id)
    if not row:
        row = TenantGuardrailSettings(tenant_id=principal.tenant_id)
        db.add(row)
    for key, value in body.model_dump(exclude_unset=True).items():
        setattr(row, key, value)
    await db.commit()
    await record_audit(
        db,
        tenant_id=principal.tenant_id,
        action="guardrails.settings_updated",
        actor_user_id=principal.user_id,
        actor_email=principal.email,
        metadata=body.model_dump(exclude_unset=True),
    )
    return await get_settings(principal, db)


@router.post("/check/generative")
async def check_generative(
    body: GuardrailCheckRequest,
    principal: Annotated[Principal, Depends(get_current_user)],
):
    """TCA-037 — generative AI content governance check."""
    return check_generative_governance(body.text)


@router.post("/check/regulated")
async def check_regulated(
    body: GuardrailCheckRequest,
    principal: Annotated[Principal, Depends(get_current_user)],
):
    """TCA-060 — regulated claim detection."""
    return check_regulated_claims(body.text)


@router.post("/rewrite/propose")
async def propose_rewrite(
    body: RewriteRequest,
    principal: Annotated[Principal, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """TCA-044 — human-in-the-loop rewrite proposal."""
    row = await db.get(TenantGuardrailSettings, principal.tenant_id)
    if row and not row.rewrite_assist:
        raise HTTPException(status_code=403, detail="Rewrite assist is not enabled for this tenant.")
    result = guardrailed_rewrite(body.text, body.suggestion)
    await record_audit(
        db,
        tenant_id=principal.tenant_id,
        action="guardrails.rewrite_proposed",
        actor_user_id=principal.user_id,
        actor_email=principal.email,
        metadata={"status": "pending_human_approval"},
    )
    return result
