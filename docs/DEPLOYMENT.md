# Deployment — GitHub repo vs runtime hosts

Your code lives in one GitHub repo: [github.com/navendubrajesh/Audira](https://github.com/navendubrajesh/Audira).

**GitHub stores and builds code. It does not run your production frontend + backend together.**

> **Step-by-step setup:** [DEPLOY_SETUP.md](./DEPLOY_SETUP.md) — Audira.run domains, Render service names, env vars.  
> **Full reference:** [DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md)

## What GitHub gives you

| Capability | Frontend | Backend API | TRIBE v2 GPU |
|---|---|---|---|
| **Git repo (monorepo)** | ✅ `apps/web` | ✅ `services/api` | ✅ `services/inference/tribev2` |
| **GitHub Actions CI** | ✅ lint/build/test | ✅ pytest | ❌ no GPU on standard runners |
| **GitHub Pages** | ⚠️ static export only | ❌ no Python/FastAPI | ❌ |
| **Runs 24/7 in production** | ❌ | ❌ | ❌ |

## Recommended: GitHub → connected hosts (all deploy from the same repo)

```
GitHub (Audira)
    │
    ├── push to main ──► Vercel          → apps/web          (Next.js frontend)
    │
    ├── push to main ──► Render          → services/api      (FastAPI orchestration)
    │                      Render          → services/worker   (Arq jobs)
    │                      Render Postgres + Redis
    │
    └── push / manual ──► Modal / RunPod  → services/inference/tribev2  (GPU + facebook/tribev2)
```

Every push to `main` can auto-deploy web + API if you connect the repo in Vercel and Render dashboards. The GPU tier is a **separate service** from the same repo.

## Environment wiring

| Service | Key env vars |
|---|---|
| **Vercel** (web @ audira.run) | `NEXT_PUBLIC_API_URL=https://api.audira.run` |
| **Render** (api) | `WEB_APP_URL=https://audira.run`, `CORS_ORIGINS=["https://audira.run"]` |
| **Render** (api) | `INFERENCE_BASE_URL=https://inference.audira.run` |
| **Render** (api) | `INFERENCE_API_KEY=…` |
| **GPU tier** | `HF_TOKEN=…` (Hugging Face — LLaMA 3.2 is gated) |
| **GPU tier** | `INFERENCE_API_KEY=…` (must match API) |

Set `INFERENCE_BASE_URL` on Render to point at your TRIBE v2 service. The API/worker call `POST /v1/inference` — already implemented in `HttpGpuProvider`.

## Local development

```bash
docker compose up -d          # Postgres, Redis, API, worker (no GPU)
npm run dev:web                 # Frontend at :3000
```

Without a GPU, jobs use the **mock provider** (stub metrics). To test real TRIBE v2 locally you need a CUDA machine and:

```bash
cd services/inference/tribev2
hf auth login                   # required for LLaMA 3.2 encoder (`huggingface-cli` is deprecated)
pip install -r requirements.txt
# pip install tribev2 per https://huggingface.co/facebook/tribev2
uvicorn main:app --port 8080
```

Then set `INFERENCE_BASE_URL=http://localhost:8080` on the API.

## Can everything be "on GitHub"?

- **All source code:** yes — already in one repo.
- **Both running in production on GitHub alone:** no — use Vercel + Render (+ GPU host) connected to the repo.
- **Free tier only:** Vercel hobby + Render free may work for demos; TRIBE v2 needs a **paid GPU** instance (Modal, RunPod, etc.).

See also [docs/TRIBE_V2.md](./TRIBE_V2.md) and [docs/TECHNOLOGY_BASELINE.md](./TECHNOLOGY_BASELINE.md).
