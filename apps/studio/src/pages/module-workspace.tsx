import { useParams } from "react-router-dom";

import {
  AnalyzerWorkspace,
  ComposeTab,
  GenericTabPlaceholder,
} from "@studio/components/analyzer/analyzer-workspace";
import { ScheduleTabPlaceholder } from "@studio/components/shared/schedule-tab";
import { ActivityTab, InsightsTab } from "@studio/components/shared/activity-insights-tabs";
import { VerticalEpicGrid } from "@studio/pages/governance/index";
import { EngagementHelperPage } from "@studio/pages/engagement-helper";
import type { ModuleId } from "@studio/types";

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

const TAB_STORIES: Record<string, string[]> = {
  schedule: ["TCA-011", "TCA-013"],
  insights: ["TCA-014", "TCA-038"],
  assets: ["TCA-079", "TCA-009"],
  activity: ["TCA-013", "TCA-061"],
};

export function ModuleWorkspace({ module }: { module: ModuleId }) {
  const { contextId, tab } = useParams();

  if (module === "linkedin" && contextId === "engagement") {
    return <EngagementHelperPage />;
  }

  const activeTab = tab ?? "compose";

  if (activeTab === "analyze") {
    if (module === "linkedin" || module === "social" || module === "blog" || module === "placement") {
      return <AnalyzerWorkspace module={module} />;
    }
    return (
      <GenericTabPlaceholder tab="analyze" storyIds={["TCA-038", "TCA-083"]}>
        <h2 className="font-display text-lg font-semibold">Analyze</h2>
        <p className="text-sm text-muted-foreground">
          Open LinkedIn module for the full split-panel analyzer workspace.
        </p>
      </GenericTabPlaceholder>
    );
  }

  if (activeTab === "compose") {
    return (
      <div className="h-full overflow-y-auto">
        <ComposeTab module={module} />
        <div className="px-6 pb-6">
          <VerticalEpicGrid epicPrefixes={EPIC_MAP[module] ?? []} />
        </div>
      </div>
    );
  }

  if (activeTab === "schedule") {
    return (
      <div className="h-full overflow-y-auto">
        <ScheduleTabPlaceholder module={module} />
      </div>
    );
  }

  if (activeTab === "activity") {
    return <ActivityTab />;
  }

  if (activeTab === "insights") {
    return <InsightsTab />;
  }

  return (
    <div className="h-full overflow-y-auto">
      <GenericTabPlaceholder
        tab={activeTab}
        storyIds={TAB_STORIES[activeTab] ?? ["TCA-014"]}
      />
      <div className="px-6 pb-6">
        <VerticalEpicGrid epicPrefixes={EPIC_MAP[module] ?? []} />
      </div>
    </div>
  );
}
