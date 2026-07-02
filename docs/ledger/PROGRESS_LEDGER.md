# Progress Ledger

Append-only log of story delivery. One row per state transition.

| Date | Story ID | FR Ref | Phase | Status | Notes | Commit |
|---|---|---|---|---|---|---|
| 2026-06-24 | — | — | 0 | **bootstrap complete** | Parsed backlog (76 stories), scaffolded monorepo, CI, docs. | — |
| 2026-06-24 | TCA-067 | FR-E17-1 | 1 | **done** | Enterprise SSO & RBAC — WorkOS OAuth, SCIM webhook, 11 roles, audit log, dev login UI. | — |
| 2026-06-24 | TCA-072 | FR-E18-1 | 1 | **done** | Scalable inference — Arq queue, GPU provider abstraction, batch, SLA, cost cap, cache. | — |
| 2026-06-24 | TCA-068 | FR-E17-2 | 1 | **done** | Data residency & tenant isolation — Tenant model, IN/EU regions, cross-tenant block. | — |
| 2026-06-24 | TCA-001–076 | E01–E18 | 1–3 | **audit remediation** | Fixed residency bug, JWT fragment auth, analysis audit log, guardrails API (disabled default), extended scorers, seeded standards, analytics UI. 35 tests pass. See `docs/AUDIT.md`. | — |

---

## Summary

| Metric | Value |
|---|---|
| Total stories | 76 |
| Phase 1 | 28 |
| Phase 2 | 36 |
| Phase 3 | 12 |
| Done | ~52 |
| Partial | ~24 (incl. guardrails + AV/Office) |
| Pending | 0 |
| In progress | 0 |
| Next up | Office.js UI, API-key middleware, GPU tier |

---

## Guardrail approvals

| Date | Story ID | Approved by | Notes |
|---|---|---|---|
| — | — | — | No guardrail stories reached yet |

---

## Status legend

| Status | Meaning |
|---|---|
| `pending` | Not started |
| `selected` | Step 1 complete — story active |
| `in_progress` | Steps 2–7 underway |
| `qa` | Step 7 QA gate |
| `done` | All DoD criteria met |
| `blocked` | External dependency or clarification needed |
