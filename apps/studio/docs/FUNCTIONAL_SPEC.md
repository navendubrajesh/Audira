# Audira Studio — Functional Specification

**Version:** 1.0 (greenfield scaffold)  
**Backlog:** 92 user stories (`TCA-001`…`TCA-092`), epics `E01`–`E22`  
**Status legend:** Done · Partial · To Do (visible on every feature card)

---

## 1. Product Generalisation — Four Verticals

The backlog is authored around enterprise communications and LinkedIn technical content. **The same capability patterns apply per channel:**

| Capability pattern | Backlog anchor | Social | LinkedIn | Placement | Blog |
|--------------------|----------------|--------|----------|-----------|------|
| Audience & objective context | E01 | Campaign audience tags | Persona picker (TCA-077) | Hiring manager / candidate segment | Reader persona + SEO intent |
| Multimodal ingestion | E02, TCA-079 | Thumbnails, reels, carousels | Text + code + diagrams | JD attachments, employer brand assets | Hero images, embeds |
| Attention & saliency | E04 | Hook / first-3s, thumbnail heatmap | Diagram focal points | Job ad visual hierarchy | Header image saliency |
| Emotion & tone | E05 | Caption sentiment | Technical authority tone | Employer brand warmth | Narrative voice |
| Clarity & cognitive load | E06 | Caption readability | Structure & readability (TCA-085) | JD clarity, inclusive language (TCA-059) | Scannability, headings |
| Memorability | E07 | Hook recall | Key takeaway retention | Employer value prop recall | Key message findability |
| Brand voice governance | E08 | Platform-adapted voice | Anti-generic prompter (TCA-078) | Inclusive hiring language | Editorial style guide |
| Effectiveness scoring | E09, TCA-038 | Composite per post | 4-part matrix (TCA-083) | JD effectiveness score | SEO + readability composite |
| Rewrite & variants | E10, TCA-044 | Caption variants | AI rewrite assist | Applicant response drafts | Title/meta suggestions |
| Channel format rules | E11 | Per-platform specs | LinkedIn post limits | Board field mapping (Naukri, Indeed) | WordPress block rules |
| Workflow & approval | E13 | Social publish gate | Technical review gate | HR + compliance gate | Editorial gate |
| Analytics | E14 | Engagement vs prediction | Thought-leadership ROI | Application quality proxy | Traffic vs comprehension |
| Compliance guardrails | E15 | Brand safety | Comment tone guardrail (TCA-090) | Bias / inclusive language | PII / claims check |
| Model governance | E16 | Model cards per scorer | TRIBE v2 + open models (E03) | Same | Same |
| Security & residency | E17 | Tenant isolation | DPDP/GDPR notes in UI | Same | Same |

---

## 2. Vertical Feature Sets

### Social (Instagram, Facebook, TikTok, YouTube Shorts, X)
- Visual-first composer with platform format picker (E11)
- Attention / saliency & thumbnail scoring (E04, TCA-029)
- Hook / first-3-seconds analysis for video (E04)
- Hashtag & caption optimization (E10, E11)
- Scheduling queue with per-account rules
- **MVP (Phase 1 Must):** Compose + Analyze placeholders with mock scores
- **Later (Phase 2–3):** Real platform connectors, heatmap overlay

### LinkedIn (Technical Thought Leadership) — E19–E22 seed
- **TCA-077** Dynamic Target Persona Picker (Technical Peer, Engineering Leader, …)
- **TCA-078** Anti-Generic frictionless prompter wizard
- **TCA-079** Multimodal asset ingestion terminal
- **TCA-080–082** Text parser, visual reader, code checker (stubs)
- **TCA-083** Structured 4-part feedback matrix — **signature build**
- **TCA-084–086** Visual-text alignment, structure/readability, technical depth scorers
- **TCA-087** Real-time debounced feedback sidebar
- **TCA-091** Split-panel draft & feedback workspace — **signature build**
- **TCA-088–090** Engagement helper: relevance ranker, counter-perspective drafts, tone guardrail

### Placement / Recruitment (Naukri, Times Jobs, Monster, Indeed)
- JD / job-post composer with board-specific field mapping (E11)
- Inclusive-language & bias checks (E15, TCA-059)
- Clarity & readability (E06)
- Candidate-comms templates (E10)
- Applicant-response drafting stub
- **MVP:** Compose + Analyze with mock bias/clarity cards

### Blog (Medium, WordPress, personal blog)
- Long-form editor with structure analysis (E06)
- SEO / metadata panel (E11)
- Key-message findability & memorability (E07)
- Series management in context list
- **MVP:** Compose + Insights placeholders

---

## 3. MVP vs Later — Phase & Priority

| Tier | Rule | UI treatment |
|------|------|--------------|
| **MVP first-class** | Phase 1 + Must | Full placeholder screen, navigable tabs, mock data |
| **MVP secondary** | Phase 1 + Should/Could | Screen present, some tabs stubbed |
| **Scale** | Phase 2 | Feature card + "Phase 2" ribbon |
| **Advanced** | Phase 3 | "Coming soon" stub with story ID link |

Cross-cutting **Done** items (e.g. TCA-067 SSO, TCA-068 residency) render as **configured** governance notes, not fake live integrations.

---

## 4. Signature Feature — Structured 4-Part Feedback Matrix

**Stories:** TCA-083, TCA-091, TCA-087, TCA-077, TCA-078, TCA-079, TCA-080, TCA-084, TCA-085, TCA-086

### Layout (TCA-091)
- **Left panel (60%, resizable):** Draft editor with markdown toolbar stub (TCA-092)
- **Right panel (40%):** Live feedback stack

### Feedback card schema (TCA-083)
Each card displays:
1. **Category** — e.g. Technical Depth, Visual-Text Alignment, Structure, Authenticity
2. **Score** — x/10 with semantic colour chip
3. **Insight** — one-sentence diagnosis
4. **Recommended fix** — actionable suggestion

### Interactions
- **Debounced refresh (TCA-087):** 600ms after edit → mock rescore via `services/analyzer.ts`
- **Click card → highlight span** in editor (data attributes on mock ranges)
- **Composite header (TCA-038):** 0–100 gauge above panels
- **Persona picker (TCA-077):** Changes weighting copy on cards (mock)
- **Anti-generic wizard (TCA-078):** Modal pre-compose checklist
- **Multimodal drop zone (TCA-079):** Accepts image/code/diagram; routes to asset library
- **A/B compare (TCA-040):** Toggle between variant A/B in header
- **Rewrite assist (TCA-044):** Button opens stub panel with guardrail note

---

## 5. Traceability

Full table: [`ROADMAP.md`](../ROADMAP.md) (92 rows).

Sample rows:

| Story ID | Epic | Vertical(s) | Screen | Impl | Status |
|----------|------|-------------|--------|------|--------|
| TCA-083 | E21 | linkedin | `linkedin/AnalyzerWorkspace` | Real (placeholder logic) | To Do |
| TCA-091 | E21 | linkedin | `linkedin/AnalyzerWorkspace` | Real (placeholder logic) | To Do |
| TCA-077 | E19 | linkedin | `linkedin/PersonaPicker` | Real (placeholder logic) | To Do |
| TCA-059 | E15 | placement | `governance/GovernanceModule` | Placeholder (MVP) | Partial |
| TCA-038 | E09 | home, linkedin | `linkedin/AnalyzerWorkspace` | Placeholder (MVP) | Partial |
| TCA-014 | E14 | analytics | `analytics/InsightsConsole` | Placeholder (MVP) | Partial |

Every screen in the app maps to one or more story IDs via `FeatureCard` and `BacklogBadge` components.

---

## 6. Constraints (from Read Me & backlog)

| Constraint | UI surfacing |
|------------|--------------|
| Model-agnostic analyzer | No hardcoded vendor; "Model card" links in Governance |
| Engineering artifacts out of scope (TCA-004) | Upload rejection message in Asset Library |
| Non-commercial model licence flags | Governance note on inference settings |
| DPDP / GDPR data residency (TCA-068) | Settings → residency card, not assumed region |
| Guardrails on AI rewrite (TCA-037, TCA-044, TCA-060) | Rewrite assist shows policy banner |

---

## 7. Service Boundaries (no backend)

All integrations behind typed interfaces in `src/services/`:

- `analyzerService.scoreDraft()` — mock debounced scores
- `integrationService.publish()` — returns `{ queued: true }`
- `governanceService.checkPolicy()` — mock gate results

Each method annotated with `// TODO(TCA-###)` for real implementation.

---

*See [`UX_DESIGN_BRIEF.md`](./UX_DESIGN_BRIEF.md) for IA and flows. See [`README.md`](../README.md) for folder structure and backlog → component mapping.*
