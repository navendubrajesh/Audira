# Audira Studio

Greenfield enterprise frontend for **Audira.run** — a neuro-grounded communications analyzer spanning Social, LinkedIn, Placement, and Blog verticals.

Built with **React + TypeScript + Vite**, **Tailwind CSS**, **React Router**, **Zustand**, and **Recharts**. All data is local mock/fixtures; integrations are stubbed in `src/services/` with `// TODO(TCA-###)` comments.

## Quick start

```bash
# From repo root
npm install
npm run dev:studio
```

Open [http://localhost:5174](http://localhost:5174).

## Information architecture

Three-zone shell (Teams *pattern*, distinct visual identity):

| Zone | Component | Purpose |
|------|-----------|---------|
| **1 — Module rail** | `components/shell/module-rail.tsx` | Home, Social, LinkedIn, Placement, Blog, Analytics, Assets, Governance, Settings |
| **2 — Context list** | `components/shell/context-list.tsx` | Filter pills + collapsible sections per module |
| **3 — Tabbed workspace** | `components/shell/tabbed-workspace.tsx` | Compose · Analyze · Schedule · Insights · Assets · Activity |

Global top bar: search / “Ask Audira”, connection status, theme toggle.

## Backlog → component mapping

| Backlog area | Primary location |
|--------------|------------------|
| TCA-083, TCA-091, TCA-087 | `components/analyzer/analyzer-workspace.tsx` |
| TCA-077 | `components/analyzer/persona-picker.tsx` |
| TCA-078 | Anti-generic wizard in `persona-picker.tsx` |
| TCA-079 | `components/analyzer/multimodal-drop-zone.tsx` |
| TCA-088–090 | `pages/engagement-helper.tsx` |
| E14 analytics | `pages/dashboards.tsx` |
| E13/E15/E16/E17 | `pages/governance.tsx` |
| Competitor Landscape sheet | `pages/competitors.tsx` |
| All 92 stories | `components/shared/feature-card.tsx` + `mock/backlog-data.json` |

Regenerate traceability table:

```bash
npm run gen:roadmap --workspace=@audira/studio
```

## Docs

- [UX Design Brief](./docs/UX_DESIGN_BRIEF.md) — Phase 1
- [Functional Spec](./docs/FUNCTIONAL_SPEC.md) — Phase 2
- [ROADMAP.md](./ROADMAP.md) — full TCA traceability

## Folder structure

```
src/
  components/
    analyzer/     # Signature split-panel workspace
    shell/        # Three-zone layout
    shared/       # Feature cards, backlog badges
    ui/           # Design system primitives
  config/         # Module definitions
  mock/           # backlog-data.json, fixtures
  pages/          # Route-level screens
  services/       # Stubbed APIs (TODO markers)
  store/          # Zustand UI + analyzer state
  types/
```

## Design tokens

CSS variables in `src/index.css` — teal primary, amber accent, semantic score colours. Toggle dark mode from the top bar. Fonts: **Outfit** (display) + **IBM Plex Sans** (body).

## Status badges

Every feature card shows **Story ID** and backlog **Status** (Done / Partial / To Do) from the spreadsheet.
