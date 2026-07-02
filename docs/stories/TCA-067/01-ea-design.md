# TCA-067 — EA Design

**Story:** Enterprise SSO & RBAC  
**FR:** FR-E17-1  
**Platform:** Platform / Shared Backend (+ web login surfaces)

## Acceptance criteria mapping

| AC | Implementation |
|---|---|
| SAML/OIDC SSO via WorkOS | API `/auth/login` → WorkOS AuthKit → `/auth/callback` → Audira.run session JWT |
| SCIM provisioning | `POST /webhooks/workos/directory` — Directory Sync events (create/update/delete users) |
| Granular roles | 11 PRD roles in `app/auth/roles.py`; `require_roles()` / `require_permission()` deps |
| Access audited | Append-only `audit_logs` table; events on login, logout, denied, SCIM |

## Component diagram

```
┌─────────────┐     OAuth/OIDC      ┌──────────────┐
│  Next.js    │ ──────────────────► │   WorkOS     │
│  (Vercel)   │ ◄── callback token  │  AuthKit     │
└──────┬──────┘                     └──────────────┘
       │ Bearer JWT
       ▼
┌─────────────┐     SCIM webhook    ┌──────────────┐
│  FastAPI    │ ◄────────────────── │   WorkOS     │
│  (Render)   │                     │  Directory   │
└──────┬──────┘                     └──────────────┘
       │
       ▼
┌─────────────┐
│  Postgres   │  users, audit_logs
└─────────────┘
```

## API contracts

| Method | Path | Auth | Purpose |
|---|---|---|---|
| GET | `/auth/login` | Public | Redirect to WorkOS (or dev login hint) |
| GET | `/auth/callback` | Public | Exchange code, issue JWT, redirect to web |
| POST | `/auth/logout` | Bearer | Invalidate session audit |
| GET | `/auth/me` | Bearer | Current user + roles |
| GET | `/auth/roles` | Bearer | List assignable roles (Admin+) |
| POST | `/webhooks/workos/directory` | WorkOS signature | SCIM directory sync events |
| GET | `/admin/audit` | Admin/Security | Paginated access audit log |

## Session JWT (Audira.run-issued)

Claims: `sub`, `email`, `tenant_id`, `roles[]`, `exp`, `iss=audira`

Signed with `JWT_SECRET`. WorkOS identity stored on `users.workos_user_id`.

## Dev mode

When `WORKOS_API_KEY` is empty, `AUTH_MODE=development` enables header-based auth for tests:
`Authorization: Bearer dev:{email}:{role}`

## Data touchpoints

- **users** — provisioned via SSO callback or SCIM webhook
- **audit_logs** — append-only; no PII beyond actor email hash optional (email stored for admin audit per AC)

## Hand-off → BM

Copy needed for login page, access-denied states, role labels, audit log column headers.
