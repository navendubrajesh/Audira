# Code Audit Report — 2026-06-24

Full audit of 76 backlog stories against `services/api`, `services/shared`, `apps/web`.

## Summary

| Category | Count | Notes |
|---|---:|---|
| Fully implemented (MVP+) | ~45 | Text analysis path, platform, governance |
| Partial (needs production hardening) | ~28 | AV/OCR, Office UI, region routing |
| Guardrails (implemented, disabled by default) | 3 | TCA-037, TCA-044, TCA-060 |

**Tests:** 35 API tests passing.

---

## Critical fixes applied

| Issue | Fix |
|---|---|
| Tenant residency loaded default tenant | `GET /tenant/residency` now uses `principal.tenant_id` |
| JWT in URL query string | SSO callback uses `#token=` fragment; web reads hash |
| Analysis runs not audit-logged | `analysis.completed` audit on every run |
| Empty standards library | Seeded inclusive/jargon rules per tenant |
| Guardrails not implemented | `/guardrails/*` with per-tenant toggles (off by default) |
| Phase 2 scorers missing | Extended metrics: emotion, crisis, cognitive load, etc. |
| Quality gates static only | `TenantQualityGates` model + PATCH endpoint |
| Privacy flags not enforced | `no_train` in inference payload; `zero_retention` skips storing input text |
| Retention not enforced | `GET /analyze/runs` filters by `retention_days` |

---

## Story status by epic

### E01 — Context (TCA-001–006)
- **Done:** Audiences, brand, artifact types, objectives, language detection heuristic
- **Partial:** TCA-006 full Indic/Hindi norms (detection only)

### E02 — Ingestion (TCA-007–012)
- **Done:** docx/pdf/pptx/txt upload, engineering exclusion
- **Partial:** TCA-009 AV (job stub → `/inference`), TCA-010 URL fetch, TCA-011 deck rendering

### E03 — Neuro engine (TCA-013–019)
- **Done:** Provider abstraction, mapping, model registry, rerun, licence gate
- **Partial:** Real GPU TRIBE v2 in production path

### E04–E08 — Scoring (TCA-020–038)
- **Done:** Readability, jargon, inclusive, brand, tone, structure, composite, heatmap proxy, compare with diffs, explainability
- **Partial:** TCA-021/022 pixel-level visual (text proxies implemented)

### E09–E15 — Analytics & workflow
- **Done:** Dashboard API + web `/analytics`, campaigns list, comments API, scorecards
- **Partial:** Branded PDF export, full approval workflow UI

### E12 — Integrations (TCA-048–050)
- **Partial:** Add-in API + manifest; API key creation; OpenAPI at `/docs`

### E16–E18 — Platform
- **Done:** SSO, RBAC, residency metadata, inference queue, privacy, observability, guardrails

### Guardrails (TCA-037, TCA-044, TCA-060)
- **Implemented, disabled by default:** Enable via `PATCH /guardrails/settings` after legal sign-off

---

## Remaining production gaps

1. **Office.js task pane UI** — backend ready; frontend add-in not built
2. **Real AV pipeline** — Whisper + frame alignment on GPU tier
3. **Region-pinned storage/processing** — metadata only today
4. **API key auth middleware** — keys created but not wired to route auth
5. **TRIBE v2 commercial licence** — blocked in production until legal sign-off

---

## Test coverage

| Module | Tests |
|---|---|
| Auth, residency, inference | Existing suite |
| Analysis, compare, quality gates | `test_analysis.py`, `test_audit_fixes.py` |
| Guardrails, extended metrics, API keys | `test_audit_remediation.py` |

---

## Recommended next steps

1. Wire API-key middleware for `/features/addin/analyze` and `/analyze`
2. Build Office.js task pane (TCA-048)
3. Connect Render GPU tier for full neuro path
4. Enable guardrails per tenant after legal approval
