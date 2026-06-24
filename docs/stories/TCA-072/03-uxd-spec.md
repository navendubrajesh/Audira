# TCA-072 — UXD Spec

## Inference demo panel (home page, authenticated)

Collapsible "Analysis queue" section below hero:

1. **Submit** — dropdown modality (text / multimodal) + "Run sample analysis" button
2. **Progress** — status pill (Queued → Running → Complete) + optional spinner
3. **Result card** — when complete:
   - Latency badge (green if within SLA, amber if breach)
   - Cost line (small, neutral-500)
   - "Cached result" badge if served from cache

## Components

- `InferenceDemo` — client component with poll loop (2s interval, max 60s)
- `JobStatusBadge` — maps status → colour variant
- `SlaBadge` — within/breach

## Hand-off → FSD

No dedicated route required — embed on `/` for authenticated users only.
