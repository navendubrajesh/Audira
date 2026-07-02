/** Mirrors services/api/app/auth/roles.py PERMISSIONS map. */

const PERMISSIONS: Record<string, readonly string[]> = {
  "users.manage": ["owner", "admin"],
  "users.view": ["owner", "admin", "security"],
  "audit.view": ["owner", "admin", "security"],
  "analyses.run": [
    "owner",
    "admin",
    "comms_manager",
    "internal_comms_lead",
    "exec_office_writer",
    "ld_lead",
    "policy_compliance",
    "brand_manager",
    "reviewer",
  ],
  "brand.manage": ["owner", "admin", "brand_manager"],
  "standards.manage": ["owner", "admin", "brand_manager", "policy_compliance"],
  "audiences.manage": ["owner", "admin", "comms_manager", "internal_comms_lead"],
  "governance.view": ["owner", "admin", "ml_platform_eng", "security", "policy_compliance"],
};

export function hasPermission(roles: string[], permission: string): boolean {
  const allowed = PERMISSIONS[permission] ?? [];
  return roles.some((r) => allowed.includes(r));
}

export function hasAnyRole(roles: string[], ...required: string[]): boolean {
  return required.some((r) => roles.includes(r));
}

export type Permission = keyof typeof PERMISSIONS;
