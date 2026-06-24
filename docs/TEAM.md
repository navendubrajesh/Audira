# Team Mandates & Hand-offs

Each role produces **one concrete artifact per story** and hands off explicitly to the next step in the 10-step loop.

| Role | Mandate | Artifact per story | Hands off to |
|---|---|---|---|
| **Enterprise Architect (EA)** | Architecture stack, module boundaries, API contracts, infra/deployment, model-abstraction interfaces | `docs/stories/{TCA-ID}/01-ea-design.md` — component diagram, API schema, data touchpoints, tech notes mapped to AC | Brand Manager |
| **Brand Manager (BM)** | Brand voice, product copy, terminology, compliance-facing language | `docs/stories/{TCA-ID}/02-bm-copy.md` — UI strings, error messages, report labels, glossary deltas | UX/UI Designer |
| **UX/UI Designer (UXD)** | Experience flows, wireframes, component specs, accessibility (WCAG 2.2 AA) | `docs/stories/{TCA-ID}/03-uxd-spec.md` — screen states, interaction notes, component mapping to design system | Full-Stack Developer |
| **Full-Stack Developer (FSD)** | Implementation across web + API + worker as scoped by EA design | Code + `docs/stories/{TCA-ID}/04-fsd-implementation.md` — files changed, env vars, migration notes | Tests (self) |
| **QA gate** (FSD + checklist) | AC verification, NFR spot-checks, accessibility smoke | `docs/stories/{TCA-ID}/05-qa-report.md` — AC checklist with pass/fail evidence | Document & trace |
| **Document & trace** (all) | Ledger update, FR↔TCA traceability | `docs/ledger/PROGRESS_LEDGER.md` entry + story folder complete | Commit → Report |

---

## Standing baselines (decided once)

| Baseline | Owner | Document |
|---|---|---|
| Technology stack | EA | [`TECHNOLOGY_BASELINE.md`](./TECHNOLOGY_BASELINE.md) |
| Design system & brand tokens | BM + UXD | [`packages/design-tokens/`](../packages/design-tokens/) + future shadcn/ui catalogue |
| Backlog & build order | PM/lead | [`data/backlog.json`](../data/backlog.json), [`BUILD_ORDER.md`](./BUILD_ORDER.md) |
| Definition of Done | All | [`DEFINITION_OF_DONE.md`](./DEFINITION_OF_DONE.md) |

---

## Tech Note column

The backlog v1.1 workbook does **not** include a separate "Android Tech Note" column — the reference stack is embedded in acceptance criteria (see Read Me sheet). For each story, the EA design artifact must extract platform-specific implementation notes from the AC and map them to the standing baseline above.
