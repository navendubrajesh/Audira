import { Navigate, Route, Routes } from "react-router-dom";

import { AppShell } from "@/components/shell/app-shell";
import { TabbedWorkspace } from "@/components/shell/tabbed-workspace";
import { getDefaultContextId } from "@/config/modules";
import { AnalyticsDashboard, HomeDashboard } from "@/pages/dashboards";
import { CompetitorLandscapePage } from "@/pages/competitors";
import { AssetsPage, GovernancePage, SettingsPage } from "@/pages/governance";
import type { ModuleId } from "@/types";

function VerticalModuleRoutes({ module }: { module: ModuleId }) {
  const defaultId = getDefaultContextId(module);
  return (
    <Routes>
      <Route index element={<Navigate to={`${defaultId}/compose`} replace />} />
      <Route path=":contextId" element={<Navigate to="compose" replace />} />
      <Route path=":contextId/:tab" element={<TabbedWorkspace module={module} />} />
    </Routes>
  );
}

export function AppRoutes() {
  return (
    <Routes>
      <Route path="/" element={<Navigate to="/home" replace />} />
      <Route element={<AppShell />}>
        <Route path="/home" element={<HomeDashboard />} />

        <Route path="/social/*" element={<VerticalModuleRoutes module="social" />} />
        <Route path="/linkedin/*" element={<VerticalModuleRoutes module="linkedin" />} />
        <Route path="/placement/*" element={<VerticalModuleRoutes module="placement" />} />
        <Route path="/blog/*" element={<VerticalModuleRoutes module="blog" />} />

        <Route path="/analytics" element={<AnalyticsDashboard />} />
        <Route path="/assets" element={<AssetsPage />} />
        <Route path="/governance" element={<GovernancePage />} />
        <Route path="/settings" element={<SettingsPage />} />
        <Route path="/competitors" element={<CompetitorLandscapePage />} />
      </Route>
    </Routes>
  );
}
