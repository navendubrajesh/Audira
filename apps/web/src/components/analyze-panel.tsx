"use client";

import { useState } from "react";

import { ScoreGauge } from "@/components/score-gauge";
import type { SessionUser } from "@/lib/auth";

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

type Audience = {
  id: string;
  name: string;
};

type AnalyzeResult = {
  id: string;
  composite_score: number | null;
  result: {
    metrics: Record<string, { score?: number }>;
    rewrite_suggestions?: Array<{ type: string; suggestion: string }>;
  };
};

export function AnalyzePanel({ token }: { token: string; user: SessionUser }) {
  const [text, setText] = useState(
    "Thank you for your commitment. We appreciate your support as we share this update with all team members.",
  );
  const [audiences, setAudiences] = useState<Audience[]>([]);
  const [audienceId, setAudienceId] = useState("");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<AnalyzeResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  async function loadAudiences() {
    const res = await fetch(`${API_URL}/audiences`, {
      headers: { Authorization: `Bearer ${token}` },
    });
    if (res.ok) {
      const data = await res.json();
      setAudiences(data);
      if (data[0]) setAudienceId(data[0].id);
    }
  }

  async function runAnalysis() {
    setLoading(true);
    setError(null);
    try {
      if (audiences.length === 0) await loadAudiences();
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
          objective: "engage",
          channel: "email",
        }),
      });
      if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        throw new Error(err.detail ?? "Analysis failed");
      }
      setResult(await res.json());
    } catch (e) {
      setError(e instanceof Error ? e.message : "Analysis failed");
    } finally {
      setLoading(false);
    }
  }

  return (
    <section className="mt-12 rounded-xl border border-neutral-200 bg-white p-6 shadow-sm">
      <h2 className="text-lg font-semibold text-neutral-900">Communications analysis</h2>
      <p className="mt-1 text-sm text-neutral-500">
        Fast-lane scoring with TRIBE v2 neuro mapping — TCA-001 through TCA-038
      </p>
      <textarea
        className="mt-4 w-full rounded-lg border border-neutral-300 p-3 text-sm"
        rows={5}
        value={text}
        onChange={(e) => setText(e.target.value)}
      />
      <div className="mt-4 flex flex-wrap gap-3">
        <button
          type="button"
          onClick={() => void loadAudiences()}
          className="rounded-md border border-neutral-300 px-3 py-1.5 text-sm hover:bg-neutral-50"
        >
          Load audiences
        </button>
        <button
          type="button"
          disabled={loading}
          onClick={() => void runAnalysis()}
          className="rounded-md bg-brand-600 px-4 py-1.5 text-sm font-semibold text-white hover:bg-brand-700 disabled:opacity-50"
        >
          {loading ? "Analyzing…" : "Run analysis"}
        </button>
      </div>
      {audiences.length > 0 ? (
        <select
          className="mt-3 rounded-md border border-neutral-300 px-2 py-1 text-sm"
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
      {error ? <p className="mt-3 text-sm text-red-600">{error}</p> : null}
      {result?.composite_score != null ? (
        <div className="mt-6 grid gap-6 lg:grid-cols-2">
          <ScoreGauge score={result.composite_score} label="Composite effectiveness" />
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
