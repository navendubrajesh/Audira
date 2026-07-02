# Backlog Audit — 2026-06-24

## Summary

| Category | Count |
|---|---|
| Fully implemented (AC met for MVP) | ~18 |
| Partial (core path + known gaps) | ~40 |
| Guardrails (correctly pending) | 3 |
| Stub / future phase | ~15 |

## Fixes applied in this audit

- **TCA-003 / TCA-038:** Objective-weighted composite + pass/needs-work verdict
- **TCA-004:** Artifact-type `checks` drive which scorers run
- **TCA-005:** Standards rollback endpoint; jargon rules from standards library
- **TCA-007:** Document parser (txt/md/docx/pdf/pptx) + blob storage key
- **TCA-008:** Fast lane skips GPU; upgrade via `full_analysis`
- **TCA-020:** Attention heatmap grid + SVG export in results
- **TCA-024 / TCA-027 / TCA-029 / TCA-031:** Sentence flags, structure scorer, enhanced jargon/readability
- **TCA-019:** Rerun endpoint for reproducibility
- **TCA-040:** Variant compare endpoint
- **TCA-052:** Quality gates endpoint
- **TCA-061 / TCA-071:** PII detect + optional redaction via privacy settings
- **TCA-016:** Production licence gate + CI script
- **TCA-048 / TCA-049:** Add-in route calls real analysis; Word manifest scaffold
- **TCA-039 / TCA-051 / TCA-045:** Analytics/campaigns/what-if backed by DB runs
- **TCA-064:** Bias check endpoint

## Still pending or partial

| ID | Gap |
|---|---|
| TCA-037, TCA-044, TCA-060 | Guardrails — require sign-off |
| TCA-048 | Full Office.js task pane UI (manifest only) |
| TCA-009–011, TCA-021–026 | AV/video/image pipelines |
| TCA-010 | URL/HTML capture |
| TCA-050 | Published SDK package |
| TCA-068 / TCA-072 | Production region routing + GPU autoscale |

## Backlog status

Stories marked `partial` in `data/backlog.json` reflect MVP delivery with documented gaps. Guardrails remain `pending`.
