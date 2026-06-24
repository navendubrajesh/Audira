# TCA-072 — BM Copy

## Job status labels

| Status | Label |
|---|---|
| `queued` | Queued |
| `running` | Running analysis |
| `completed` | Complete |
| `failed` | Failed |
| `cached` | Retrieved from cache |

## SLA messages

| Key | Copy |
|---|---|
| `sla.within` | Completed within target latency |
| `sla.breach` | Completed outside target latency — flagged for review |
| `sla.text_target` | Text analysis target: under 2 seconds |
| `sla.multimodal_target` | Full analysis target: under 60 seconds |

## Cost messages

| Key | Copy |
|---|---|
| `cost.cap_exceeded` | Your organisation has reached its monthly inference budget. Contact your administrator to increase the limit. |
| `cost.per_job` | Estimated cost: {amount} |

## Batch

| Key | Copy |
|---|---|
| `batch.submitted` | {count} analyses queued |
| `batch.progress` | {completed} of {total} complete |

## Hand-off → UXD

Async pattern: submit → progress indicator → result card with latency badge and cost line.
