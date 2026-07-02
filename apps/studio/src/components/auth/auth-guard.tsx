import { Navigate, Outlet, useLocation } from "react-router-dom";
import { useEffect } from "react";

import { GlobalStatePanel } from "@studio/components/shared/global-states";
import { useAuthStore } from "@studio/store/auth-store";

export function AuthGuard() {
  const { user, loading, initialized, initialize } = useAuthStore();
  const location = useLocation();

  useEffect(() => {
    if (!initialized) void initialize();
  }, [initialized, initialize]);

  if (!initialized || loading) {
    return <GlobalStatePanel variant="loading" />;
  }

  if (!user) {
    return <Navigate to="/login" state={{ from: location.pathname }} replace />;
  }

  return <Outlet />;
}
