# TCA-072 — FSD Implementation

## Summary

Decoupled GPU inference via Arq queue + shared `audira_core` provider abstraction.

## Key paths

| Area | Files |
|---|---|
| Shared core | `services/shared/audira_core/inference/`, `process_job.py`, `sla.py`, `cost.py` |
| API | `app/models/inference_job.py`, `app/services/inference_service.py`, `app/routers/inference.py` |
| Worker | `worker/tasks.py`, `worker/job_processor.py` |
| Web | `components/inference/*`, home page panel |

## Env vars

`INFERENCE_BASE_URL`, `INFERENCE_API_KEY`, `INFERENCE_MONTHLY_COST_CAP_USD`

## Hand-off → QA

12 API tests pass; manual: sign in → Run sample analysis on home page.
