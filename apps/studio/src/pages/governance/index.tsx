import { NavLink, Outlet, Route, Routes, Navigate } from "react-router-dom";

import { cn } from "@studio/lib/utils";
import { ApprovalsBoard } from "@studio/pages/governance/approvals-board";
import { ArtifactTypesScreen } from "@studio/pages/governance/artifact-types-screen";
import { GuardrailsScreen } from "@studio/pages/governance/guardrails-screen";
import { AuditLogScreen } from "@studio/pages/governance/audit-log-screen";
import { ModelsScreen } from "@studio/pages/governance/models-screen";
import { QualityGatesScreen } from "@studio/pages/governance/quality-gates-screen";
import { StandardsScreen } from "@studio/pages/governance/standards-screen";

const TABS = [
  { path: "standards", label: "Standards" },
  { path: "artifacts", label: "Artifact types" },
  { path: "gates", label: "Quality gates" },
  { path: "models", label: "Model registry" },
  { path: "audit", label: "Audit log" },
  { path: "guardrails", label: "Guardrails" },
] as const;

function GovernanceLayout() {
  return (
    <div className="h-full overflow-y-auto p-6">
      <h1 className="font-display text-2xl font-bold">Governance & Admin</h1>
      <p className="text-sm text-muted-foreground">
        Standards library, quality gates, approval workflow, audit log, model cards.
      </p>

      <div className="mt-4 rounded-lg border border-primary/30 bg-primary/5 p-4 text-sm">
        <strong>Governance note (TCA-068):</strong> Data residency is tenant-configurable
        (India/EU). DPDP/GDPR compliance is not assumed — verify in Settings → Security.
      </div>

      <nav
        className="mt-6 flex flex-wrap gap-1 border-b border-border"
        role="tablist"
        aria-label="Governance sections"
      >
        {TABS.map((tab) => (
          <NavLink
            key={tab.path}
            to={`/governance/${tab.path}`}
            role="tab"
            className={({ isActive }) =>
              cn(
                "px-4 py-2 text-sm font-medium transition",
                isActive
                  ? "border-b-2 border-primary text-primary"
                  : "text-muted-foreground hover:text-slate-900 dark:hover:text-slate-100",
              )
            }
          >
            {tab.label}
          </NavLink>
        ))}
      </nav>

      <div className="mt-6">
        <Outlet />
      </div>

      <ApprovalsBoard />
    </div>
  );
}

export function GovernanceRoutes() {
  return (
    <Routes>
      <Route element={<GovernanceLayout />}>
        <Route index element={<Navigate to="standards" replace />} />
        <Route path="standards" element={<StandardsScreen />} />
        <Route path="artifacts" element={<ArtifactTypesScreen />} />
        <Route path="gates" element={<QualityGatesScreen />} />
        <Route path="models" element={<ModelsScreen />} />
        <Route path="audit" element={<AuditLogScreen />} />
        <Route path="guardrails" element={<GuardrailsScreen />} />
      </Route>
    </Routes>
  );
}

export { AssetsPage } from "@studio/pages/governance/assets-page";

import { FeatureGrid } from "@studio/components/shared/feature-card";
import { storiesForEpic } from "@studio/mock/fixtures";

export function VerticalEpicGrid({ epicPrefixes }: { epicPrefixes: string[] }) {
  const ids = epicPrefixes.flatMap((e) => storiesForEpic(e).map((s) => s.ID));
  return (
    <div className="mt-6">
      <FeatureGrid storyIds={ids.slice(0, 12)} />
      {ids.length > 12 ? (
        <p className="mt-2 text-xs text-muted-foreground">+ {ids.length - 12} more stories mapped</p>
      ) : null}
    </div>
  );
}
