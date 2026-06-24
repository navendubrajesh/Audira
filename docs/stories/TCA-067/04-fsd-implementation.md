# TCA-067 — FSD Implementation

## Files changed

### API (`services/api/`)

| Path | Change |
|---|---|
| `app/auth/roles.py` | 11 PRD roles + permission matrix |
| `app/auth/principal.py` | Authenticated principal |
| `app/auth/session.py` | Resonode JWT issue/verify |
| `app/auth/workos_client.py` | WorkOS OAuth URL + code exchange |
| `app/auth/dependencies.py` | `get_current_user`, `require_permission`, `require_roles` |
| `app/models/user.py` | User table |
| `app/models/audit_log.py` | Append-only audit log |
| `app/services/audit.py` | Audit recording |
| `app/services/user_service.py` | SSO + SCIM user provisioning |
| `app/routers/auth.py` | Login, callback, dev-login, me, roles, logout |
| `app/routers/webhooks.py` | WorkOS Directory Sync webhook |
| `app/routers/admin.py` | Audit log listing |
| `app/main.py` | Lifespan DB init + router registration |
| `app/config.py` | Auth + WorkOS settings |
| `tests/test_auth.py` | 6 integration tests |

### Web (`apps/web/`)

| Path | Change |
|---|---|
| `src/lib/auth.ts` | Session cookie + API helpers |
| `src/components/auth/login-card.tsx` | Login + callback client |
| `src/components/user-menu.tsx` | User header + sign out |
| `src/components/app-header.tsx` | Server-side session check |
| `src/app/login/page.tsx` | Login screen |
| `src/app/auth/callback/page.tsx` | SSO callback handler |

## Environment variables

See `.env.example` — `WORKOS_*` for production SSO/SCIM; `AUTH_MODE=development` for local dev login.

## Migration

Tables `users` and `audit_logs` created automatically on API startup (`Base.metadata.create_all`).

## Hand-off → QA

Run `pytest services/api/tests` and manual login at `/login` with dev credentials.
