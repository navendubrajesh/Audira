"""Audit logging service."""

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.audit_log import AuditLog


async def record_audit(
    db: AsyncSession,
    *,
    tenant_id: UUID,
    action: str,
    actor_user_id: UUID | None = None,
    actor_email: str | None = None,
    resource: str | None = None,
    metadata: dict | None = None,
) -> AuditLog:
    entry = AuditLog(
        tenant_id=tenant_id,
        actor_user_id=actor_user_id,
        actor_email=actor_email,
        action=action,
        resource=resource,
        metadata_=metadata,
    )
    db.add(entry)
    await db.commit()
    await db.refresh(entry)
    return entry
