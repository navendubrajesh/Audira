import { ChevronDown, Plus } from "lucide-react";
import { useEffect, useMemo, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";

import { ScoreChip } from "@studio/components/ui/score-chip";
import {
  CHANNEL_CATEGORIES,
  DEFAULT_CATEGORY,
  isChannelModule,
} from "@studio/config/categories";
import { MODULE_CONFIG } from "@studio/config/modules";
import { storiesForCategory } from "@studio/lib/category-stories";
import { cn } from "@studio/lib/utils";
import { DEFAULT_PERSONAS } from "@studio/mock/fixtures";
import { createDraft } from "@studio/services/studio-api";
import { useDraftsStore } from "@studio/store/drafts-store";
import { useUiStore } from "@studio/store/ui-store";
import type { CategorySlug, DraftItem, ModuleId } from "@studio/types";

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

function StoryRow({
  storyId,
  label,
  active,
  onClick,
}: {
  storyId: string;
  label: string;
  active: boolean;
  onClick: () => void;
}) {
  return (
    <button
      type="button"
      onClick={onClick}
      className={cn(
        "flex w-full items-start gap-2 rounded-md px-3 py-1.5 text-left text-sm transition hover:bg-surface-overlay",
        active && "bg-primary/10",
      )}
    >
      <span className="mt-0.5 shrink-0 font-mono text-[10px] text-primary">{storyId}</span>
      <span className="min-w-0 flex-1 text-xs leading-snug text-muted-foreground">{label}</span>
    </button>
  );
}

function ChannelCategoryNav({ module }: { module: ModuleId }) {
  const config = MODULE_CONFIG[module];
  const { contextId, tab } = useParams();
  const navigate = useNavigate();
  const { contextWidth, setContextWidth } = useUiStore();
  const { getForModule, load } = useDraftsStore();
  const [collapsed, setCollapsed] = useState<Record<string, boolean>>({});

  const activeCategory = (tab as CategorySlug) ?? DEFAULT_CATEGORY;
  const clientId = contextId ?? `${module}-default`;

  useEffect(() => {
    void load(module);
  }, [module, load]);

  const apiDrafts = getForModule(module);

  const draftsByStatus = useMemo(
    () => ({
      draft: apiDrafts.filter((d) => d.status === "draft"),
      scheduled: apiDrafts.filter((d) => d.status === "scheduled"),
      published: apiDrafts.filter((d) => d.status === "published"),
    }),
    [apiDrafts],
  );

  const navigateCategory = (categoryId: CategorySlug, draftId?: string) => {
    const id = draftId ?? clientId;
    navigate(`/${module}/${id}/${categoryId}`);
  };

  return (
    <aside
      className="relative flex h-full min-h-0 shrink-0 flex-col border-r border-border bg-surface-raised"
      style={{ width: contextWidth }}
      aria-label={`${config.label} workspace navigation`}
    >
      <header className="border-b border-border px-4 py-3">
        <div className="flex items-center justify-between">
          <h2 className="font-display text-base font-semibold">{config.label}</h2>
          <button
            type="button"
            className="rounded-md p-1.5 text-primary hover:bg-primary/10"
            aria-label="Create new draft"
            onClick={() => {
              void createDraft({ vertical: module, title: "New draft", body: "" }).then((d) => {
                void load(module);
                navigate(`/${module}/${d.id}/compose-drafting`);
              });
            }}
          >
            <Plus className="h-4 w-4" />
          </button>
        </div>
        <p className="mt-1 text-xs text-muted-foreground">
          Pick a category, then open a user story or draft.
        </p>
      </header>

      <div
        className="scrollbar-thin min-h-0 flex-1 overflow-y-auto p-2 focus:outline-none focus-visible:ring-2 focus-visible:ring-primary/40"
        tabIndex={0}
      >
        {CHANNEL_CATEGORIES.map((category) => {
          const stories = storiesForCategory(category.id, module);
          const isActiveCategory = activeCategory === category.id;

          return (
            <section key={category.id} className="mb-2">
              <div
                className={cn(
                  "flex w-full items-center gap-0.5 rounded-md px-1 py-1 transition",
                  isActiveCategory && "bg-primary/10",
                )}
              >
                <button
                  type="button"
                  className="rounded p-1 text-muted-foreground hover:bg-surface-overlay"
                  aria-label={collapsed[category.id] ? "Expand section" : "Collapse section"}
                  onClick={() =>
                    setCollapsed((c) => ({ ...c, [category.id]: !c[category.id] }))
                  }
                >
                  <ChevronDown
                    className={cn(
                      "h-3.5 w-3.5 transition",
                      collapsed[category.id] && "-rotate-90",
                    )}
                  />
                </button>
                <button
                  type="button"
                  className={cn(
                    "min-w-0 flex-1 py-1 text-left text-xs font-semibold uppercase leading-snug tracking-wide",
                    isActiveCategory ? "text-primary" : "text-muted-foreground",
                  )}
                  onClick={() => {
                    navigateCategory(category.id);
                    setCollapsed((c) => ({ ...c, [category.id]: false }));
                  }}
                >
                  {category.label}
                </button>
              </div>

              {!collapsed[category.id] ? (
                <div className="ml-1 mt-0.5 space-y-0.5 border-l border-border/60 pl-2">
                  {category.id === "personas-audience"
                    ? DEFAULT_PERSONAS.map((p) => (
                        <StoryRow
                          key={p.id}
                          storyId={p.storyId}
                          label={p.label}
                          active={isActiveCategory && contextId === p.id}
                          onClick={() => navigateCategory(category.id, clientId)}
                        />
                      ))
                    : null}

                  {category.id === "compose-drafting"
                    ? apiDrafts.map((item) => (
                        <ContextRow
                          key={item.id}
                          item={item}
                          active={contextId === item.id && isActiveCategory}
                          onClick={() => navigateCategory(category.id, item.id)}
                        />
                      ))
                    : null}

                  {category.id === "engagement-community" && module === "linkedin" ? (
                    <button
                      type="button"
                      onClick={() => navigate(`/${module}/${clientId}/engagement-community`)}
                      className={cn(
                        "flex w-full rounded-md px-3 py-2 text-left text-sm hover:bg-surface-overlay",
                        isActiveCategory && "bg-primary/10",
                      )}
                    >
                      <span className="font-medium">Peer-post relevance queue</span>
                      <span className="ml-1 text-xs text-muted-foreground">· TCA-088</span>
                    </button>
                  ) : null}

                  {category.id === "schedule-publishing" ? (
                    <>
                      {draftsByStatus.scheduled.length > 0 ? (
                        <p className="px-2 pt-1 text-[10px] font-semibold uppercase text-muted-foreground">
                          Scheduled
                        </p>
                      ) : null}
                      {draftsByStatus.scheduled.map((item) => (
                        <ContextRow
                          key={item.id}
                          item={item}
                          active={contextId === item.id && isActiveCategory}
                          onClick={() => navigateCategory(category.id, item.id)}
                        />
                      ))}
                      {draftsByStatus.published.length > 0 ? (
                        <p className="px-2 pt-2 text-[10px] font-semibold uppercase text-muted-foreground">
                          Published
                        </p>
                      ) : null}
                      {draftsByStatus.published.map((item) => (
                        <ContextRow
                          key={item.id}
                          item={item}
                          active={contextId === item.id && isActiveCategory}
                          onClick={() => navigateCategory(category.id, item.id)}
                        />
                      ))}
                    </>
                  ) : null}

                  {stories.map((story) => (
                    <StoryRow
                      key={story.id}
                      storyId={story.id}
                      label={story.label}
                      active={isActiveCategory}
                      onClick={() => navigateCategory(category.id, clientId)}
                    />
                  ))}

                  {stories.length === 0 &&
                  category.id !== "compose-drafting" &&
                  category.id !== "engagement-community" &&
                  category.id !== "schedule-publishing" &&
                  category.id !== "personas-audience" ? (
                    <p className="px-3 py-2 text-xs text-muted-foreground">No stories mapped yet.</p>
                  ) : null}
                </div>
              ) : null}
            </section>
          );
        })}
      </div>

      <div
        className="absolute -right-1 top-0 z-10 h-full w-2 cursor-col-resize hover:bg-primary/20"
        role="separator"
        aria-orientation="vertical"
        aria-label="Resize navigation panel"
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

/** Legacy context list for Home, Analytics, Governance, etc. */
function LegacyContextList({ module }: { module: ModuleId }) {
  const config = MODULE_CONFIG[module];
  const { contextId } = useParams();
  const navigate = useNavigate();
  const { activeFilter, setActiveFilter, contextWidth, setContextWidth } = useUiStore();
  const [collapsed, setCollapsed] = useState<Record<string, boolean>>({});

  const filteredSections = useMemo(
    () =>
      config.sections.map((section) => ({
        ...section,
        items: section.items.filter((item) => {
          if (activeFilter === "All" || activeFilter === config.filterPills[0]) return true;
          if (activeFilter === "Drafts") return item.status === "draft";
          if (activeFilter === "Scheduled") return item.status === "scheduled";
          if (activeFilter === "Published") return item.status === "published";
          if (activeFilter === "Needs review" || activeFilter === "In review")
            return item.status === "review";
          if (activeFilter === "Attention") return item.status === "review";
          return true;
        }),
      })),
    [config, activeFilter],
  );

  return (
    <aside
      className="relative flex h-full min-h-0 shrink-0 flex-col border-r border-border bg-surface-raised"
      style={{ width: contextWidth }}
      aria-label={`${config.label} context list`}
    >
      <header className="border-b border-border px-4 py-3">
        <h2 className="font-display text-base font-semibold">{config.label}</h2>
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

      <div className="scrollbar-thin min-h-0 flex-1 overflow-y-auto p-2" tabIndex={0}>
        {filteredSections.map((section) => (
          <section key={section.id} className="mb-3">
            <button
              type="button"
              className="flex w-full items-center gap-1 px-2 py-1.5 text-xs font-semibold uppercase tracking-wide text-muted-foreground"
              onClick={() => setCollapsed((c) => ({ ...c, [section.id]: !c[section.id] }))}
            >
              <ChevronDown
                className={cn("h-3.5 w-3.5 transition", collapsed[section.id] && "-rotate-90")}
              />
              {section.label}
            </button>
            {!collapsed[section.id]
              ? section.items.map((item) => (
                  <ContextRow
                    key={item.id}
                    item={item}
                    active={contextId === item.id}
                    onClick={() => navigate(`/${module}/${item.id}/insights-reporting`)}
                  />
                ))
              : null}
          </section>
        ))}
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

export function ContextList({ module }: { module: ModuleId }) {
  if (isChannelModule(module)) {
    return <ChannelCategoryNav module={module} />;
  }
  return <LegacyContextList module={module} />;
}
