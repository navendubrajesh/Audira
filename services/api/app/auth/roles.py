"""Audira.run RBAC roles and permissions (PRD §11)."""

from enum import Enum


class Role(str, Enum):
    OWNER = "owner"
    ADMIN = "admin"
    COMMS_MANAGER = "comms_manager"
    INTERNAL_COMMS_LEAD = "internal_comms_lead"
    EXEC_OFFICE_WRITER = "exec_office_writer"
    LD_LEAD = "ld_lead"
    POLICY_COMPLIANCE = "policy_compliance"
    BRAND_MANAGER = "brand_manager"
    REVIEWER = "reviewer"
    ML_PLATFORM_ENG = "ml_platform_eng"
    SECURITY = "security"


ROLE_LABELS: dict[Role, str] = {
    Role.OWNER: "Owner",
    Role.ADMIN: "Administrator",
    Role.COMMS_MANAGER: "Comms Manager",
    Role.INTERNAL_COMMS_LEAD: "Internal Comms Lead",
    Role.EXEC_OFFICE_WRITER: "Exec-Office Writer",
    Role.LD_LEAD: "L&D Lead",
    Role.POLICY_COMPLIANCE: "Policy / Compliance Officer",
    Role.BRAND_MANAGER: "Brand Manager",
    Role.REVIEWER: "Reviewer",
    Role.ML_PLATFORM_ENG: "ML / Platform Engineer",
    Role.SECURITY: "Security / IT",
}

# Permission → roles that hold it
PERMISSIONS: dict[str, frozenset[Role]] = {
    "users.manage": frozenset({Role.OWNER, Role.ADMIN}),
    "users.view": frozenset({Role.OWNER, Role.ADMIN, Role.SECURITY}),
    "audit.view": frozenset({Role.OWNER, Role.ADMIN, Role.SECURITY}),
    "analyses.run": frozenset(
        {
            Role.OWNER,
            Role.ADMIN,
            Role.COMMS_MANAGER,
            Role.INTERNAL_COMMS_LEAD,
            Role.EXEC_OFFICE_WRITER,
            Role.LD_LEAD,
            Role.POLICY_COMPLIANCE,
            Role.BRAND_MANAGER,
            Role.REVIEWER,
        }
    ),
    "brand.manage": frozenset({Role.OWNER, Role.ADMIN, Role.BRAND_MANAGER}),
    "standards.manage": frozenset(
        {Role.OWNER, Role.ADMIN, Role.BRAND_MANAGER, Role.POLICY_COMPLIANCE}
    ),
    "audiences.manage": frozenset(
        {
            Role.OWNER,
            Role.ADMIN,
            Role.COMMS_MANAGER,
            Role.INTERNAL_COMMS_LEAD,
        }
    ),
    "governance.view": frozenset(
        {Role.OWNER, Role.ADMIN, Role.ML_PLATFORM_ENG, Role.SECURITY, Role.POLICY_COMPLIANCE}
    ),
}


def role_has_permission(role: Role, permission: str) -> bool:
    allowed = PERMISSIONS.get(permission, frozenset())
    return role in allowed


def user_has_permission(roles: list[Role], permission: str) -> bool:
    return any(role_has_permission(r, permission) for r in roles)


def parse_roles(raw: list[str]) -> list[Role]:
    result: list[Role] = []
    for value in raw:
        try:
            result.append(Role(value))
        except ValueError:
            continue
    return result
