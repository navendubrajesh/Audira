# TCA-072 — EA Design

**Story:** Scalable inference architecture  
**FR:** FR-E18-1  
**Depends on:** TCA-067 (auth)

## Acceptance criteria mapping

| AC | Implementation |
|---|---|
| GPU inference on dedicated tier | `HttpGpuInferenceProvider` calls decoupled `INFERENCE_BASE_URL`; app/worker never run models locally |
| Queue + batch | Arq + Redis; `POST /inference/jobs`, `POST /inference/batches`; worker `run_inference_job` |
| Latency SLA targets | NFR-01: text p95 < 2s, multimodal p95 < 60s; `sla.py` flags breaches on job completion |
| Cost tracked & capped | `cost_usd` per job; tenant monthly cap via `INFERENCE_MONTHLY_COST_CAP_USD`; reject when exceeded |

## Architecture

```
Client → POST /inference/jobs → API (auth) → Postgres job row → Arq enqueue
                                              ↓
Worker ← Redis queue ← run_inference_job → GpuProvider (Modal/etc.)
                                              ↓
Client ← GET /inference/jobs/{id} ← status + result + latency + cost
```

## API contracts

| Method | Path | Purpose |
|---|---|---|
| POST | `/inference/jobs` | Submit single job (returns job_id, poll URL) |
| POST | `/inference/batches` | Submit batch (list of payloads) |
| GET | `/inference/jobs/{id}` | Poll status, latency, SLA, cost |
| GET | `/inference/batches/{id}` | Batch aggregate status |
| GET | `/inference/metrics` | Admin: SLA + cost rollup |

## Caching

Identical `payload_hash` within tenant returns completed cached job (NFR-13).

## Hand-off → BM

Job status labels, SLA breach copy, cost-cap error message.
