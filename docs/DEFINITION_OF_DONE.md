# Definition of Done (Global)

Applies to every backlog story unless a story explicitly overrides.

A story is **Done** when:

- [ ] Code merged via CI with **passing automated tests**
- [ ] **Acceptance criteria** demonstrably met (evidence in `05-qa-report.md`)
- [ ] Mapping/calibration **golden-set regression green** where the mapping layer is touched
- [ ] **Security/privacy** checks passed — no PII in logs; residency honoured for data touched
- [ ] **Accessibility** — WCAG 2.2 AA for any UI surface added or changed
- [ ] **Telemetry/audit** emitted for user-visible actions and overrides
- [ ] **Documentation** updated — story folder complete; API docs if endpoints added
- [ ] **Model/version stamping** verified for any analysis-producing change (FR-E03-7)
- [ ] **Progress ledger** updated with status `done`, date, and commit ref

---

## Phase 0 bootstrap DoD

Phase 0 is Done when:

- [x] Excel parsed → `data/backlog.json`
- [x] Build order computed → `docs/BUILD_ORDER.md`
- [x] Monorepo scaffolded (web, api, worker, design tokens)
- [x] Docker Compose for local dev
- [x] CI pipeline configured
- [x] Team/workflow/guardrail/baseline docs in place
- [x] **Paused** before first story — awaiting go-ahead
