# Audira.run — Deployment Setup (Step-by-Step)

**Product:** [Audira.run](https://audira.run) — Enterprise Communications Neuro-Analyzer  
**Repo:** [github.com/navendubrajesh/Audira](https://github.com/navendubrajesh/Audira)

Use this checklist to go from zero to a live pilot. Full reference: [DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md).

---

## Target production URLs

| Service | URL | Platform |
|---|---|---|
| **Web app** | `https://audira.run` | Vercel |
| **API** | `https://api.audira.run` | Render (custom domain) |
| **API (Render default)** | `https://audira-api.onrender.com` | Use until DNS is ready |
| **WorkOS callback** | `https://api.audira.run/auth/callback` | Must hit API, not Vercel |
| **GPU inference** | `https://inference.audira.run` (private) | RunPod / Modal / AWS |

---

## Before you start

1. Register **audira.run** on your domain registrar.
2. Create accounts: [Render](https://render.com), [Vercel](https://vercel.com).
3. Connect both to GitHub repo **`navendubrajesh/Audira`**, branch **`main`**.

**Pilot shortcuts:** skip GPU (fast analysis only), skip WorkOS (`AUTH_MODE=development`), skip R2 (uploads won’t persist).

---

## Step 1 — Render: PostgreSQL

1. Render → **New +** → **PostgreSQL**
2. Name: **`audira-db`**
3. Region: **Singapore** (APAC) or **Frankfurt** (EU)
4. Create → copy **Internal Database URL**
5. Convert URL:

```
postgres://...  →  postgresql+asyncpg://...
```

6. Shell tab (or `psql`):

```sql
CREATE EXTENSION IF NOT EXISTS vector;
```

Save as **`DATABASE_URL`**.

---

## Step 2 — Render: Redis

1. **New +** → **Key Value**
2. Name: **`audira-redis`**
3. Same region as Postgres
4. Copy **Internal Redis URL** → **`REDIS_URL`**

---

## Step 3 — Render: API

1. **New +** → **Web Service** → connect **Audira** repo
2. Settings:

| Field | Value |
|---|---|
| Name | `audira-api` |
| Runtime | Docker |
| Dockerfile | `services/api/Dockerfile` |
| Docker context | `.` |
| Health check | `/health` |

3. Environment variables:

```env
DATABASE_URL=postgresql+asyncpg://...
REDIS_URL=redis://...
AUTH_MODE=development
JWT_SECRET=<40-random-chars>
WEB_APP_URL=https://audira.run
CORS_ORIGINS=["https://audira.run"]
ENVIRONMENT=production
INFERENCE_BASE_URL=
```

4. Deploy → note URL: `https://audira-api.onrender.com`
5. Test: `https://audira-api.onrender.com/health`

---

## Step 4 — Render: Worker

1. **New +** → **Background Worker**
2. Dockerfile: `services/worker/Dockerfile`, context `.`
3. Name: **`audira-worker`**
4. Same `DATABASE_URL`, `REDIS_URL`, `INFERENCE_BASE_URL` as API
5. Check logs for successful Arq startup

---

## Step 5 — Vercel: Frontend

1. [vercel.com/new](https://vercel.com/new) → Import **Audira**
2. Root directory: **`apps/web`**
3. Install (monorepo): `cd ../.. && npm ci`
4. Build: `cd ../.. && npm run build:web`
5. Environment:

```env
NEXT_PUBLIC_API_URL=https://audira-api.onrender.com
```

(Use `https://api.audira.run` after Step 7.)

6. Deploy → confirm `https://audira.run` or `*.vercel.app` works

---

## Step 6 — Wire web ↔ API

On **Render → audira-api → Environment**:

```env
WEB_APP_URL=https://audira.run
CORS_ORIGINS=["https://audira.run"]
```

Redeploy API.

**Smoke test:**

1. Open `https://audira.run/login?dev=1`
2. Dev login → **Analyze** → run fast analysis
3. API docs: `https://audira-api.onrender.com/docs`

---

## Step 7 — Custom domains (recommended)

### Vercel — audira.run

1. Vercel → Project → **Domains** → add `audira.run` and `www.audira.run`
2. Add DNS records at your registrar (Vercel shows exact values)

### Render — api.audira.run

1. Render → **audira-api** → **Settings → Custom Domains**
2. Add `api.audira.run`
3. Add CNAME at registrar per Render instructions
4. Update env everywhere:

| Where | Variable | Value |
|---|---|---|
| Vercel | `NEXT_PUBLIC_API_URL` | `https://api.audira.run` |
| Render API | `WORKOS_REDIRECT_URI` | `https://api.audira.run/auth/callback` |
| WorkOS dashboard | Redirect URI | same |

---

## Step 8 — WorkOS SSO (when ready)

1. [workos.com](https://workos.com) → create project
2. Redirect URI: **`https://api.audira.run/auth/callback`**
3. On Render API:

```env
AUTH_MODE=workos
WORKOS_API_KEY=sk_...
WORKOS_CLIENT_ID=client_...
WORKOS_REDIRECT_URI=https://api.audira.run/auth/callback
WORKOS_WEBHOOK_SECRET=...
```

4. Test: `https://audira.run/login` → organisation SSO

---

## Step 9 — Object storage (uploads)

**Cloudflare R2** bucket `audira-artifacts`:

```env
OBJECT_STORAGE_ENDPOINT=https://<accountid>.r2.cloudflarestorage.com
OBJECT_STORAGE_BUCKET=audira-artifacts
OBJECT_STORAGE_ACCESS_KEY=...
OBJECT_STORAGE_SECRET_KEY=...
```

Set on Render **audira-api** only.

---

## Step 10 — GPU inference (optional)

Deploy `services/inference/tribev2` on RunPod/Modal, then:

```env
INFERENCE_BASE_URL=https://inference.audira.run
INFERENCE_API_KEY=<shared-secret>
```

Set on **audira-api** and **audira-worker**. Same key on GPU service.

Without this, **Audira.run fast analysis** still works; full neuro path uses stub metrics.

---

## Quick reference — service names on Render

| Render service | Purpose |
|---|---|
| `audira-db` | PostgreSQL + pgvector |
| `audira-redis` | Queue + cache |
| `audira-api` | FastAPI |
| `audira-worker` | Arq jobs |

---

## Troubleshooting

| Issue | Fix |
|---|---|
| CORS error | `CORS_ORIGINS` must include `https://audira.run` exactly |
| SSO redirect fails | WorkOS URI must match `api.audira.run/auth/callback` |
| DB errors | Use `postgresql+asyncpg://` not `postgres://` |
| Login works locally only | Update `WEB_APP_URL` + Vercel domain |

See [DEPLOYMENT_GUIDE.md §18](./DEPLOYMENT_GUIDE.md#18-troubleshooting) for more.

---

## Local development (Audira.run codebase)

```bash
docker compose up -d
npm ci && npm run dev:web
```

- Web: http://localhost:3000  
- API: http://localhost:8000/docs  

Default dev login: `admin@audira.run` on `/login?dev=1`
