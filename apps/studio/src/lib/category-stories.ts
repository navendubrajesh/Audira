import { CHANNEL_CATEGORIES } from "@studio/config/categories";
import traceability from "@studio/mock/traceability.json";
import type { CategorySlug, ModuleId } from "@studio/types";

export interface CategoryStoryItem {
  id: string;
  label: string;
  status: string;
  priority: string;
}

interface TraceRow {
  id: string;
  epic: string;
  functionality: string;
  status: string;
  priority: string;
  verticals: string[];
}

const rows = traceability as TraceRow[];

function storyMatchesVertical(row: TraceRow, module: ModuleId): boolean {
  if (!row.verticals?.length) return true;
  if (row.verticals.includes(module)) return true;
  if (row.verticals.includes("home") && module !== "competitors") return true;
  return false;
}

function storyInCategory(row: TraceRow, categoryId: CategorySlug): boolean {
  const cat = CHANNEL_CATEGORIES.find((c) => c.id === categoryId);
  if (!cat) return false;
  if (cat.extraStoryIds?.includes(row.id)) return true;
  return cat.epicPrefixes.some((prefix) => row.epic.startsWith(prefix));
}

export function storiesForCategory(
  categoryId: CategorySlug,
  module: ModuleId,
): CategoryStoryItem[] {
  const seen = new Set<string>();
  const items: CategoryStoryItem[] = [];

  for (const row of rows) {
    if (!storyInCategory(row, categoryId)) continue;
    if (!storyMatchesVertical(row, module)) continue;
    if (seen.has(row.id)) continue;
    seen.add(row.id);
    items.push({
      id: row.id,
      label: row.functionality,
      status: row.status,
      priority: row.priority,
    });
  }

  return items.sort((a, b) => a.id.localeCompare(b.id));
}
