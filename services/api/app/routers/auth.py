"""Auth API routes — Google OAuth + session."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import oauth
from app.auth.dependencies import get_current_user, require_permission
from app.auth.principal import Principal
from app.auth.roles import ROLE_LABELS, Role, parse_roles
from app.auth.session import create_session_token
from app.config import settings
from app.db.session import get_db
from app.services.audit import record_audit
from app.services.user_service import get_user_by_workos_id, upsert_user_from_sso

router = APIRouter(prefix="/auth", tags=["auth"])


class MeResponse(BaseModel):
    user_id: str
    email: str
    tenant_id: str
    roles: list[str]
    role_labels: list[str]


class RoleInfo(BaseModel):
    id: str
    label: str


class LogoutResponse(BaseModel):
    status: str = "ok"


@router.get("/login")
async def login(return_url: str | None = Query(default=None)) -> RedirectResponse:
    if not oauth.is_google_configured():
        if settings.auth_mode == "development":
            return RedirectResponse(f"{settings.web_app_url}/login?dev=1")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Google sign-in is not configured.",
        )

    state = oauth.sign_state(return_url or settings.web_app_url)
    return RedirectResponse(oauth.build_authorize_url(state))


@router.get("/callback")
async def callback(
    code: str | None = Query(default=None),
    state: str | None = Query(default=None),
    error: str | None = Query(default=None),
    db: AsyncSession = Depends(get_db),
) -> RedirectResponse:
    if error or not code:
        return RedirectResponse(
            f"{settings.web_app_url}/login?error=oauth",
            status_code=status.HTTP_303_SEE_OTHER,
        )
    if not state:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Missing state")

    try:
        return_url = oauth.verify_state(state)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired sign-in request. Please try again.",
        ) from exc

    try:
        email, google_user_id = await oauth.complete_login(code)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="We could not complete sign-in. Please try again.",
        ) from exc

    scoped_id = f"google:{google_user_id}"
    existing = await get_user_by_workos_id(db, scoped_id)
    preserve_roles = parse_roles(existing.roles) if existing and existing.roles else None

    user = await upsert_user_from_sso(
        db,
        email=email,
        workos_user_id=scoped_id,
        roles=preserve_roles,
    )

    token = create_session_token(
        user_id=user.id,
        email=user.email,
        tenant_id=user.tenant_id,
        roles=parse_roles(user.roles),
        workos_user_id=user.workos_user_id,
    )

    await record_audit(
        db,
        tenant_id=user.tenant_id,
        action="auth.login",
        actor_user_id=user.id,
        actor_email=user.email,
        resource="oauth",
        metadata={"provider": "google"},
    )

    return RedirectResponse(
        f"{return_url}/auth/callback#token={token}",
        status_code=status.HTTP_303_SEE_OTHER,
    )


@router.post("/dev-login")
async def dev_login(
    email: str = Query(...),
    role: Role = Query(default=Role.COMMS_MANAGER),
    db: AsyncSession = Depends(get_db),
) -> dict[str, str]:
    if settings.auth_mode != "development":
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not available")

    user = await upsert_user_from_sso(
        db,
        email=email,
        workos_user_id=f"dev-{email}",
        roles=[role],
    )
    token = create_session_token(
        user_id=user.id,
        email=user.email,
        tenant_id=user.tenant_id,
        roles=parse_roles(user.roles),
        workos_user_id=user.workos_user_id,
    )
    await record_audit(
        db,
        tenant_id=user.tenant_id,
        action="auth.login",
        actor_user_id=user.id,
        actor_email=user.email,
        resource="dev",
    )
    return {"token": token}


@router.get("/me", response_model=MeResponse)
async def me(principal: Annotated[Principal, Depends(get_current_user)]) -> MeResponse:
    return MeResponse(
        user_id=str(principal.user_id),
        email=principal.email,
        tenant_id=str(principal.tenant_id),
        roles=[r.value for r in principal.roles],
        role_labels=[ROLE_LABELS[r] for r in principal.roles],
    )


@router.get("/roles", response_model=list[RoleInfo])
async def list_roles(
    _: Annotated[Principal, Depends(require_permission("users.view"))],
) -> list[RoleInfo]:
    return [RoleInfo(id=r.value, label=ROLE_LABELS[r]) for r in Role]


@router.post("/logout", response_model=LogoutResponse)
async def logout(
    principal: Annotated[Principal, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
) -> LogoutResponse:
    await record_audit(
        db,
        tenant_id=principal.tenant_id,
        action="auth.logout",
        actor_user_id=principal.user_id,
        actor_email=principal.email,
    )
    return LogoutResponse()
