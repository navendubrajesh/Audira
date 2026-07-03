import { useCallback, useEffect, useState } from "react";

import { Button } from "@studio/components/ui/button";
import { GlobalStatePanel } from "@studio/components/shared/global-states";
import { StoryIdBadge } from "@studio/components/ui/badge";
import {
  addRunComment,
  listAnalysisRuns,
  listRunComments,
} from "@studio/services/features-api";
import { useAnalyzerStore } from "@studio/store/analyzer-store";

export function ActivityTab() {
  const analysisId = useAnalyzerStore((s) => s.analysisId);
  const [comments, setComments] = useState<
    Array<{ id: string; body: string; author_email: string; resolved: boolean }>
  >([]);
  const [body, setBody] = useState("");
  const [loading, setLoading] = useState(false);

  const load = useCallback(async () => {
    if (!analysisId) return;
    setLoading(true);
    try {
      setComments(await listRunComments(analysisId));
    } finally {
      setLoading(false);
    }
  }, [analysisId]);

  useEffect(() => {
    void load();
  }, [load]);

  if (!analysisId) {
    return (
      <div className="p-6 text-sm text-muted-foreground">
        Run analysis on the Analyze tab to enable activity comments (TCA-053).
      </div>
    );
  }

  return (
    <div className="h-full min-h-0 overflow-y-auto p-6 focus:outline-none focus-visible:ring-2 focus-visible:ring-primary/40" tabIndex={0}>
      <div className="mb-4 flex items-center gap-2">
        <h2 className="font-display text-lg font-semibold">Activity</h2>
        <StoryIdBadge id="TCA-053" />
      </div>
      {loading ? <GlobalStatePanel variant="loading" className="py-8" /> : null}
      <ul className="mb-4 space-y-2">
        {comments.map((c) => (
          <li key={c.id} className="rounded-lg border border-border p-3 text-sm">
            <p className="text-xs text-muted-foreground">{c.author_email}</p>
            <p>{c.body}</p>
          </li>
        ))}
      </ul>
      <div className="flex gap-2">
        <input
          className="flex-1 rounded-lg border border-border px-3 py-2 text-sm"
          placeholder="Add review comment…"
          value={body}
          onChange={(e) => setBody(e.target.value)}
        />
        <Button
          onClick={() =>
            void addRunComment(analysisId, body).then(() => {
              setBody("");
              void load();
            })
          }
        >
          Post
        </Button>
      </div>
    </div>
  );
}

export function InsightsTab() {
  const [runs, setRuns] = useState<
    Array<{ id: string; composite_score: number; objective: string; verdict: string; created_at: string }>
  >([]);

  useEffect(() => {
    void listAnalysisRuns().then(setRuns).catch(() => setRuns([]));
  }, []);

  return (
    <div className="h-full min-h-0 overflow-y-auto p-6 focus:outline-none focus-visible:ring-2 focus-visible:ring-primary/40" tabIndex={0}>
      <div className="mb-4 flex items-center gap-2">
        <h2 className="font-display text-lg font-semibold">Insights</h2>
        <StoryIdBadge id="TCA-014" />
        <StoryIdBadge id="TCA-038" />
      </div>
      <div className="overflow-x-auto rounded-lg border border-border">
        <table className="w-full text-left text-sm">
          <thead className="bg-surface-overlay text-xs uppercase text-muted-foreground">
            <tr>
              <th className="px-4 py-3">Run</th>
              <th className="px-4 py-3">Score</th>
              <th className="px-4 py-3">Objective</th>
              <th className="px-4 py-3">Verdict</th>
              <th className="px-4 py-3">When</th>
            </tr>
          </thead>
          <tbody>
            {runs.map((r) => (
              <tr key={r.id} className="border-t border-border">
                <td className="px-4 py-3 font-mono text-xs">{r.id.slice(0, 8)}…</td>
                <td className="px-4 py-3">{r.composite_score}</td>
                <td className="px-4 py-3">{r.objective ?? "—"}</td>
                <td className="px-4 py-3 capitalize">{r.verdict ?? "—"}</td>
                <td className="px-4 py-3 text-xs">{new Date(r.created_at).toLocaleString()}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
