import { useParams } from "react-router-dom";

import {
  getCategoryById,
  isCategorySlug,
  resolveCategorySlug,
} from "@studio/config/categories";
import { ModuleWorkspace } from "@studio/pages/module-workspace";
import { cn } from "@studio/lib/utils";
import type { ModuleId } from "@studio/types";

export function CategoryWorkspace({ module }: { module: ModuleId }) {
  const { tab } = useParams();
  const category = resolveCategorySlug(tab);
  const meta = getCategoryById(category);

  return (
    <section className="flex min-h-0 min-w-0 flex-1 flex-col bg-surface">
      <header className="flex shrink-0 items-center gap-2 border-b border-border bg-surface-raised px-4 py-3">
        <h1 className="font-display text-sm font-semibold">{meta.label}</h1>
        <span
          className={cn(
            "rounded-full px-2 py-0.5 text-[10px] font-medium uppercase tracking-wide",
            "bg-primary/10 text-primary",
          )}
        >
          {meta.shortLabel}
        </span>
      </header>
      <div className="min-h-0 flex-1 overflow-hidden">
        <ModuleWorkspace module={module} category={category} />
      </div>
    </section>
  );
}

/** @deprecated Use CategoryWorkspace — kept for non-channel modules if needed. */
export function TabbedWorkspace({ module }: { module: ModuleId }) {
  return <CategoryWorkspace module={module} />;
}

export function categoryFromParams(tab: string | undefined) {
  if (isCategorySlug(tab)) return tab;
  return resolveCategorySlug(tab);
}
