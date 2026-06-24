# Guardrails

Guardrail stories implement **policy enforcement surfaces** — generative AI governance, regulated-claim detection, and guardrailed rewrites. They carry higher compliance, legal, and UX risk than feature stories.

## Guardrail story IDs

| ID | FR | Phase | Name |
|---|---|---|---|
| TCA-037 | FR-E08-4 | 2 | Generative-AI content governance |
| TCA-044 | FR-E10-3 | 3 | AI rewrite assist (guardrailed) |
| TCA-060 | FR-E15-2 | 2 | Regulated-claim & risk-language guardrails |

## Stop rule

When the build queue reaches any guardrail story:

1. **Pause** the 10-step loop before EA design.
2. Confirm all prerequisite stories in the same phase are `done`.
3. Obtain **explicit stakeholder go-ahead** (legal/compliance review where applicable).
4. Document the approval in `docs/ledger/PROGRESS_LEDGER.md` under a "Guardrail approvals" section.

Do not implement guardrail enforcement logic speculatively ahead of the queue.

## Implementation constraints (apply when approved)

- Human-in-the-loop required for AI rewrites (TCA-044 AC).
- All guardrail decisions **logged** to append-only audit store (FR-E16-5).
- Block/warn behaviour must be **configurable per tenant** (quality gates — FR-E13-2).
- UI copy must position outputs as **decision support**, not guaranteed outcomes (PRD §14).

## Non-guardrail but related

These are compliance foundations, not guardrail pauses:

- TCA-061 — DPDP/GDPR consent & PII (Phase 1 Must)
- TCA-070 — No-training guarantee (Phase 1 Must)
- TCA-052 — Quality gates / score thresholds (Phase 2)
