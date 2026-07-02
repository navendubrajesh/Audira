import { Outlet, useLocation } from "react-router-dom";
import { useEffect } from "react";

import { ContextList } from "@studio/components/shell/context-list";
import { GlobalTopBar } from "@studio/components/shell/global-top-bar";
import { moduleFromPath, ModuleRail } from "@studio/components/shell/module-rail";
import { useUiStore } from "@studio/store/ui-store";

export function AppShell() {
  const location = useLocation();
  const module = moduleFromPath(location.pathname);
  const { theme } = useUiStore();

  useEffect(() => {
    document.documentElement.classList.toggle("dark", theme === "dark");
  }, [theme]);

  useEffect(() => {
    const handler = (e: KeyboardEvent) => {
      if (e.altKey && e.key >= "1" && e.key <= "9") {
        const idx = Number(e.key) - 1;
        const paths = ["/home", "/social", "/linkedin", "/placement", "/blog", "/analytics", "/assets", "/governance", "/settings"];
        if (paths[idx]) window.location.href = paths[idx];
      }
    };
    window.addEventListener("keydown", handler);
    return () => window.removeEventListener("keydown", handler);
  }, []);

  const hideContext = module === "competitors";

  return (
    <div className="flex h-screen flex-col overflow-hidden">
      <GlobalTopBar />
      <div className="flex min-h-0 flex-1">
        <ModuleRail />
        {!hideContext ? <ContextList module={module} /> : null}
        <main className="flex min-w-0 flex-1 flex-col">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
