"""FastAPI auth dependencies."""

from typing import Annotated
from uuid import UUID

import jwt
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.principal import Principal
from app.auth.roles import Role, parse_roles, user_has_permission
from app.auth.session import decode_session_token
from app.config import settings
from app.db.session import get_db
from app.services.audit import record_audit
from app.services.user_service import get_user_by_email, upsert_user_from_sso, user_to_principal
from app.tenants import DEFAULT_TENANT_ID

bearer_scheme = HTTPBearer(auto_error=False)


async def _principal_from_dev_token(
    db: AsyncSession, token: str, request: Request
) -> Principal:
    parts = token.removeprefix("dev:").split(":")
    if len(parts) < 2:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid dev token")
    email, role_str = parts[0], parts[1]
    try:
        role = Role(role_str)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail=f"Unknown role: {role_str}"
        ) from exc

    user = await get_user_by_email(db, email)
    if not user:
        user = await upsert_user_from_sso(
            db,
            email=email,
            workos_user_id=f"dev-{email}",
            roles=[role],
            tenant_id=DEFAULT_TENANT_ID,
        )
    return user_to_principal(user)


async def get_current_user(
    request: Request,
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer_scheme)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> Principal:
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = credentials.credentials

    if settings.auth_mode == "development" and token.startswith("dev:"):
        return await _principal_from_dev_token(db, token, request)

    try:
        return decode_session_token(token)
    except jwt.PyJWTError as exc:
        await record_audit(
            db,
            tenant_id=DEFAULT_TENANT_ID,
            action="auth.access_denied",
            actor_email=None,
            resource=request.url.path,
            metadata={"reason": "invalid_token"},
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired session",
        ) from exc


def require_permission(permission: str):
    async def checker(
        request: Request,
        principal: Annotated[Principal, Depends(get_current_user)],
        db: Annotated[AsyncSession, Depends(get_db)],
    ) -> Principal:
        if not user_has_permission(principal.roles, permission):
            await record_audit(
                db,
                tenant_id=principal.tenant_id,
                action="auth.access_denied",
                actor_user_id=principal.user_id,
                actor_email=principal.email,
                resource=request.url.path,
                metadata={"permission": permission},
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access not authorised",
            )
        return principal

    return checker


def require_roles(*roles: Role):
    allowed = set(roles)

    async def checker(
        request: Request,
        principal: Annotated[Principal, Depends(get_current_user)],
        db: Annotated[AsyncSession, Depends(get_db)],
    ) -> Principal:
        if not principal.has_any_role(allowed):
            await record_audit(
                db,
                tenant_id=principal.tenant_id,
                action="auth.access_denied",
                actor_user_id=principal.user_id,
                actor_email=principal.email,
                resource=request.url.path,
                metadata={"required_roles": [r.value for r in roles]},
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access not authorised",
            )
        return principal

    return checker
