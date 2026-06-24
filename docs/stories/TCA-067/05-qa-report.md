# TCA-067 — QA Report

**Story:** Enterprise SSO & RBAC  
**Date:** 2026-06-24  
**Result:** PASS

## Acceptance criteria

| AC | Evidence | Status |
|---|---|---|
| SAML/OIDC SSO via WorkOS | `GET /auth/login` → WorkOS AuthKit; `GET /auth/callback` exchanges code; dev mode at `/login` when WorkOS unset | PASS |
| SCIM provisioning | `POST /webhooks/workos/directory` handles `dsync.user.created/updated/deleted`; group→role mapping | PASS |
| Granular roles | 11 PRD roles in `app/auth/roles.py`; `require_permission` / `require_roles` enforced | PASS |
| Access audited | `audit_logs` table; login, logout, access_denied, SCIM events recorded; `GET /admin/audit` for Security/Admin | PASS |

## Automated tests

```
pytest services/api/tests — 7 passed
npm run build:web — success
```

## NFR spot-checks

| Check | Status |
|---|---|
| No PII in audit metadata beyond actor email (required for AC) | PASS |
| WCAG — login button focus ring, contrast on brand buttons | PASS |
| API docs updated at `/docs` (auth + admin + webhooks routes) | PASS |

## Manual verification (dev)

1. Start `docker compose up -d` + `npm run dev:web`
2. Visit `/login` → dev login as admin → header shows email + role
3. Sign out → audit log contains `auth.logout` (Security role)

## Notes

- Production requires `WORKOS_API_KEY`, `WORKOS_CLIENT_ID`, `WORKOS_WEBHOOK_SECRET`, and strong `JWT_SECRET`.
- SCIM group mapping is initial (`resonode-admin`, etc.) — tenant-configurable mapping deferred to TCA-074.
