"""Authenticated principal."""

from dataclasses import dataclass
from uuid import UUID

from app.auth.roles import Role


@dataclass(frozen=True)
class Principal:
    user_id: UUID
    email: str
    tenant_id: UUID
    roles: list[Role]
    workos_user_id: str | None = None

    def has_role(self, *roles: Role) -> bool:
        return any(r in self.roles for r in roles)

    def has_any_role(self, roles: set[Role]) -> bool:
        return any(r in roles for r in self.roles)
