import type { CategorySlug, ModuleId } from "@studio/types";

export interface NavCategory {
  id: CategorySlug;
  label: string;
  shortLabel: string;
  /** Route segment under /:channel/:clientId/:category */
  epicPrefixes: string[];
  extraStoryIds?: string[];
}

/** Fixed order — matches channel sidebar groups. */
export const CHANNEL_CATEGORIES: NavCategory[] = [
  {
    id: "personas-audience",
    label: "Personas & Audience Context",
    shortLabel: "Personas",
    epicPrefixes: ["E01"],
    extraStoryIds: ["TCA-077"],
  },
  {
    id: "assets-ingestion",
    label: "Assets & Ingestion",
    shortLabel: "Assets",
    epicPrefixes: ["E02"],
    extraStoryIds: ["TCA-007", "TCA-079", "TCA-009", "TCA-010"],
  },
  {
    id: "analyze-score",
    label: "Analyze & Score",
    shortLabel: "Analyze",
    epicPrefixes: ["E06", "E07", "E08", "E09", "E19", "E20", "E21"],
    extraStoryIds: ["TCA-008", "TCA-038", "TCA-040", "TCA-083", "TCA-087", "TCA-091"],
  },
  {
    id: "engagement-community",
    label: "Engagement & Community",
    shortLabel: "Engagement",
    epicPrefixes: ["E05", "E22"],
    extraStoryIds: ["TCA-088", "TCA-089", "TCA-090"],
  },
  {
    id: "compose-drafting",
    label: "Compose & Drafting",
    shortLabel: "Compose",
    epicPrefixes: ["E04"],
    extraStoryIds: ["TCA-006"],
  },
  {
    id: "schedule-publishing",
    label: "Schedule & Publishing",
    shortLabel: "Schedule",
    epicPrefixes: ["E11", "E12"],
    extraStoryIds: ["TCA-011", "TCA-013"],
  },
  {
    id: "insights-reporting",
    label: "Insights & Reporting",
    shortLabel: "Insights",
    epicPrefixes: ["E14"],
    extraStoryIds: ["TCA-014", "TCA-039", "TCA-053", "TCA-056", "TCA-061"],
  },
];

export const CHANNEL_MODULES: ModuleId[] = ["social", "linkedin", "placement", "blog"];

export const DEFAULT_CATEGORY: CategorySlug = "analyze-score";

/** Legacy top-tab slugs → new category slugs. */
export const LEGACY_TAB_REDIRECTS: Record<string, CategorySlug> = {
  compose: "compose-drafting",
  analyze: "analyze-score",
  schedule: "schedule-publishing",
  insights: "insights-reporting",
  assets: "assets-ingestion",
  activity: "insights-reporting",
};

export function isChannelModule(module: ModuleId): boolean {
  return CHANNEL_MODULES.includes(module);
}

export function isCategorySlug(value: string | undefined): value is CategorySlug {
  return CHANNEL_CATEGORIES.some((c) => c.id === value);
}

export function resolveCategorySlug(tabOrCategory: string | undefined): CategorySlug {
  if (!tabOrCategory) return DEFAULT_CATEGORY;
  if (isCategorySlug(tabOrCategory)) return tabOrCategory;
  return LEGACY_TAB_REDIRECTS[tabOrCategory] ?? DEFAULT_CATEGORY;
}

export function getCategoryById(id: CategorySlug): NavCategory {
  return CHANNEL_CATEGORIES.find((c) => c.id === id)!;
}
