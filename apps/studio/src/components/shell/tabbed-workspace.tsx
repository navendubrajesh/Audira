import { NavLink, useParams } from "react-router-dom";

import { ModuleWorkspace } from "@/pages/module-workspace";
import { MODULE_CONFIG } from "@/config/modules";
import { cn } from "@/lib/utils";
import type { ModuleId, WorkspaceTab } from "@/types";

const TAB_LABELS: Record<WorkspaceTab, string> = {
  compose: "Compose",
  analyze: "Analyze",
  schedule: "Schedule",
  insights: "Insights",
  assets: "Assets",
  activity: "Activity",
};

export function TabbedWorkspace({ module }: { module: ModuleId }) {
  const { contextId, tab } = useParams();
  const config = MODULE_CONFIG[module];
  const tabs = config.tabs;
  const activeTab = (tab as WorkspaceTab) ?? tabs[0];
  const base = `/${module}/${contextId ?? "default"}`;

  return (
    <section className="flex min-w-0 flex-1 flex-col bg-surface">
      <div
        className="flex items-center gap-1 border-b border-border bg-surface-raised px-4"
        role="tablist"
        aria-label="Workspace tabs"
      >
        {tabs.map((t) => (
          <NavLink
            key={t}
            to={`${base}/${t}`}
            role="tab"
            aria-selected={activeTab === t}
            className={({ isActive }) =>
              cn(
                "relative px-4 py-3 text-sm font-medium transition",
                isActive
                  ? "text-primary after:absolute after:inset-x-2 after:bottom-0 after:h-0.5 after:rounded-full after:bg-primary"
                  : "text-muted-foreground hover:text-slate-900 dark:hover:text-slate-100",
              )
            }
          >
            {TAB_LABELS[t]}
          </NavLink>
        ))}
      </div>
      <div className="flex-1 overflow-hidden">
        <ModuleWorkspace module={module} />
      </div>
    </section>
  );
}
