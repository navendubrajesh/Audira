"""WorkOS Directory Sync (SCIM) webhooks."""

import json
import hashlib
import hmac
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.db.session import get_db
from app.services.audit import record_audit
from app.services.user_service import get_user_by_workos_id, provision_user_scim

router = APIRouter(prefix="/webhooks/workos", tags=["webhooks"])


class DirectoryEvent(BaseModel):
    event: str
    data: dict[str, Any]


def verify_workos_signature(payload: bytes, signature: str | None, secret: str) -> bool:
    if not signature or not secret:
        return False
    expected = hmac.new(secret.encode(), payload, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, signature)


def _extract_role_from_groups(data: dict[str, Any]) -> list[str]:
    """Map WorkOS directory groups to Resonode roles (configurable per tenant later)."""
    groups = data.get("groups") or []
    group_names = {g.get("name", "").lower() for g in groups if isinstance(g, dict)}
    role_map = {
        "resonode-admin": "admin",
        "resonode-comms": "comms_manager",
        "resonode-brand": "brand_manager",
        "resonode-security": "security",
    }
    roles = [role_map[name] for name in group_names if name in role_map]
    return roles or ["comms_manager"]


@router.post("/directory")
async def directory_webhook(
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> dict[str, str]:
    body = await request.body()
    signature = request.headers.get("WorkOS-Signature")

    if settings.workos_webhook_secret:
        if not verify_workos_signature(body, signature, settings.workos_webhook_secret):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid signature")
    elif settings.environment == "production":
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Webhook secret not configured",
        )

    payload = DirectoryEvent.model_validate(json.loads(body))
    event = payload.event
    data = payload.data

    if event in ("dsync.user.created", "dsync.user.updated"):
        email = data.get("email")
        workos_id = data.get("id")
        if not email or not workos_id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Missing user fields")

        roles = _extract_role_from_groups(data)
        user = await provision_user_scim(
            db,
            email=email,
            workos_user_id=workos_id,
            roles=roles,
            active=data.get("state") != "inactive",
        )
        action = (
            "scim.user_provisioned" if event == "dsync.user.created" else "scim.user_updated"
        )
        await record_audit(
            db,
            tenant_id=user.tenant_id,
            action=action,
            actor_email=email,
            resource=f"user:{user.id}",
            metadata={"workos_id": workos_id, "roles": roles},
        )

    elif event == "dsync.user.deleted":
        workos_id = data.get("id")
        if workos_id:
            user = await get_user_by_workos_id(db, workos_id)
            if user:
                user.is_active = False
                await db.commit()
                await record_audit(
                    db,
                    tenant_id=user.tenant_id,
                    action="scim.user_deprovisioned",
                    actor_email=user.email,
                    resource=f"user:{user.id}",
                )

    return {"status": "ok"}
