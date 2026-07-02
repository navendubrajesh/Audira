"use client";

import { useEffect, useState } from "react";

import { ScoreGauge } from "@/components/score-gauge";
import type { SessionUser } from "@/lib/auth";

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

const OBJECTIVES = ["inform", "engage", "drive_action", "reassure", "celebrate"] as const;

type Audience = { id: string; name: string };

type AnalyzeResult = {
  id: string;
  composite_score: number | null;
  result: {
    metrics: Record<string, { score?: number }>;
    verdict?: { label: string };
    rewrite_suggestions?: Array<{ type: string; suggestion: string }>;
    can_upgrade?: boolean;
  };
};

export function AnalyzePanel({ token }: { token: string; user: SessionUser }) {
  const [text, setText] = useState(
    "Thank you for your commitment. We appreciate your support as we share this update with all team members.",
  );
  const [audiences, setAudiences] = useState<Audience[]>([]);
  const [audienceId, setAudienceId] = useState("");
  const [objective, setObjective] = useState<(typeof OBJECTIVES)[number]>("engage");
  const [fullAnalysis, setFullAnalysis] = useState(false);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<AnalyzeResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    void (async () => {
      const res = await fetch(`${API_URL}/audiences`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (res.ok) {
        const data = await res.json();
        setAudiences(data);
        if (data[0]) setAudienceId(data[0].id);
      }
    })();
  }, [token]);

  async function runAnalysis(upgrade = false) {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch(`${API_URL}/analyze`, {
        method: "POST",
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          text,
          audience_id: audienceId || undefined,
          artifact_type_code: "email",
          objective,
          channel: "email",
          fast_lane: !upgrade && !fullAnalysis,
          full_analysis: upgrade || fullAnalysis,
        }),
      });
      if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        throw new Error(typeof err.detail === "string" ? err.detail : "Analysis failed");
      }
      setResult(await res.json());
    } catch (e) {
      setError(e instanceof Error ? e.message : "Analysis failed");
    } finally {
      setLoading(false);
    }
  }

  const verdict = result?.result?.verdict?.label;

  return (
    <section className="mt-12 rounded-xl border border-neutral-200 bg-white p-6 shadow-sm">
      <h2 className="text-lg font-semibold text-neutral-900">Communications analysis</h2>
      <p className="mt-1 text-sm text-neutral-500">
        Fast lane (&lt;2s, no GPU) or full TRIBE neuro analysis
      </p>
      <textarea
        className="mt-4 w-full rounded-lg border border-neutral-300 p-3 text-sm"
        rows={5}
        value={text}
        onChange={(e) => setText(e.target.value)}
      />
      <div className="mt-3 flex flex-wrap gap-3">
        <select
          className="rounded-md border border-neutral-300 px-2 py-1 text-sm"
          value={objective}
          onChange={(e) => setObjective(e.target.value as (typeof OBJECTIVES)[number])}
        >
          {OBJECTIVES.map((o) => (
            <option key={o} value={o}>
              {o}
            </option>
          ))}
        </select>
        {audiences.length > 0 ? (
          <select
            className="rounded-md border border-neutral-300 px-2 py-1 text-sm"
            value={audienceId}
            onChange={(e) => setAudienceId(e.target.value)}
          >
            {audiences.map((a) => (
              <option key={a.id} value={a.id}>
                {a.name}
              </option>
            ))}
          </select>
        ) : null}
        <label className="flex items-center gap-2 text-sm text-neutral-600">
          <input
            type="checkbox"
            checked={fullAnalysis}
            onChange={(e) => setFullAnalysis(e.target.checked)}
          />
          Full neuro analysis
        </label>
      </div>
      <div className="mt-4 flex flex-wrap gap-3">
        <button
          type="button"
          disabled={loading}
          onClick={() => void runAnalysis(false)}
          className="rounded-md bg-brand-600 px-4 py-1.5 text-sm font-semibold text-white hover:bg-brand-700 disabled:opacity-50"
        >
          {loading ? "Analyzing…" : "Run fast analysis"}
        </button>
        {result?.result?.can_upgrade ? (
          <button
            type="button"
            disabled={loading}
            onClick={() => void runAnalysis(true)}
            className="rounded-md border border-brand-600 px-4 py-1.5 text-sm font-semibold text-brand-600 hover:bg-brand-50 disabled:opacity-50"
          >
            Upgrade to full analysis
          </button>
        ) : null}
      </div>
      {error ? <p className="mt-3 text-sm text-red-600">{error}</p> : null}
      {result?.composite_score != null ? (
        <div className="mt-6 grid gap-6 lg:grid-cols-2">
          <div>
            <ScoreGauge score={result.composite_score} label="Composite effectiveness" />
            {verdict ? (
              <p className="mt-2 text-sm capitalize text-neutral-600">
                Verdict: <span className="font-medium">{verdict.replace("_", " ")}</span>
              </p>
            ) : null}
          </div>
          <div className="text-sm text-neutral-600">
            <p className="font-medium text-neutral-800">Metric breakdown</p>
            <ul className="mt-2 space-y-1">
              {Object.entries(result.result.metrics).map(([key, val]) =>
                typeof val === "object" && val && "score" in val ? (
                  <li key={key}>
                    {key}: {val.score}
                  </li>
                ) : null,
              )}
            </ul>
          </div>
        </div>
      ) : null}
    </section>
  );
}
