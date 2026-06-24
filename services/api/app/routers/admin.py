"""Admin audit log access."""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import require_permission
from app.auth.principal import Principal
from app.db.session import get_db
from app.models.audit_log import AuditLog

router = APIRouter(prefix="/admin", tags=["admin"])


class AuditEntry(BaseModel):
    id: str
    action: str
    actor_email: str | None
    resource: str | None
    created_at: str


class AuditListResponse(BaseModel):
    entries: list[AuditEntry]
    total: int


@router.get("/audit", response_model=AuditListResponse)
async def list_audit_logs(
    principal: Annotated[Principal, Depends(require_permission("audit.view"))],
    db: Annotated[AsyncSession, Depends(get_db)],
    limit: int = Query(default=50, le=200),
    offset: int = Query(default=0, ge=0),
) -> AuditListResponse:
    stmt = (
        select(AuditLog)
        .where(AuditLog.tenant_id == principal.tenant_id)
        .order_by(AuditLog.created_at.desc())
        .limit(limit)
        .offset(offset)
    )
    result = await db.execute(stmt)
    rows = result.scalars().all()

    count_stmt = select(AuditLog).where(AuditLog.tenant_id == principal.tenant_id)
    count_result = await db.execute(count_stmt)
    total = len(count_result.scalars().all())

    return AuditListResponse(
        entries=[
            AuditEntry(
                id=str(r.id),
                action=r.action,
                actor_email=r.actor_email,
                resource=r.resource,
                created_at=r.created_at.isoformat(),
            )
            for r in rows
        ],
        total=total,
    )
