import { useParams } from "react-router-dom";

import {
  AnalyzerWorkspace,
  ComposeTab,
  GenericTabPlaceholder,
} from "@studio/components/analyzer/analyzer-workspace";
import { resolveCategorySlug } from "@studio/config/categories";
import { ScheduleTabPlaceholder } from "@studio/components/shared/schedule-tab";
import { ActivityTab, InsightsTab } from "@studio/components/shared/activity-insights-tabs";
import { VerticalEpicGrid } from "@studio/pages/governance/index";
import { EngagementHelperPage } from "@studio/pages/engagement-helper";
import type { CategorySlug, ModuleId } from "@studio/types";

const EPIC_MAP: Record<ModuleId, string[]> = {
  home: ["E01", "E09", "E14"],
  social: ["E04", "E05", "E11"],
  linkedin: ["E19", "E20", "E21", "E22"],
  placement: ["E06", "E15", "E10"],
  blog: ["E06", "E07", "E11"],
  analytics: ["E14", "E09"],
  assets: ["E02"],
  governance: ["E13", "E15", "E16", "E17"],
  settings: ["E17"],
  competitors: [],
};

function CategoryPlaceholder({
  title,
  description,
  storyIds,
  module,
}: {
  title: string;
  description: string;
  storyIds: string[];
  module: ModuleId;
}) {
  return (
    <div className="h-full min-h-0 overflow-y-auto">
      <GenericTabPlaceholder tab={title} storyIds={storyIds}>
        <h2 className="font-display text-lg font-semibold">{title}</h2>
        <p className="text-sm text-muted-foreground">{description}</p>
      </GenericTabPlaceholder>
      <div className="px-6 pb-6">
        <VerticalEpicGrid epicPrefixes={EPIC_MAP[module] ?? []} />
      </div>
    </div>
  );
}

export function ModuleWorkspace({
  module,
  category: categoryProp,
}: {
  module: ModuleId;
  category?: CategorySlug;
}) {
  const { tab } = useParams();
  const category = categoryProp ?? resolveCategorySlug(tab);

  const contentChannels: ModuleId[] = ["linkedin", "social", "blog", "placement"];

  switch (category) {
    case "analyze-score":
      if (contentChannels.includes(module)) {
        return <AnalyzerWorkspace module={module} />;
      }
      return (
        <CategoryPlaceholder
          title="Analyze & Score"
          description="Open a content channel (LinkedIn, Social, Blog, Placement) for the split-panel analyzer."
          storyIds={["TCA-038", "TCA-083", "TCA-091"]}
          module={module}
        />
      );

    case "compose-drafting":
      return (
        <div className="h-full min-h-0 overflow-y-auto">
          <ComposeTab module={module} />
        </div>
      );

    case "schedule-publishing":
      return (
        <div className="h-full min-h-0 overflow-y-auto">
          <ScheduleTabPlaceholder module={module} />
        </div>
      );

    case "insights-reporting":
      return (
        <div className="h-full min-h-0 overflow-y-auto">
          <InsightsTab />
          <div className="border-t border-border px-6 py-4">
            <ActivityTab />
          </div>
        </div>
      );

    case "engagement-community":
      if (module === "linkedin" || module === "social") {
        return <EngagementHelperPage />;
      }
      return (
        <CategoryPlaceholder
          title="Engagement & Community"
          description="Comment helper, DM checks, and outreach pipeline — coming soon for this channel."
          storyIds={["TCA-088", "TCA-089", "TCA-090"]}
          module={module}
        />
      );

    case "assets-ingestion":
      return (
        <CategoryPlaceholder
          title="Assets & Ingestion"
          description="Upload documents, images, and code blocks for multimodal scoring."
          storyIds={["TCA-007", "TCA-079", "TCA-009"]}
          module={module}
        />
      );

    case "personas-audience":
      return (
        <CategoryPlaceholder
          title="Personas & Audience Context"
          description="Define who you are talking to — audiences, personas, brand voice, and ICP tracks."
          storyIds={["TCA-001", "TCA-002", "TCA-077"]}
          module={module}
        />
      );

    default:
      return (
        <CategoryPlaceholder
          title="Workspace"
          description="Select a category from the left navigation."
          storyIds={["TCA-014"]}
          module={module}
        />
      );
  }
}
