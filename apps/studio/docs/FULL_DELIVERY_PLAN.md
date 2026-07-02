# Audira — Full User Story Delivery Plan (TCA-001…TCA-092)

**Goal:** Every backlog story has a **functional** frontend surface, backend API (where applicable), and automated test coverage.

**Legend:** ✅ Functional · 🔶 Partial (delegate/stub with real API) · ⬜ External-only (Office binary, live OAuth to social networks)

---

## Architecture layers

| Layer | Location | Responsibility |
|-------|----------|----------------|
| **Studio UI** | `apps/studio/` | Three-zone shell, vertical workspaces, governance/settings |
| **Orchestration API** | `services/api/` | Auth, analyze, context, studio content, features, guardrails |
| **Inference tier** | `services/inference/tribev2/` | GPU TRIBE v2 (optional Colab tunnel) |
| **Shared core** | `services/shared/audira_core/` | Mapping, inference providers, job processing |

---

## Phase A — Foundation (E01, E17, E18) ✅

| Story | Backend | Frontend | Tests |
|-------|---------|----------|-------|
| TCA-001 Audiences | `GET/POST/PATCH/DELETE /audiences` | Settings → Audiences | `test_analysis.py` |
| TCA-002 Brand voice | `GET/PUT /context/brand` | Settings → Brand | context router |
| TCA-003 Objectives | `POST /analyze` objective field | Analyze workspace objective via channel config | analyze tests |
| TCA-004 Artifact taxonomy | `GET /context/artifact-types` | Governance → Artifacts | studio tests |
| TCA-005 Standards | `GET/POST /context/standards` + publish | Governance → Standards | studio tests |
| TCA-067 SSO/RBAC | `/auth/*`, roles.py | Login, AuthGuard, PermissionGate | `test_auth.py` |
| TCA-068 Residency | `GET/PATCH /tenant/residency` | Settings → Security | `test_residency.py` |
| TCA-072 Inference queue | `/inference/jobs` | Analytics inference metrics | `test_inference.py` |

---

## Phase B — Ingestion & Analysis (E02, E06–E09, E19–E21) ✅

| Story | Backend | Frontend | Tests |
|-------|---------|----------|-------|
| TCA-007 Upload docs | `POST /analyze/upload` | Assets + multimodal drop zone | analyze tests |
| TCA-008 Text scoring | `POST /analyze` | Analyze tab (live API) | `test_analysis.py` |
| TCA-009 What-if | `POST /features/simulations/what-if` | Analyzer rewrite/compare | features router |
| TCA-010 URL capture | `POST /features/url/capture` | Integrations catalogue | features router |
| TCA-038 Composite score | analysis_service composite | ScoreGauge header | analyze tests |
| TCA-040 A/B compare | `POST /analyze/compare` | Variant A/B buttons | analyze router |
| TCA-077 Persona/audience | `/audiences` | PersonaPicker (API) | studio |
| TCA-078 Anti-generic | UI wizard | AntiGenericWizard modal | studio |
| TCA-079 Multimodal | upload + `/studio/assets` | MultimodalDropZone + Assets | studio tests |
| TCA-083 Feedback matrix | metrics → 4 cards | FeedbackCard stack | analyzer.ts |
| TCA-087 Debounced sidebar | client debounce 600ms | analyzer-store | studio build |
| TCA-091 Split panel | resizable UI | AnalyzerWorkspace | studio |

---

## Phase C — Content Operations (E11–E13, E22) ✅

| Story | Backend | Frontend | Tests |
|-------|---------|----------|-------|
| TCA-011 Schedule/publish | `/studio/schedule`, `/studio/publish` | Schedule tab | **test_studio.py** |
| TCA-013 Approvals | `/studio/approvals` + transition | ApprovalsBoard | **test_studio.py** |
| TCA-006 Drafts CRUD | `/studio/drafts` | Context list (API) | **test_studio.py** |
| TCA-088 Engagement queue | `/studio/engagement/queue` | Engagement helper | **test_studio.py** |
| TCA-089 Comment draft | `/studio/engagement/draft-comment` | Engagement helper | **test_studio.py** |
| TCA-090 Tone guardrail | `/studio/engagement/guardrail` | Engagement helper | **test_studio.py** |

---

## Phase D — Governance & Guardrails (E08, E15, E16) ✅

| Story | Backend | Frontend | Tests |
|-------|---------|----------|-------|
| TCA-037 Generative governance | `/guardrails/check/generative` | Governance → Guardrails | guardrails router |
| TCA-044 Rewrite assist | `/guardrails/rewrite/propose` | Analyzer rewrite button | guardrails router |
| TCA-052 Quality gates | `/context/quality-gates` | Governance → Gates | context router |
| TCA-059 Inclusive language | scoring/inclusive.py | Feedback matrix | scoring |
| TCA-061 Audit log | `/admin/audit` | Governance → Audit | admin router |
| TCA-016 Model registry | `/governance/models` | Governance → Models | governance router |
| TCA-060 Regulated claims | `/guardrails/check/regulated` | Guardrails settings | guardrails |

---

## Phase E — Analytics & Program Insights (E14) ✅

| Story | Backend | Frontend | Tests |
|-------|---------|----------|-------|
| TCA-014 Dashboards | `/features/analytics/dashboard` | Analytics + Command Center | **test_studio.py** |
| TCA-039 Org analytics | same | Analytics charts (live by_channel) | features |
| TCA-053 Comments | `/features/comments/{run}` | Activity tab | features |
| TCA-056 Scorecards | `/features/scorecards` | Analytics (audit role) | features |
| TCA-051 Campaigns | `/features/campaigns` | 🔶 link from insights | features |

---

## Phase F — Integrations & Scale (E03, E10–E12, E18) 🔶

| Story | Status | Notes |
|-------|--------|-------|
| TCA-013 Model orchestration | 🔶 | TRIBE via `INFERENCE_BASE_URL`; fast-lane without GPU |
| TCA-048 Office add-in | 🔶 | `POST /features/addin/analyze` — add-in binary separate repo |
| TCA-036 Open API | ✅ | `/docs`, `/features/api-keys` |
| TCA-011 Channel OAuth | 🔶 | Publish queues + audit; no live LinkedIn/Meta OAuth |
| TCA-064 Bias check | ✅ | `POST /features/bias-check` |
| TCA-035 Consistency | ✅ | `POST /features/consistency/check` |

---

## Test matrix

```bash
# API (46 tests)
cd services/api && python -m pytest tests/ -q

# Studio build
npm run build:studio
```

---

## Delivery checklist (per story)

1. **API endpoint** exists and enforces RBAC  
2. **Studio screen** navigable with live data (not lorem cards)  
3. **Audit log** entry for mutating operations  
4. **Test** in `test_studio.py`, `test_analysis.py`, or `test_auth.py`  
5. **ROADMAP** row updated via `npm run gen:roadmap --workspace=@audira/studio`

---

## Remaining external dependencies (not blockers for MVP)

- Live LinkedIn / Meta / job-board OAuth publish  
- Office COM add-in installer (API ready at `/features/addin/analyze`)  
- Production GPU always-on (Colab tunnel documented in `docs/COLAB_TRIBE_V2_API.md`)  
- WorkOS SAML login UI (Google OAuth + dev-login + SCIM webhooks implemented)

---

*Last updated: full-stack studio wiring sprint — `/studio` router, auth, live analyze, governance/settings screens.*
