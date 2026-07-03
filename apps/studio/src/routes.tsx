import { Navigate, Route, Routes } from "react-router-dom";

import { AuthGuard } from "@studio/components/auth/auth-guard";
import { AppShell } from "@studio/components/shell/app-shell";
import { VerticalModuleRoutes } from "@studio/routes/channel-routes";
import { AnalyticsDashboard, HomeDashboard } from "@studio/pages/dashboards";
import { CompetitorLandscapePage } from "@studio/pages/competitors";
import { AssetsPage, GovernanceRoutes } from "@studio/pages/governance/index";
import { SettingsRoutes } from "@studio/pages/settings/index";
import { AuthCallbackPage } from "@studio/pages/auth-callback";
import { LoginPage } from "@studio/pages/login";

export function AppRoutes() {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route path="/auth/callback" element={<AuthCallbackPage />} />

      <Route element={<AuthGuard />}>
        <Route path="/" element={<Navigate to="/home" replace />} />
        <Route element={<AppShell />}>
          <Route path="/home" element={<HomeDashboard />} />

          <Route path="/social/*" element={<VerticalModuleRoutes module="social" />} />
          <Route path="/linkedin/*" element={<VerticalModuleRoutes module="linkedin" />} />
          <Route path="/placement/*" element={<VerticalModuleRoutes module="placement" />} />
          <Route path="/blog/*" element={<VerticalModuleRoutes module="blog" />} />

          <Route path="/analytics" element={<AnalyticsDashboard />} />
          <Route path="/assets" element={<AssetsPage />} />
          <Route path="/governance/*" element={<GovernanceRoutes />} />
          <Route path="/settings/*" element={<SettingsRoutes />} />
          <Route path="/competitors" element={<CompetitorLandscapePage />} />
        </Route>
      </Route>
    </Routes>
  );
}
