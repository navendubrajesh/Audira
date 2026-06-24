"""User provisioning from SSO and SCIM."""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.roles import Role, parse_roles
from app.models.user import User
from app.tenants import DEFAULT_TENANT_ID


async def get_user_by_email(db: AsyncSession, email: str) -> User | None:
    result = await db.execute(select(User).where(User.email == email))
    return result.scalar_one_or_none()


async def get_user_by_workos_id(db: AsyncSession, workos_user_id: str) -> User | None:
    result = await db.execute(select(User).where(User.workos_user_id == workos_user_id))
    return result.scalar_one_or_none()


async def upsert_user_from_sso(
    db: AsyncSession,
    *,
    email: str,
    workos_user_id: str,
    roles: list[Role] | None = None,
    tenant_id: UUID | None = None,
) -> User:
    user = await get_user_by_workos_id(db, workos_user_id) or await get_user_by_email(db, email)

    if user:
        user.email = email
        user.workos_user_id = workos_user_id
        user.is_active = True
        if roles is not None:
            user.roles = [r.value for r in roles]
    else:
        role_values = [r.value for r in (roles or [Role.COMMS_MANAGER])]
        user = User(
            email=email,
            workos_user_id=workos_user_id,
            tenant_id=tenant_id or DEFAULT_TENANT_ID,
            roles=role_values,
            is_active=True,
        )
        db.add(user)

    await db.commit()
    await db.refresh(user)
    return user


async def provision_user_scim(
    db: AsyncSession,
    *,
    email: str,
    workos_user_id: str,
    roles: list[str],
    active: bool = True,
) -> User:
    user = await get_user_by_workos_id(db, workos_user_id) or await get_user_by_email(db, email)
    if user:
        user.email = email
        user.workos_user_id = workos_user_id
        user.roles = roles
        user.is_active = active
    else:
        user = User(
            email=email,
            workos_user_id=workos_user_id,
            tenant_id=DEFAULT_TENANT_ID,
            roles=roles,
            is_active=active,
        )
        db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


def user_to_principal(user: User):
    from app.auth.principal import Principal

    return Principal(
        user_id=user.id,
        email=user.email,
        tenant_id=user.tenant_id,
        roles=parse_roles(user.roles),
        workos_user_id=user.workos_user_id,
    )
