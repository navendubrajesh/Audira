"""Audira.run session JWT issue and verify."""

from datetime import UTC, datetime, timedelta
from uuid import UUID

import jwt
from pydantic import BaseModel

from app.auth.principal import Principal
from app.auth.roles import Role, parse_roles
from app.config import settings


class TokenPayload(BaseModel):
    sub: str
    email: str
    tenant_id: str
    roles: list[str]
    workos_user_id: str | None = None
    exp: int
    iss: str = "audira"


def create_session_token(
    user_id: UUID,
    email: str,
    tenant_id: UUID,
    roles: list[Role],
    workos_user_id: str | None = None,
) -> str:
    now = datetime.now(UTC)
    payload = {
        "sub": str(user_id),
        "email": email,
        "tenant_id": str(tenant_id),
        "roles": [r.value for r in roles],
        "workos_user_id": workos_user_id,
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(hours=settings.jwt_expiry_hours)).timestamp()),
        "iss": "audira",
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm="HS256")


def decode_session_token(token: str) -> Principal:
    payload = jwt.decode(token, settings.jwt_secret, algorithms=["HS256"], issuer="audira")
    data = TokenPayload.model_validate(payload)
    return Principal(
        user_id=UUID(data.sub),
        email=data.email,
        tenant_id=UUID(data.tenant_id),
        roles=parse_roles(data.roles),
        workos_user_id=data.workos_user_id,
    )
