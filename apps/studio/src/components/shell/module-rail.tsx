import {
  BarChart3,
  Briefcase,
  FileText,
  FolderOpen,
  Home,
  Linkedin,
  PanelLeft,
  Settings,
  Share2,
  Shield,
  Table2,
} from "lucide-react";
import { NavLink } from "react-router-dom";

import { MODULES } from "@studio/config/modules";
import { cn } from "@studio/lib/utils";
import { useUiStore } from "@studio/store/ui-store";
import type { ModuleId } from "@studio/types";

const ICONS: Record<string, React.ComponentType<{ className?: string }>> = {
  home: Home,
  share2: Share2,
  linkedin: Linkedin,
  briefcase: Briefcase,
  "file-text": FileText,
  "bar-chart3": BarChart3,
  folder: FolderOpen,
  shield: Shield,
  settings: Settings,
  table: Table2,
};

export function ModuleRail() {
  const { railExpanded, setRailExpanded } = useUiStore();

  return (
    <nav
      className={cn(
        "flex h-full min-h-0 shrink-0 flex-col border-r border-border bg-surface-raised py-3",
        railExpanded ? "w-[var(--rail-width-expanded)]" : "w-[var(--rail-width)]",
      )}
      aria-label="Primary modules"
    >
      <div className="mb-2 flex justify-center px-2">
        <button
          type="button"
          onClick={() => setRailExpanded(!railExpanded)}
          className="rounded-md p-2 text-muted-foreground hover:bg-surface-overlay"
          aria-label={railExpanded ? "Collapse module rail" : "Expand module rail"}
        >
          <PanelLeft className="h-5 w-5" />
        </button>
      </div>

      <div className="flex min-h-0 flex-1 flex-col gap-1 overflow-y-auto px-2">
        {MODULES.map((mod, idx) => {
          const Icon = ICONS[mod.id === "home" ? "home" : mod.id === "social" ? "share2" : mod.id === "linkedin" ? "linkedin" : mod.id === "placement" ? "briefcase" : mod.id === "blog" ? "file-text" : mod.id === "analytics" ? "bar-chart3" : mod.id === "assets" ? "folder" : mod.id === "governance" ? "shield" : "settings"];
          return (
            <NavLink
              key={mod.id}
              to={mod.path}
              title={mod.label}
              aria-keyshortcuts={`Alt+${idx + 1}`}
              className={({ isActive }) =>
                cn(
                  "relative flex items-center gap-3 rounded-lg px-2 py-2.5 text-sm font-medium transition",
                  isActive
                    ? "bg-primary/10 text-primary"
                    : "text-muted-foreground hover:bg-surface-overlay hover:text-slate-900 dark:hover:text-slate-100",
                  railExpanded ? "justify-start" : "justify-center",
                )
              }
            >
              <Icon className="h-5 w-5 shrink-0" aria-hidden />
              {railExpanded ? <span className="truncate text-xs">{mod.label}</span> : null}
              {mod.badge ? (
                <span
                  className={cn(
                    "flex h-4 min-w-4 items-center justify-center rounded-full bg-danger px-1 text-[10px] font-bold text-white",
                    railExpanded ? "ml-auto" : "absolute -right-0.5 -top-0.5",
                  )}
                  aria-label={`${mod.badge} items need attention`}
                >
                  {mod.badge}
                </span>
              ) : null}
            </NavLink>
          );
        })}

        <div className="my-2 border-t border-border" />

        <NavLink
          to="/competitors"
          title="Competitor Landscape"
          className={({ isActive }) =>
            cn(
              "flex items-center gap-3 rounded-lg px-2 py-2.5 text-sm transition",
              isActive ? "bg-primary/10 text-primary" : "text-muted-foreground hover:bg-surface-overlay",
              railExpanded ? "justify-start" : "justify-center",
            )
          }
        >
          <Table2 className="h-5 w-5" />
          {railExpanded ? <span className="text-xs">Competitors</span> : null}
        </NavLink>
      </div>

      <div className="px-2 pt-2">
        <div
          className={cn(
            "rounded-lg bg-gradient-to-br from-primary/20 to-accent/10 p-2 text-center",
            !railExpanded && "p-1.5",
          )}
        >
          <span className="font-display text-xs font-bold text-primary">A</span>
          {railExpanded ? (
            <p className="mt-1 text-[10px] leading-tight text-muted-foreground">Audira.run</p>
          ) : null}
        </div>
      </div>
    </nav>
  );
}

export function moduleFromPath(path: string): ModuleId {
  const seg = path.split("/").filter(Boolean)[0] ?? "home";
  const valid: ModuleId[] = [
    "home",
    "social",
    "linkedin",
    "placement",
    "blog",
    "analytics",
    "assets",
    "governance",
    "settings",
    "competitors",
  ];
  return valid.includes(seg as ModuleId) ? (seg as ModuleId) : "home";
}
