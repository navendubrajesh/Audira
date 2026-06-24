# TCA-068 — FSD Implementation

- `app/models/tenant.py` — Tenant with region, encryption, TLS config
- `app/residency/regions.py` — IN/EU/SG region map
- `app/services/tenant_service.py` — isolation helpers, seed default tenant
- `app/routers/tenant.py` — residency GET/PATCH, isolation verify
- `apps/web/src/components/residency-card.tsx` — settings preview UI

## Hand-off → QA

16 API tests pass including cross-tenant 404.
