import { Link } from "react-router-dom";
import { useEffect, useState } from "react";
import {
  Bar,
  BarChart,
  CartesianGrid,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import { FeatureGrid } from "@studio/components/shared/feature-card";
import { PermissionGate } from "@studio/components/auth/permission-gate";
import { getAnalyticsDashboard } from "@studio/services/features-api";
import { getInferenceMetrics } from "@studio/services/governance-api";
import { ScoreChip } from "@studio/components/ui/score-chip";
import { StoryIdBadge } from "@studio/components/ui/badge";
import {
  attentionQueue,
  commsHealthWidgets,
  scheduledItems,
  storiesForEpic,
} from "@studio/mock/fixtures";
import type { DraftItem } from "@studio/types";

const EPICS = [
  "E01", "E02", "E03", "E04", "E05", "E06", "E07", "E08", "E09", "E10", "E11",
  "E12", "E13", "E14", "E15", "E16", "E17", "E18", "E19", "E20", "E21", "E22",
];

const trendData = [
  { week: "W1", score: 62, predicted: 58 },
  { week: "W2", score: 68, predicted: 65 },
  { week: "W3", score: 71, predicted: 70 },
  { week: "W4", score: 74, predicted: 72 },
];

const channelData = [
  { channel: "LinkedIn", score: 78 },
  { channel: "Social", score: 65 },
  { channel: "Blog", score: 82 },
  { channel: "Placement", score: 71 },
];

const VERTICAL_PATH: Partial<Record<DraftItem["vertical"], string>> = {
  social: "/social",
  linkedin: "/linkedin",
  placement: "/placement",
  blog: "/blog",
  analytics: "/analytics",
  assets: "/assets",
  governance: "/governance",
  settings: "/settings",
};

export function AnalyticsDashboard() {
  const e14 = storiesForEpic("E14").map((s) => s.ID);
  const [dashboard, setDashboard] = useState<{
    avg_composite_score: number;
    analyses_count: number;
    by_channel: Array<{ channel: string; avg_score: number; count: number }>;
  } | null>(null);
  const [inference, setInference] = useState<{
    jobs_completed: number;
    p95_latency_ms: number;
    monthly_spend_usd: number;
    monthly_cap_usd: number;
  } | null>(null);

  const channelChart =
    dashboard?.by_channel.map((c) => ({
      channel: c.channel,
      score: c.avg_score,
    })) ?? channelData;

  useEffect(() => {
    void getAnalyticsDashboard().then(setDashboard).catch(() => setDashboard(null));
    void getInferenceMetrics()
      .then(setInference)
      .catch(() => setInference(null));
  }, []);

  return (
    <div className="h-full overflow-y-auto p-6">
      <h2 className="font-display text-xl font-semibold">Analytics & Insights Console</h2>
      <p className="text-sm text-muted-foreground">
        E14 — {dashboard ? `${dashboard.analyses_count} analyses · avg ${dashboard.avg_composite_score}` : "Loading…"}
      </p>

      <PermissionGate permission="audit.view">
        {inference ? (
          <div className="mt-4 grid gap-3 sm:grid-cols-4">
            <div className="rounded-lg border border-border p-3 text-sm">
              <p className="text-xs text-muted-foreground">Jobs completed</p>
              <p className="font-display text-xl font-bold">{inference.jobs_completed}</p>
            </div>
            <div className="rounded-lg border border-border p-3 text-sm">
              <p className="text-xs text-muted-foreground">P95 latency</p>
              <p className="font-display text-xl font-bold">{inference.p95_latency_ms}ms</p>
            </div>
            <div className="rounded-lg border border-border p-3 text-sm">
              <p className="text-xs text-muted-foreground">Monthly spend</p>
              <p className="font-display text-xl font-bold">${inference.monthly_spend_usd.toFixed(2)}</p>
            </div>
            <div className="rounded-lg border border-border p-3 text-sm">
              <p className="text-xs text-muted-foreground">Spend cap</p>
              <p className="font-display text-xl font-bold">${inference.monthly_cap_usd.toFixed(0)}</p>
            </div>
          </div>
        ) : null}
      </PermissionGate>

      <div className="mt-6 grid gap-4 lg:grid-cols-2">
        <div className="rounded-lg border border-border bg-surface-raised p-4 shadow-card">
          <h3 className="mb-3 text-sm font-semibold">Effectiveness trend</h3>
          <ResponsiveContainer width="100%" height={200}>
            <LineChart data={trendData}>
              <CartesianGrid strokeDasharray="3 3" opacity={0.3} />
              <XAxis dataKey="week" tick={{ fontSize: 11 }} />
              <YAxis domain={[50, 90]} tick={{ fontSize: 11 }} />
              <Tooltip />
              <Line type="monotone" dataKey="score" stroke="hsl(172 66% 32%)" strokeWidth={2} />
              <Line type="monotone" dataKey="predicted" stroke="hsl(32 95% 44%)" strokeDasharray="4 4" />
            </LineChart>
          </ResponsiveContainer>
        </div>
        <div className="rounded-lg border border-border bg-surface-raised p-4 shadow-card">
          <h3 className="mb-3 text-sm font-semibold">Score by vertical</h3>
          <ResponsiveContainer width="100%" height={200}>
            <BarChart data={channelChart}>
              <CartesianGrid strokeDasharray="3 3" opacity={0.3} />
              <XAxis dataKey="channel" tick={{ fontSize: 11 }} />
              <YAxis domain={[0, 100]} tick={{ fontSize: 11 }} />
              <Tooltip />
              <Bar dataKey="score" fill="hsl(172 66% 32%)" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      <div className="mt-6">
        <h3 className="mb-3 font-display text-sm font-semibold">Epic E14 features</h3>
        <FeatureGrid storyIds={e14} />
      </div>
    </div>
  );
}

export function HomeDashboard() {
  return (
    <div className="h-full overflow-y-auto p-6">
      <h1 className="font-display text-2xl font-bold">Command Center</h1>
      <p className="text-sm text-muted-foreground">
        Cross-channel attention queue, comms health, and upcoming scheduled items.
      </p>

      <div className="mt-6 grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        {channelData.map((c) => (
          <div
            key={c.channel}
            className="rounded-lg border border-border bg-surface-raised p-4 shadow-card"
          >
            <p className="text-xs font-medium uppercase text-muted-foreground">{c.channel}</p>
            <div className="mt-2 flex items-end justify-between">
              <ScoreChip score={c.score / 10} max={10} />
              <span className="text-2xl font-display font-bold tabular-nums">{c.score}</span>
            </div>
          </div>
        ))}
      </div>

      <section className="mt-8">
        <h2 className="mb-3 font-display text-sm font-semibold">Comms health (E14)</h2>
        <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
          {commsHealthWidgets.map((w) => (
            <div
              key={w.label}
              className="rounded-lg border border-border bg-surface-raised p-4 shadow-card"
            >
              <div className="flex items-center justify-between gap-2">
                <p className="text-xs font-medium text-muted-foreground">{w.label}</p>
                <StoryIdBadge id={w.storyId} />
              </div>
              <p className="mt-2 font-display text-2xl font-bold tabular-nums">
                {w.value}
                {w.unit ? ` ${w.unit}` : ""}
              </p>
              <p className="mt-1 text-xs text-muted-foreground">{w.delta}</p>
            </div>
          ))}
        </div>
      </section>

      <section className="mt-8 grid gap-6 lg:grid-cols-2">
        <div className="rounded-lg border border-border bg-surface-raised p-4 shadow-card">
          <h2 className="mb-3 font-display text-sm font-semibold">Attention queue</h2>
          <ul className="space-y-2">
            {attentionQueue.map((item) => (
              <li key={item.id}>
                <Link
                  to={`${VERTICAL_PATH[item.vertical] ?? "/home"}/${item.id}/analyze`}
                  className="flex items-center gap-3 rounded-md px-2 py-2 hover:bg-surface-overlay"
                >
                  <ScoreChip score={(item.compositeScore ?? 0) / 10} max={10} />
                  <div className="min-w-0 flex-1">
                    <p className="truncate text-sm font-medium">{item.title}</p>
                    <p className="truncate text-xs text-muted-foreground">{item.excerpt}</p>
                  </div>
                  <span className="text-xs capitalize text-muted-foreground">{item.vertical}</span>
                </Link>
              </li>
            ))}
          </ul>
        </div>

        <div className="rounded-lg border border-border bg-surface-raised p-4 shadow-card">
          <h2 className="mb-3 font-display text-sm font-semibold">Upcoming scheduled</h2>
          <ul className="space-y-2">
            {scheduledItems.map((item) => (
              <li key={item.id}>
                <Link
                  to={`${VERTICAL_PATH[item.vertical] ?? "/home"}/${item.id}/schedule`}
                  className="flex items-center gap-3 rounded-md px-2 py-2 hover:bg-surface-overlay"
                >
                  <span className="rounded-full bg-primary/10 px-2 py-0.5 text-[10px] font-semibold uppercase text-primary">
                    Scheduled
                  </span>
                  <div className="min-w-0 flex-1">
                    <p className="truncate text-sm font-medium">{item.title}</p>
                    <p className="truncate text-xs text-muted-foreground">{item.excerpt}</p>
                  </div>
                </Link>
              </li>
            ))}
          </ul>
        </div>
      </section>

      <div className="mt-8">
        <h2 className="mb-3 font-display text-sm font-semibold">All epics (E01–E22)</h2>
        <div className="grid gap-2 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
          {EPICS.map((epic) => {
            const stories = storiesForEpic(epic);
            const name = stories[0]?.Epic.replace(/^E\d+\s*/, "") ?? epic;
            return (
              <div
                key={epic}
                className="rounded-lg border border-border bg-surface-raised px-3 py-2 text-xs shadow-card"
              >
                <p className="font-display font-semibold">{epic}</p>
                <p className="truncate text-muted-foreground">{name}</p>
                <p className="mt-1 tabular-nums text-muted-foreground">{stories.length} stories</p>
              </div>
            );
          })}
        </div>
      </div>

      <div className="mt-8">
        <h2 className="mb-3 font-display text-sm font-semibold">Phase 1 MVP features (E01, E14)</h2>
        <FeatureGrid storyIds={["TCA-001", "TCA-002", "TCA-003", "TCA-014", "TCA-038"]} />
      </div>
    </div>
  );
}
