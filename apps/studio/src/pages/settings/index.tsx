import { NavLink, Outlet, Route, Routes, Navigate } from "react-router-dom";

import { cn } from "@studio/lib/utils";
import { AudiencesScreen } from "@studio/pages/settings/audiences-screen";
import { BrandScreen } from "@studio/pages/settings/brand-screen";
import { IntegrationsScreen } from "@studio/pages/settings/integrations-screen";
import { ResidencyScreen } from "@studio/pages/settings/residency-screen";

const TABS = [
  { path: "security", label: "Security & residency", story: "TCA-068" },
  { path: "audiences", label: "Audiences", story: "TCA-001" },
  { path: "brand", label: "Brand voice", story: "TCA-002" },
  { path: "integrations", label: "Integrations", story: "TCA-036" },
] as const;

function SettingsLayout() {
  return (
    <div className="h-full min-h-0 overflow-y-auto p-6">
      <h1 className="font-display text-2xl font-bold">Settings</h1>
      <p className="text-sm text-muted-foreground">
        SSO, RBAC, audiences, brand voice, and data residency (Phase 1 Must).
      </p>

      <nav
        className="mt-6 flex flex-wrap gap-1 border-b border-border"
        role="tablist"
        aria-label="Settings sections"
      >
        {TABS.map((tab) => (
          <NavLink
            key={tab.path}
            to={`/settings/${tab.path}`}
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
    </div>
  );
}

export function SettingsRoutes() {
  return (
    <Routes>
      <Route element={<SettingsLayout />}>
        <Route index element={<Navigate to="security" replace />} />
        <Route path="security" element={<ResidencyScreen />} />
        <Route path="audiences" element={<AudiencesScreen />} />
        <Route path="brand" element={<BrandScreen />} />
        <Route path="integrations" element={<IntegrationsScreen />} />
      </Route>
    </Routes>
  );
}

/** @deprecated use SettingsRoutes — kept for assets import compatibility */
export function SettingsPage() {
  return <SettingsRoutes />;
}
