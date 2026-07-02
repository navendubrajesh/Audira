import { ChevronDown, Plus, Search } from "lucide-react";
import { useMemo, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";

import { ScoreChip } from "@/components/ui/score-chip";
import { MODULE_CONFIG } from "@/config/modules";
import { cn } from "@/lib/utils";
import { useUiStore } from "@/store/ui-store";
import type { DraftItem, ModuleId } from "@/types";

function ContextRow({
  item,
  active,
  onClick,
}: {
  item: DraftItem;
  active: boolean;
  onClick: () => void;
}) {
  const statusDot =
    item.status === "review"
      ? "bg-warning"
      : item.status === "scheduled"
        ? "bg-primary"
        : item.status === "published"
          ? "bg-success"
          : "bg-muted-foreground";

  return (
    <button
      type="button"
      onClick={onClick}
      className={cn(
        "flex w-full items-start gap-2 rounded-md px-3 py-2 text-left text-sm transition hover:bg-surface-overlay",
        active && "bg-primary/10",
      )}
      aria-current={active ? "true" : undefined}
    >
      <span className={cn("mt-2 h-2 w-2 shrink-0 rounded-full", statusDot)} aria-hidden />
      <div className="min-w-0 flex-1">
        <p className="truncate font-medium">{item.title}</p>
        <p className="truncate text-xs text-muted-foreground">{item.excerpt}</p>
      </div>
      {item.compositeScore !== undefined ? (
        <ScoreChip score={item.compositeScore / 10} max={10} className="shrink-0 scale-90" />
      ) : null}
    </button>
  );
}

export function ContextList({ module }: { module: ModuleId }) {
  const config = MODULE_CONFIG[module];
  const { contextId } = useParams();
  const navigate = useNavigate();
  const { activeFilter, setActiveFilter, contextWidth, setContextWidth } = useUiStore();
  const [collapsed, setCollapsed] = useState<Record<string, boolean>>({});

  const filteredSections = useMemo(() => {
    return config.sections.map((section) => ({
      ...section,
      items: section.items.filter((item) => {
        if (activeFilter === "All" || activeFilter === config.filterPills[0]) return true;
        if (activeFilter === "Drafts") return item.status === "draft";
        if (activeFilter === "Scheduled") return item.status === "scheduled";
        if (activeFilter === "Published") return item.status === "published";
        if (activeFilter === "Needs review" || activeFilter === "In review")
          return item.status === "review";
        if (activeFilter === "Engagement") return item.id.startsWith("eng");
        if (activeFilter === "SEO") return item.excerpt.toLowerCase().includes("seo");
        if (activeFilter === "Attention") return item.status === "review";
        return true;
      }),
    }));
  }, [config, activeFilter]);

  return (
    <aside
      className="relative flex h-full shrink-0 flex-col border-r border-border bg-surface-raised"
      style={{ width: contextWidth }}
      aria-label={`${config.label} context list`}
    >
      <header className="border-b border-border px-4 py-3">
        <div className="flex items-center justify-between">
          <h2 className="font-display text-base font-semibold">{config.label}</h2>
          <button
            type="button"
            className="rounded-md p-1.5 text-primary hover:bg-primary/10"
            aria-label="Create new item"
          >
            <Plus className="h-4 w-4" />
          </button>
        </div>
        <div className="mt-2 flex flex-wrap gap-1" role="tablist" aria-label="Filter views">
          {config.filterPills.map((pill) => (
            <button
              key={pill}
              type="button"
              role="tab"
              aria-selected={activeFilter === pill}
              onClick={() => setActiveFilter(pill)}
              className={cn(
                "rounded-full px-2.5 py-1 text-xs font-medium transition",
                activeFilter === pill
                  ? "bg-primary text-primary-foreground"
                  : "bg-surface-overlay text-muted-foreground hover:text-slate-900 dark:hover:text-slate-100",
              )}
            >
              {pill}
            </button>
          ))}
        </div>
      </header>

      <div className="scrollbar-thin flex-1 overflow-y-auto p-2">
        {filteredSections.every((s) => s.items.length === 0) ? (
          <div className="px-3 py-8 text-center text-sm text-muted-foreground">
            <p>No items in this view.</p>
            <p className="mt-1 text-xs">Create a draft to get started.</p>
          </div>
        ) : (
          filteredSections.map((section) => (
            <section key={section.id} className="mb-3">
              <button
                type="button"
                className="flex w-full items-center gap-1 px-2 py-1.5 text-xs font-semibold uppercase tracking-wide text-muted-foreground"
                onClick={() =>
                  setCollapsed((c) => ({ ...c, [section.id]: !c[section.id] }))
                }
              >
                <ChevronDown
                  className={cn(
                    "h-3.5 w-3.5 transition",
                    collapsed[section.id] && "-rotate-90",
                  )}
                />
                {section.label}
              </button>
              {!collapsed[section.id]
                ? section.items.map((item) => (
                    <ContextRow
                      key={item.id}
                      item={item}
                      active={contextId === item.id}
                      onClick={() => navigate(`/${module}/${item.id}/compose`)}
                    />
                  ))
                : null}
            </section>
          ))
        )}

        {module === "linkedin" ? (
          <section className="mb-3">
            <p className="px-2 py-1.5 text-xs font-semibold uppercase tracking-wide text-muted-foreground">
              Engagement queue
            </p>
            <button
              type="button"
              onClick={() => navigate("/linkedin/engagement/compose")}
              className={cn(
                "flex w-full items-center gap-2 rounded-md px-3 py-2 text-left text-sm hover:bg-surface-overlay",
                contextId === "engagement" && "bg-primary/10",
              )}
            >
              <Search className="h-4 w-4 text-accent" />
              <span>Peer-post relevance queue</span>
            </button>
          </section>
        ) : null}
      </div>

      <div
        className="absolute -right-1 top-0 z-10 h-full w-2 cursor-col-resize hover:bg-primary/20"
        role="separator"
        aria-orientation="vertical"
        aria-label="Resize context panel"
        onMouseDown={(e) => {
          e.preventDefault();
          const startX = e.clientX;
          const startW = contextWidth;
          const onMove = (ev: MouseEvent) => setContextWidth(startW + ev.clientX - startX);
          const onUp = () => {
            window.removeEventListener("mousemove", onMove);
            window.removeEventListener("mouseup", onUp);
          };
          window.addEventListener("mousemove", onMove);
          window.addEventListener("mouseup", onUp);
        }}
      />
    </aside>
  );
}
