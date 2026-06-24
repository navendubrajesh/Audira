# Repeatable 10-Step Story Loop

**Mission:** One story at a time. Backlog is law. Foundation before features. Honour Acceptance Criteria. Stop at guardrails.

```
Select → EA design → BM copy → UXD experience → FSD build → Tests → QA gate → Document & trace → Commit → Report & continue
```

| Step | Action | Owner | Output |
|---:|---|---|---|
| 1 | **Select** next story from [`BUILD_ORDER.md`](./BUILD_ORDER.md) where all dependencies are `done` | Lead | Story ID confirmed; guardrail check |
| 2 | **EA design** — architecture, contracts, dependencies | EA | `docs/stories/{ID}/01-ea-design.md` |
| 3 | **BM copy** — strings, terminology, compliance language | BM | `docs/stories/{ID}/02-bm-copy.md` |
| 4 | **UXD experience** — flows, wireframes, a11y | UXD | `docs/stories/{ID}/03-uxd-spec.md` |
| 5 | **FSD build** — implement per EA+UXD; honour AC | FSD | Code + `04-fsd-implementation.md` |
| 6 | **Tests** — unit/integration; golden-set if mapping layer touched | FSD | Passing CI |
| 7 | **QA gate** — AC demonstrably met; NFR spot-check | FSD | `05-qa-report.md` |
| 8 | **Document & trace** — update ledger, link FR↔TCA | All | Ledger entry |
| 9 | **Commit** — only when user requests or pipeline policy allows | FSD | Git commit |
| 10 | **Report & continue** — summary to stakeholder; loop to step 1 | Lead | Status report |

---

## Ordering rules (when selecting)

1. **Phase** — Phase 1 → 2 → 3  
2. **Type** — Foundation → Parity → Differentiator  
3. **Priority** — Must → Should → Could  
4. **Epic sequence** — E18 → E17 → E01 → E02 → E03 → metrics → integrations  
5. **Dependencies** — see `dependencies` in [`data/backlog.json`](../data/backlog.json)

Recompute order after backlog changes:

```bash
python scripts/parse_backlog.py
```

---

## Guardrail pause

When the queue reaches a **guardrail story**, stop the loop and obtain explicit go-ahead before step 2:

| ID | Story |
|---|---|
| TCA-037 | Generative-AI content governance |
| TCA-044 | AI rewrite assist (guardrailed) |
| TCA-060 | Regulated-claim & risk-language guardrails |

See [`GUARDRAILS.md`](./GUARDRAILS.md).

---

## Phase 0 status

| Item | Status |
|---|---|
| Parse Excel backlog | ✅ Done |
| Compute build order | ✅ Done |
| Scaffold monorepo | ✅ Done |
| Design tokens baseline | ✅ Done |
| Docker + CI | ✅ Done |
| Docs / ledger | ✅ Done |
| **First story (TCA-067)** | ⏸ Paused — awaiting go-ahead |
