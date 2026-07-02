# Audira.run — Complete Deployment Guide

**Product:** Audira.run (Enterprise Communications Neuro-Analyzer)  
**Repository:** [github.com/navendubrajesh/Audira](https://github.com/navendubrajesh/Audira)  
**Last updated:** 2026-06-24  

This document is the end-to-end guide for deploying **Audira.run** to production using the **recommended stack**: **Vercel + Render + external GPU + R2/S3 + WorkOS**.

### Production URLs (Audira.run)

| Role | URL |
|---|---|
| Web app | `https://audira.run` |
| API | `https://api.audira.run` (Render custom domain) or `https://audira-api.onrender.com` |
| WorkOS OAuth callback | `https://api.audira.run/auth/callback` |
| GPU inference (private) | `https://inference.audira.run` |

**Quick setup checklist:** [DEPLOY_SETUP.md](./DEPLOY_SETUP.md)

---

## Table of contents

1. [Architecture overview](#1-architecture-overview)
2. [Platform matrix — what runs where](#2-platform-matrix--what-runs-where)
3. [Accounts & prerequisites](#3-accounts--prerequisites)
4. [Recommended deployment order](#4-recommended-deployment-order)
5. [GitHub & CI/CD](#5-github--cicd)
6. [Render — Postgres, Redis, API, Worker](#6-render--postgres-redis-api-worker)
7. [Vercel — Next.js frontend](#7-vercel--nextjs-frontend)
8. [GPU inference tier — TRIBE v2](#8-gpu-inference-tier--tribe-v2)
9. [Object storage — Cloudflare R2 or AWS S3](#9-object-storage--cloudflare-r2-or-aws-s3)
10. [WorkOS — Enterprise SSO & SCIM](#10-workos--enterprise-sso--scim)
11. [Environment variables reference](#11-environment-variables-reference)
12. [URL wiring & auth flow](#12-url-wiring--auth-flow)
13. [Data residency (India / EU / Singapore)](#13-data-residency-india--eu--singapore)
14. [Local development](#14-local-development)
15. [Office add-ins (Word / PowerPoint)](#15-office-add-ins-word--powerpoint)
16. [Observability & operations](#16-observability--operations)
17. [Production checklist](#17-production-checklist)
18. [Troubleshooting](#18-troubleshooting)
19. [Cost planning (indicative)](#19-cost-planning-indicative)
20. [Alternative & future targets](#20-alternative--future-targets)

---

## 1. Architecture overview

Audira.run is a **monorepo** with **five runtime tiers**. GitHub stores code and runs CI; it does **not** host production services.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              END USERS                                       │
│         Browser (Communications Studio)  │  Office 365 Add-ins (future)      │
└────────────────────────────┬────────────────────────────┬───────────────────┘
                             │ HTTPS                       │
                             ▼                             ▼
┌────────────────────────────────────┐    ┌──────────────────────────────────┐
│  VERCEL                            │    │  VERCEL (add-in host URL)         │
│  apps/web — Next.js 15             │    │  apps/addins — Office.js          │
│  • /login, /analyze, /           │    │  manifest → /analyze              │
└────────────────────────────┬───────┘    └──────────────────────────────────┘
                             │ NEXT_PUBLIC_API_URL
                             ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  RENDER — Web Service                                                        │
│  services/api — FastAPI                                                        │
│  • Auth (WorkOS OAuth callback)  • /analyze  • /inference  • /governance     │
└───────┬──────────────────────────────┬──────────────────────┬───────────────┘
        │                              │                      │
        ▼                              ▼                      ▼
┌───────────────┐            ┌─────────────────┐    ┌─────────────────────────┐
│ RENDER        │            │ RENDER          │    │ EXTERNAL GPU TIER        │
│ Postgres      │            │ Redis           │    │ services/inference/      │
│ + pgvector    │            │ (cache + queue) │    │ tribev2                  │
└───────────────┘            └────────┬────────┘    │ Modal / RunPod / AWS g5  │
                                      │             └────────────▲────────────┘
                                      ▼                          │
                            ┌─────────────────┐                  │
                            │ RENDER          │    INFERENCE_BASE_URL
                            │ Background      │──────────────────┘
                            │ Worker (Arq)    │
                            │ services/worker │
                            └─────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│  EXTERNAL SERVICES                                                           │
│  • WorkOS (SAML/OIDC + SCIM)   • Cloudflare R2 / AWS S3 (artifact blobs)    │
│  • Sentry / OTEL (optional)    • Hugging Face (TRIBE v2 model weights)      │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Request paths

| User action | Path |
|---|---|
| Sign in | Browser → Vercel `/login` → Render `/auth/login` → WorkOS → Render `/auth/callback` → redirect to Vercel with session cookie |
| Fast text analysis | Vercel `/analyze` → Render `POST /analyze` (no GPU, &lt;2s) |
| Full neuro analysis | Same, with `full_analysis: true` → API/worker → GPU `POST /v1/inference` |
| Batch inference job | Vercel → Render `POST /inference/jobs` → Redis queue → Worker → GPU |
| Document upload | Render `POST /analyze/upload` → parse → optional R2 storage → analysis |

---

## 2. Platform matrix — what runs where

| Component | Technology | Production host | Repo path | Docker |
|---|---|---|---|---|
| **Frontend** | Next.js 15, TypeScript, Tailwind | **Vercel** | `apps/web` | Optional (not used on Vercel) |
| **API** | Python 3.12, FastAPI, Uvicorn | **Render Web Service** | `services/api` | ✅ `services/api/Dockerfile` |
| **Worker** | Python 3.12, Arq | **Render Background Worker** | `services/worker` | ✅ `services/worker/Dockerfile` |
| **Database** | PostgreSQL 16 + **pgvector** | **Render Postgres** | — | Managed |
| **Queue / cache** | Redis 7 | **Render Key Value** | — | Managed |
| **GPU inference** | TRIBE v2 (PyTorch) | **Modal / RunPod / AWS / Azure GPU** | `services/inference/tribev2` | ✅ GPU Dockerfile |
| **Object storage** | S3-compatible | **Cloudflare R2** or **AWS S3** | — | External |
| **Auth** | WorkOS (SSO + SCIM) | **WorkOS SaaS** | middleware in API | External |
| **CI** | GitHub Actions | **GitHub** | `.github/workflows/ci.yml` | — |
| **Source code** | Git monorepo | **GitHub** | entire repo | — |

### What GitHub does **not** do

- Does not run FastAPI, Postgres, Redis, or GPU workloads in production
- Does not host the Next.js app (unless you chose self-hosted Node — not recommended)
- CI runners have **no GPU** — TRIBE v2 is never tested on GPU in standard CI

---

## 3. Accounts & prerequisites

Create accounts before deploying:

| Service | Purpose | Sign-up |
|---|---|---|
| **GitHub** | Source + CI | Already: `navendubrajesh/Audira` |
| **Render** | API, worker, Postgres, Redis | [render.com](https://render.com) |
| **Vercel** | Frontend | [vercel.com](https://vercel.com) |
| **WorkOS** | Enterprise SSO + SCIM | [workos.com](https://workos.com) |
| **Cloudflare R2** or **AWS S3** | Document/artifact storage | [cloudflare.com](https://www.cloudflare.com/products/r2/) |
| **Hugging Face** | TRIBE v2 model access | [huggingface.co](https://huggingface.co) |
| **GPU host** | TRIBE v2 inference | Modal, RunPod, or cloud GPU VM |
| **Sentry** (optional) | Error tracking | [sentry.io](https://sentry.io) |

### Local tools

- **Docker Desktop** — local Postgres, Redis, API, worker
- **Node.js 20+** — frontend dev
- **Python 3.12** — API tests
- **Git**

---

## 4. Recommended deployment order

Deploy in this sequence to avoid broken redirects and missing dependencies:

```
1. GitHub     → confirm main branch, CI green
2. Render     → Postgres (+ enable pgvector)
3. Render     → Redis
4. Render     → API Web Service (AUTH_MODE=development first)
5. Render     → Background Worker
6. Vercel     → Web app (point at Render API URL)
7. WorkOS     → configure redirect URI to Render /auth/callback
8. Render API → switch AUTH_MODE=workos, set WorkOS secrets
9. R2/S3      → bucket + API keys → set on Render API
10. GPU tier  → deploy tribev2 → set INFERENCE_BASE_URL on API + worker
11. Smoke test → login, /analyze, /inference/jobs
```

---

## 5. GitHub & CI/CD

### Repository structure

```
Audira/
├── apps/web/                 ← Vercel root (set in Vercel dashboard)
├── services/api/             ← Render API Docker context = repo root
├── services/worker/          ← Render worker Docker context = repo root
├── services/inference/tribev2/ ← GPU host
├── .github/workflows/ci.yml  ← runs on push to main/develop
└── .env.example              ← template (never commit .env)
```

### CI pipeline (automatic on push)

| Job | What it runs |
|---|---|
| **api** | `ruff check`, `pytest services/api/tests`, licence check script |
| **web** | `npm ci`, lint, vitest, `next build` |
| **backlog** | Validates backlog JSON generation |

### Branch strategy

- **`main`** — production; connect Vercel + Render auto-deploy to this branch
- **`develop`** — optional staging environment (duplicate Render/Vercel projects)

---

## 6. Render — Postgres, Redis, API, Worker

### 6.1 PostgreSQL (+ pgvector)

1. Render Dashboard → **New → PostgreSQL**
2. Choose region:
   - **EU pilots:** Frankfurt (`eu-central`) or closest EU
   - **India:** Render has **no India region** — use **Singapore** (`ap-southeast`) as closest, or external Postgres on AWS Mumbai (see [§13 Data residency](#13-data-residency-india--eu--singapore))
3. Plan: **Starter** for pilot; scale for production
4. Copy **Internal Database URL** and **External Database URL**

**Critical — convert connection string for SQLAlchemy async:**

Render gives:
```
postgres://user:pass@host/dbname
```

You must set on API and worker:
```
postgresql+asyncpg://user:pass@host/dbname
```

**Enable pgvector:**

In Render Postgres → **Shell** tab (if available on your plan):
```sql
CREATE EXTENSION IF NOT EXISTS vector;
```

Or connect with `psql` using the external URL and run the same command.

### 6.2 Redis

1. Render Dashboard → **New → Key Value** (Redis)
2. Same region as Postgres when possible
3. Copy **Internal Redis URL** → use as `REDIS_URL` on API and worker

### 6.3 API Web Service

1. **New → Web Service**
2. Connect GitHub repo `navendubrajesh/Audira`
3. Settings:

| Setting | Value |
|---|---|
| **Name** | `audira-api` |
| **Region** | Match Postgres (e.g. Singapore for APAC) |
| **Branch** | `main` |
| **Root Directory** | *(leave empty — repo root)* |
| **Runtime** | **Docker** |
| **Dockerfile Path** | `services/api/Dockerfile` |
| **Docker Context** | `.` (repository root) |
| **Instance type** | Starter → Standard for production |
| **Health Check Path** | `/health` |

4. **Environment variables** — see [§11](#11-environment-variables-reference). Minimum for first boot:

```env
DATABASE_URL=postgresql+asyncpg://...
REDIS_URL=redis://...
AUTH_MODE=development
JWT_SECRET=<random-32+-chars>
WEB_APP_URL=https://your-app.vercel.app
CORS_ORIGINS=["https://your-app.vercel.app"]
ENVIRONMENT=production
```

5. Deploy. Note the URL: `https://audira-api.onrender.com`

### 6.4 Background Worker

1. **New → Background Worker**
2. Same repo, branch `main`
3. Settings:

| Setting | Value |
|---|---|
| **Dockerfile Path** | `services/worker/Dockerfile` |
| **Docker Context** | `.` |
| **Start Command** | *(default from Dockerfile)* `arq worker.tasks.WorkerSettings` |

4. **Same env vars as API** for:
   - `DATABASE_URL`
   - `REDIS_URL`
   - `INFERENCE_BASE_URL`
   - `INFERENCE_API_KEY`
   - `INFERENCE_MONTHLY_COST_CAP_USD`

5. Worker does **not** need `CORS_ORIGINS` or `WEB_APP_URL` unless you add features that need them.

### 6.5 Render free tier notes

- Free web services **spin down** after inactivity (~50s cold start)
- Free Postgres expires after 90 days — use paid for pilots
- Worker + Redis typically need paid plans for reliable queue processing

---

## 7. Vercel — Next.js frontend

### 7.1 Import project

1. [vercel.com/new](https://vercel.com/new) → Import `navendubrajesh/Audira`
2. Configure:

| Setting | Value |
|---|---|
| **Framework Preset** | Next.js |
| **Root Directory** | `apps/web` |
| **Build Command** | `npm run build` (default in workspace) |
| **Output Directory** | `.next` (default) |
| **Install Command** | `npm ci` from monorepo root — set **Root Directory** to `apps/web` and override install if needed |

**Monorepo install (recommended):**

In Vercel project settings:
- Root Directory: `apps/web`
- Install Command: `cd ../.. && npm ci`
- Build Command: `cd ../.. && npm run build:web`

Or deploy from repo root with:
- Root Directory: `.`
- Build Command: `npm run build:web`

### 7.2 Environment variables (Vercel)

| Variable | Example | Notes |
|---|---|---|
| `NEXT_PUBLIC_API_URL` | `https://audira-api.onrender.com` | **Must be public** — browser calls API |

No secrets on Vercel except if you add server-side API routes later.

### 7.3 Domains

1. Vercel → Project → **Domains**
2. Add `app.yourcompany.com` (or use `*.vercel.app` for pilot)
3. Update `WEB_APP_URL` and `CORS_ORIGINS` on Render API to match

### 7.4 Deploy

Push to `main` → Vercel auto-builds. Verify:
- `https://your-app.vercel.app/login`
- `https://your-app.vercel.app/analyze` (after dev login or SSO)

---

## 8. GPU inference tier — TRIBE v2

TRIBE v2 **never runs on Vercel or Render API containers**. It runs as a separate GPU service.

### 8.1 Model & licence

- Model: [facebook/tribev2](https://huggingface.co/facebook/tribev2)
- Licence: **CC-BY-NC-4.0** — commercial resale requires Meta licence (TCA-016)
- **Pilot/dev:** use `tribe-v2-stub` with empty `INFERENCE_BASE_URL` (mock metrics)
- **Production neuro analysis:** deploy GPU service + legal sign-off

### 8.2 Hugging Face setup

1. Create HF account and **access token**
2. Accept **LLaMA 3.2** gated model terms (TRIBE dependency)
3. Set `HF_TOKEN` on GPU service only

### 8.3 Deploy GPU service (generic)

**Build context:** `services/inference/tribev2/`  
**Endpoint:** `POST /v1/inference`  
**Health:** `GET /health`

#### Option A — RunPod

1. Create GPU Pod (A100 / A10 / RTX 4090, 24GB+ VRAM recommended)
2. Deploy Docker image built from `services/inference/tribev2/Dockerfile`
3. Expose port 8080 with HTTPS proxy or RunPod HTTP service
4. Set pod env: `HF_TOKEN`, `INFERENCE_API_KEY`

#### Option B — Modal

1. Wrap `main.py` as Modal web endpoint
2. Mount GPU (`gpu="A10G"` or similar)
3. Deploy; copy HTTPS URL

#### Option C — AWS EC2 (g5.xlarge+)

1. Launch GPU instance in target region (e.g. `ap-south-1` for India processing)
2. Install NVIDIA drivers, Docker
3. Run tribev2 container; put behind ALB + TLS

### 8.4 Wire to Render

On **API** and **Worker**:

```env
INFERENCE_BASE_URL=https://your-gpu-host.example.com
INFERENCE_API_KEY=<shared-secret>
INFERENCE_MONTHLY_COST_CAP_USD=500
```

On **GPU service**:

```env
INFERENCE_API_KEY=<same-shared-secret>
HF_TOKEN=<huggingface-token>
TRIBE_CACHE_DIR=/cache/tribev2
```

### 8.5 Verify GPU path

```bash
curl -X POST https://your-gpu-host/v1/inference \
  -H "Authorization: Bearer YOUR_INFERENCE_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"modality":"text","model_id":"facebook/tribev2","payload":{"text":"Hello team."}}'
```

Then from API:
```bash
curl -X POST https://audira-api.onrender.com/analyze \
  -H "Authorization: Bearer dev:you@co.com:comms_manager" \
  -H "Content-Type: application/json" \
  -d '{"text":"Hello team.","full_analysis":true,"model_id":"tribe-v2-stub"}'
```

*(Use real SSO token in production; dev token only when `AUTH_MODE=development`.)*

---

## 9. Object storage — Cloudflare R2 or AWS S3

Used for uploaded documents (TCA-007). Without config, files store locally in the API container (ephemeral on Render — **not for production**).

### Cloudflare R2 (recommended — no egress fees)

1. Cloudflare Dashboard → **R2** → Create bucket `audira-artifacts`
2. Create **API token** with Object Read & Write
3. Note: Account ID, Access Key, Secret Key, endpoint `https://<accountid>.r2.cloudflarestorage.com`

On Render API:

```env
OBJECT_STORAGE_ENDPOINT=https://<accountid>.r2.cloudflarestorage.com
OBJECT_STORAGE_BUCKET=audira-artifacts
OBJECT_STORAGE_ACCESS_KEY=<key>
OBJECT_STORAGE_SECRET_KEY=<secret>
```

### AWS S3

```env
OBJECT_STORAGE_ENDPOINT=https://s3.ap-south-1.amazonaws.com
OBJECT_STORAGE_BUCKET=audira-artifacts-prod
OBJECT_STORAGE_ACCESS_KEY=<key>
OBJECT_STORAGE_SECRET_KEY=<secret>
```

Pick region to match residency policy (§13).

---

## 10. WorkOS — Enterprise SSO & SCIM

### 10.1 WorkOS project setup

1. [dashboard.workos.com](https://dashboard.workos.com) → Create project
2. Enable **AuthKit** / SSO
3. Configure **Redirect URI**:

```
https://audira-api.onrender.com/auth/callback
```

**Important:** Redirect goes to **Render API**, not Vercel. The API sets a JWT and redirects the browser to Vercel.

4. Copy **API Key** and **Client ID**

### 10.2 Render API env (production auth)

```env
AUTH_MODE=workos
WORKOS_API_KEY=sk_...
WORKOS_CLIENT_ID=client_...
WORKOS_REDIRECT_URI=https://audira-api.onrender.com/auth/callback
WORKOS_WEBHOOK_SECRET=<from WorkOS webhooks>
WEB_APP_URL=https://your-app.vercel.app
JWT_SECRET=<strong-random-secret>
```

### 10.3 SCIM provisioning (optional)

1. WorkOS → Directory Sync → configure IdP (Okta, Azure AD, etc.)
2. Set webhook URL on WorkOS:

```
https://audira-api.onrender.com/webhooks/workos/directory
```

3. Events create/update users and roles in Postgres

### 10.4 Auth flow diagram

```
User → Vercel /login
     → clicks Sign in
     → Render GET /auth/login
     → WorkOS hosted login
     → Render GET /auth/callback?code=...
     → API creates JWT, redirects to Vercel /auth/callback?token=...
     → Vercel stores audira_session cookie
     → Subsequent API calls: Authorization: Bearer <jwt>
```

### 10.5 Development auth (no WorkOS)

Keep `AUTH_MODE=development` on Render. Use dev login on Vercel `/login?dev=1` or:

```
Authorization: Bearer dev:email@company.com:comms_manager
```

Roles: `owner`, `admin`, `comms_manager`, `brand_manager`, etc. (see `services/api/app/auth/roles.py`).

---

## 11. Environment variables reference

### Vercel (`apps/web`)

| Variable | Required | Description |
|---|---|---|
| `NEXT_PUBLIC_API_URL` | ✅ | Render API base URL |

### Render API (`services/api`)

| Variable | Required | Description |
|---|---|---|
| `DATABASE_URL` | ✅ | `postgresql+asyncpg://...` |
| `REDIS_URL` | ✅ | Redis connection URL |
| `JWT_SECRET` | ✅ | Min 32 chars; signs session tokens |
| `WEB_APP_URL` | ✅ | Vercel URL (post-login redirect) |
| `CORS_ORIGINS` | ✅ | JSON array, e.g. `["https://app.example.com"]` |
| `AUTH_MODE` | ✅ | `development` or `workos` |
| `ENVIRONMENT` | ✅ | `production` — enables licence checks |
| `WORKOS_API_KEY` | SSO | WorkOS secret key |
| `WORKOS_CLIENT_ID` | SSO | WorkOS client ID |
| `WORKOS_REDIRECT_URI` | SSO | `https://<api>/auth/callback` |
| `WORKOS_WEBHOOK_SECRET` | SCIM | Webhook signature verification |
| `INFERENCE_BASE_URL` | GPU | GPU service URL; empty = mock inference |
| `INFERENCE_API_KEY` | GPU | Shared secret with GPU tier |
| `INFERENCE_MONTHLY_COST_CAP_USD` | Optional | Default `500` |
| `OBJECT_STORAGE_ENDPOINT` | Storage | R2/S3 endpoint |
| `OBJECT_STORAGE_BUCKET` | Storage | Bucket name |
| `OBJECT_STORAGE_ACCESS_KEY` | Storage | Access key |
| `OBJECT_STORAGE_SECRET_KEY` | Storage | Secret key |
| `SENTRY_DSN` | Optional | Error tracking |
| `OTEL_EXPORTER_OTLP_ENDPOINT` | Optional | OpenTelemetry collector |

### Render Worker (`services/worker`)

Same as API for: `DATABASE_URL`, `REDIS_URL`, `INFERENCE_BASE_URL`, `INFERENCE_API_KEY`, `INFERENCE_MONTHLY_COST_CAP_USD`.

### GPU service (`services/inference/tribev2`)

| Variable | Required | Description |
|---|---|---|
| `HF_TOKEN` | ✅ | Hugging Face token |
| `INFERENCE_API_KEY` | ✅ | Must match Render |
| `TRIBE_CACHE_DIR` | Optional | Model weight cache path |

---

## 12. URL wiring & auth flow

### Production URL map

| Purpose | URL |
|---|---|
| Frontend | `https://app.yourcompany.com` (Vercel) |
| API | `https://api.yourcompany.com` (Render — optional custom domain) |
| WorkOS redirect | `https://api.yourcompany.com/auth/callback` |
| GPU inference | `https://inference.internal.yourcompany.com` (private or IP-restricted) |
| R2 bucket | Private — no public URL required |

### Custom domains

**Vercel:** Project → Domains → `app.yourcompany.com`  
**Render:** Web Service → Settings → Custom Domains → `api.yourcompany.com`

Update all env vars and WorkOS redirect URIs when domains change.

---

## 13. Data residency (India / EU / Singapore)

Audira.run supports tenant-level residency metadata (TCA-068). **Platform choice must match policy.**

| Region code | Label | Render | Recommended cloud mapping |
|---|---|---|---|
| `IN` | India | ❌ No Render region | AWS `ap-south-1` (Mumbai) or Azure Central India |
| `EU` | European Union | ✅ Frankfurt area | Render EU + R2 EU jurisdiction |
| `SG` | Singapore / APAC | ✅ Singapore | Render Singapore + R2 APAC |

### India-specific deployment path

Render cannot pin data to India today. For strict **DPDP** residency:

1. **Frontend:** Vercel (edge) — confirm legal review for static assets
2. **API + DB:** AWS Mumbai (ECS/EKS + RDS Postgres) or Azure India — same Docker images
3. **GPU:** AWS `ap-south-1` g5 instance
4. **Storage:** S3 bucket in `ap-south-1`

Use Render Singapore only when **contractual residency allows APAC** with Singapore as processing hub.

Tenant residency is configured via API:

```http
GET  /tenant/residency
PATCH /tenant/residency
```

---

## 14. Local development

### Quick start (no GPU)

```bash
# Terminal 1 — infrastructure + API + worker
docker compose up -d

# Terminal 2 — frontend
npm ci
npm run dev:web
```

| Service | URL |
|---|---|
| Web | http://localhost:3000 |
| API | http://localhost:8000 |
| API docs | http://localhost:8000/docs |
| Postgres | localhost:5432 |
| Redis | localhost:6379 |

Copy `.env.example` → `.env` at repo root for local overrides.

### Local with GPU

```bash
cd services/inference/tribev2
pip install -r requirements.txt
hf auth login   # `huggingface-cli` is deprecated; use `hf`
uvicorn main:app --port 8080
```

Set on API container / `.env`:
```
INFERENCE_BASE_URL=http://host.docker.internal:8080
```

### Run tests

```bash
pip install -r requirements.txt
pytest services/api/tests -q
npm run test:web
npm run build:web
```

---

## 15. Office add-ins (Word / PowerPoint)

**Status:** Manifest scaffold at `apps/addins/word/manifest.xml` (TCA-048 partial).

### Deployment steps

1. Host task pane URL on Vercel (`/analyze` or dedicated add-in page)
2. Update manifest `SourceLocation` to your Vercel URL
3. Deploy manifest via **Microsoft 365 Admin Center** → Integrated apps (centralized deployment)
4. Add-in calls Render API: `POST /features/addin/analyze` (proxies to `/analyze`)

SSO: add-ins use same WorkOS session — implement Office SSO → exchange for Audira.run JWT (Phase 2).

---

## 16. Observability & operations

### Health checks

| Service | Endpoint |
|---|---|
| API | `GET /health` |
| GPU | `GET /health` |
| Detailed (admin) | `GET /observability/health-detail` |

### Logs

- **Render:** Dashboard → Service → Logs (API + worker)
- **Vercel:** Dashboard → Deployments → Function logs
- **GPU host:** Provider-specific (Modal/RunPod/CloudWatch)

### Error tracking (optional)

Set `SENTRY_DSN` on Render API. Initialize Sentry SDK in API startup (future hardening).

### Audit log

`GET /admin/audit` — requires `audit.view` permission (admin/security roles).

### Backups

- **Render Postgres:** enable automatic backups on paid plans
- **R2/S3:** enable versioning for artifact retention policies

### Scaling triggers

| Symptom | Action |
|---|---|
| Slow analysis queue | Scale Render worker instances |
| API latency | Scale API web service tier |
| GPU queue depth | Add GPU replicas / larger GPU |
| DB connections | Upgrade Postgres plan; add connection pooling (PgBouncer) |

---

## 17. Production checklist

### Before go-live

- [ ] `AUTH_MODE=workos` with WorkOS redirect URI exact match
- [ ] `JWT_SECRET` rotated (32+ random chars, not default)
- [ ] `DATABASE_URL` uses `postgresql+asyncpg://`
- [ ] pgvector extension enabled
- [ ] `CORS_ORIGINS` lists only your Vercel domain(s)
- [ ] `WEB_APP_URL` matches Vercel production URL
- [ ] R2/S3 configured (uploads persist)
- [ ] Redis + worker running (inference jobs process)
- [ ] GPU tier tested OR consciously using fast-lane-only (`INFERENCE_BASE_URL` empty)
- [ ] TRIBE v2 licence reviewed for commercial use (TCA-016)
- [ ] `ENVIRONMENT=production` set
- [ ] Custom domains + TLS verified
- [ ] Smoke test: login → analyze → inference job → audit log

### Security

- [ ] No secrets in GitHub repo
- [ ] Render env vars marked secret
- [ ] GPU endpoint IP-restricted or mTLS where possible
- [ ] `INFERENCE_API_KEY` shared only between API/worker/GPU
- [ ] WorkOS webhook secret configured

---

## 18. Troubleshooting

| Problem | Likely cause | Fix |
|---|---|---|
| CORS error in browser | `CORS_ORIGINS` missing Vercel URL | Add exact origin including `https://` |
| SSO redirect loop | `WORKOS_REDIRECT_URI` mismatch | Must match WorkOS dashboard exactly |
| SSO lands on wrong site | `WEB_APP_URL` wrong | Set to Vercel URL |
| `Invalid dev token` in prod | `AUTH_MODE=development` left on | Switch to `workos` |
| DB connection errors | Wrong URL scheme | Use `postgresql+asyncpg://` |
| Inference jobs stuck queued | Worker not running / Redis wrong | Check worker logs + `REDIS_URL` |
| Mock inference only | `INFERENCE_BASE_URL` empty | Deploy GPU + set URL |
| GPU 401 | `INFERENCE_API_KEY` mismatch | Sync keys across services |
| GPU 503 tribev2 not installed | GPU image missing deps | Rebuild tribev2 Dockerfile with CUDA |
| Uploads disappear on redeploy | No object storage | Configure R2/S3 |
| pgvector errors | Extension not created | Run `CREATE EXTENSION vector;` |
| Cold start 50s+ | Render free tier | Upgrade to paid always-on |
| India residency audit fail | Data on US/EU Render | Migrate to AWS Mumbai stack |

---

## 19. Cost planning (indicative)

| Service | Pilot / mo | Production / mo |
|---|---|---|
| Vercel Pro | $20 | $20–150 |
| Render API (Starter) | $7 | $25–85 |
| Render Worker | $7 | $25–85 |
| Render Postgres | $7 | $20–90 |
| Render Redis | $10 | $10–32 |
| Cloudflare R2 | ~$1 | $5–50 (storage + ops) |
| WorkOS | Free tier → | $100+ (enterprise SSO) |
| GPU (RunPod A10) | ~$50–200 | $200–2000+ (usage) |
| **Total (ex-GPU)** | **~$50–100** | **~$200–500** |
| **With GPU neuro** | **~$150–400** | **~$500–3000+** |

Fast-lane text analysis (`full_analysis: false`) avoids GPU cost during pilots.

---

## 20. Alternative & future targets

### Same Docker images, different hosts

| Target | Use case |
|---|---|
| **AWS ECS/Fargate** | India residency, enterprise standard |
| **Azure Container Apps** | Microsoft-centric enterprises |
| **Kubernetes (Helm)** | On-prem, air-gapped (TCA-069) |
| **Fly.io / Railway** | Alternative to Render |

### What stays the same

- FastAPI API contract (`/docs` OpenAPI)
- Arq worker job format
- GPU `POST /v1/inference` contract
- Postgres schema (migrations via SQLAlchemy `create_all` today — add Alembic for production)

---

## Quick reference — copy/paste deploy commands

```bash
# Clone
git clone https://github.com/navendubrajesh/Audira.git
cd Audira

# Local
docker compose up -d
npm ci && npm run dev:web

# Test
pytest services/api/tests -q
npm run build:web

# Build API image locally (same as Render)
docker build -f services/api/Dockerfile -t audira-api .
docker build -f services/worker/Dockerfile -t audira-worker .
```

---

## Related docs

- [DEPLOYMENT.md](./DEPLOYMENT.md) — short overview
- [TECHNOLOGY_BASELINE.md](./TECHNOLOGY_BASELINE.md) — stack decisions
- [TRIBE_V2.md](./TRIBE_V2.md) — GPU model setup
- [GUARDRAILS.md](./GUARDRAILS.md) — stories requiring sign-off before enable
- [.env.example](../.env.example) — environment template

---

*For deployment support, verify each section against your Render/Vercel dashboards after any platform UI changes.*
