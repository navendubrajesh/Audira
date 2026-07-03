export type BacklogStatus = "Done" | "Partial" | "To Do";

export interface BacklogStory {
  ID: string;
  Platform: string;
  Epic: string;
  Functionality: string;
  "User Story": string;
  Role: string;
  Type: string;
  Priority: string;
  "Benchmark Source": string;
  "Acceptance Criteria": string;
  Phase: string;
  "Market Coverage": string;
  Status: BacklogStatus;
}

export interface CompetitorRow {
  Vendor: string;
  "Primary Archetype": string;
  Secondary: string;
  "Modalities Analysed": string;
  "Core Predictions / Metrics": string;
  "Enterprise / Comms Fit": string;
  Website: string;
  "Signature strength / signal": string;
}

export interface FeedbackCategory {
  id: string;
  category: string;
  score: number;
  maxScore: number;
  insight: string;
  recommendedFix: string;
  highlightStart?: number;
  highlightEnd?: number;
  storyIds: string[];
}

export interface DraftItem {
  id: string;
  title: string;
  vertical: ModuleId;
  status: "draft" | "scheduled" | "published" | "review";
  compositeScore?: number;
  updatedAt: string;
  excerpt: string;
  storyIds?: string[];
}

export type ModuleId =
  | "home"
  | "social"
  | "linkedin"
  | "placement"
  | "blog"
  | "analytics"
  | "assets"
  | "governance"
  | "settings"
  | "competitors";

export type WorkspaceTab =
  | "compose"
  | "analyze"
  | "schedule"
  | "insights"
  | "assets"
  | "activity";

/** Channel workspace navigation categories (replaces horizontal tabs). */
export type CategorySlug =
  | "personas-audience"
  | "assets-ingestion"
  | "analyze-score"
  | "engagement-community"
  | "compose-drafting"
  | "schedule-publishing"
  | "insights-reporting";

export interface Persona {
  id: string;
  label: string;
  description: string;
  storyId: string;
}

export interface ContextListSection {
  id: string;
  label: string;
  items: DraftItem[];
  collapsible?: boolean;
}

export interface ModuleConfig {
  id: ModuleId;
  label: string;
  icon: string;
  badge?: number;
  filterPills: string[];
  sections: ContextListSection[];
  tabs: WorkspaceTab[];
}
