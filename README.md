# Resonode

**Enterprise Communications Neuro-Analyzer** — pre-send, neuro-grounded analysis for IT-services organisations.

Phase 0 bootstrap complete. Story delivery follows the [10-step workflow](docs/WORKFLOW.md).

## Quick start

### Prerequisites

- Node.js ≥ 20
- Python ≥ 3.12
- Docker (optional, for full stack)

### Local development

```bash
# Install JS dependencies
npm install

# Install Python dependencies
pip install -r requirements.txt

# Start infrastructure + API + worker
docker compose up -d

# Start web app
npm run dev:web
```

- Web: http://localhost:3000  
- API: http://localhost:8000  
- API docs: http://localhost:8000/docs  

### Backlog

```bash
python scripts/parse_backlog.py
```

Source: `Enterprise_Comms_NeuroAnalyzer_Competitive_Backlog_1.xlsx`  
Output: `data/backlog.json`, `docs/BUILD_ORDER.md`

### Tests

```bash
# API
cd services/api && pytest

# Web
npm run test:web
```

## Repository layout

| Path | Purpose |
|---|---|
| `apps/web` | Communications Studio (Next.js on Vercel) |
| `apps/addins` | Office.js add-ins |
| `services/api` | FastAPI orchestration (Render) |
| `services/worker` | Arq async jobs |
| `packages/design-tokens` | Brand & design baseline |
| `docs/` | Workflow, ledger, per-story artifacts |

## Key docs

- [Technology baseline](docs/TECHNOLOGY_BASELINE.md) — standing stack decision
- [Team & hand-offs](docs/TEAM.md)
- [Build order](docs/BUILD_ORDER.md)
- [Progress ledger](docs/ledger/PROGRESS_LEDGER.md)

## Status

**Paused after Phase 0.** Next story: **TCA-067** (Enterprise SSO & RBAC) — awaiting go-ahead.
