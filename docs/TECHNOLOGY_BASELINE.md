# Technology Baseline — Standing Decision (Never Re-litigate)

**Product:** Audira.run — Enterprise Communications Neuro-Analyzer  
**Decided:** Phase 0 bootstrap  
**Supersedes:** Any Android/Kotlin template references in generic delivery playbooks. The backlog v1.1 bakes the web stack into acceptance criteria.

> **Deployment philosophy:** Vercel + Render are *one deployment target*, not *the* architecture. Everything is Dockerised from day one so identical images run on Render now and on a client's Kubernetes / on-prem later (TCA-069, TCA-074, FR-E17-3).

---

## Layer map

| Layer | Technology | Host | Notes |
|---|---|---|---|
| **Frontend** | Next.js 15 (App Router) + TypeScript + React | Vercel | Tailwind + shadcn/ui pattern; TanStack Query; Recharts for scores/heatmaps |
| **Office add-ins** | React + Office.js | Vercel (separate apps) | Word/PowerPoint (Phase 1), Outlook/Teams (Phase 2) — FR-E12 |
| **API & orchestration** | Python 3.12 + FastAPI + Pydantic | Render Web Service | Mapping/calibration IP, doc parsing, model orchestration; OpenAPI for SDK |
| **Async workers** | Arq (+ Redis queue) | Render Background Workers | Transcription, batch audits (FR-E18-2); submit → poll/webhook pattern |
| **Primary database** | PostgreSQL + pgvector | Render Postgres | Embeddings, norms, benchmarks |
| **Cache / queue** | Redis | Render Key Value | Cache + Arq broker |
| **Object storage** | Cloudflare R2 or AWS S3 | External (day one) | Artifacts, rendered slides, AV, reports — Render has no native blob store |
| **GPU inference** | TRIBE v2 + specialised models (PyTorch) | Modal / Replicate / Baseten / RunPod | **Decoupled** from Vercel/Render; FastAPI calls via abstraction (FR-E03-2) |
| **ASR** | faster-whisper (self-hosted) | Same GPU tier | No-training + residency (FR-E17-4, NFR-05) |
| **Document handling** | python-docx, python-pptx, PyMuPDF, LibreOffice headless, Tesseract/PaddleOCR | API/worker containers | |
| **Enterprise auth** | WorkOS (SAML/OIDC + SCIM) | WorkOS + API middleware | FR-E17-1; Clerk/Auth0 acceptable alternatives |
| **Observability** | Sentry + OpenTelemetry + log backend | Better Stack / Grafana Cloud / Datadog | Append-only audit log is a **separate immutable store** (FR-E16-5) |

---

## Architecture principles (EA mandate)

1. **Model-agnostic** — all model access through orchestration abstraction; no business logic hard-bound to TRIBE output shape (FR-E03-2).
2. **Stateless inference, stateful records** — every analysis reproducible from model + adapter + mapping + input hash (FR-E03-7).
3. **Tenant isolation by default** — no cross-tenant data bleed (FR-E18-3, FR-E17-2).
4. **Privacy-first** — PII handling per NFR-05; no content used to train shared models (FR-E17-4).
5. **Container-first** — Docker images for api, worker, and future GPU inference adapters; `docker-compose.yml` for local dev.

---

## Module structure (monorepo)

```
audira/
├── apps/web/              # Communications Studio (Next.js)
├── apps/addins/           # Office.js add-ins (Phase 1+)
├── services/api/          # FastAPI orchestration
├── services/worker/       # Arq background jobs
├── packages/design-tokens/# BM+UXD brand baseline
├── data/backlog.json      # Parsed backlog (source of truth mirror)
├── docs/                  # Ledger, workflow, per-story artifacts
└── scripts/parse_backlog.py
```

---

## Residency & platform caveats (flagged, not blocking Phase 0)

| Requirement | Risk | Mitigation |
|---|---|---|
| **NFR-06 India data residency** | Render/Vercel may lack India regions | Confirm current regions; data tier may need AWS Mumbai / Azure Central India |
| **FR-E17-3 on-prem / air-gapped** | Incompatible with PaaS | Docker + Helm/K8s manifests (Phase 2); same images as Render |

---

## What Phase 0 delivers vs Phase 1 stories

Phase 0 scaffolds the baseline above — **no TCA story is implemented yet**. First story after go-ahead: **TCA-067** (Enterprise SSO & RBAC).
