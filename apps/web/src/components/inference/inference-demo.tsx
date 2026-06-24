"use client";

import { useCallback, useState } from "react";

import { JobStatusBadge } from "@/components/inference/job-status-badge";
import { SlaBadge } from "@/components/inference/sla-badge";
import { getApiUrl, getSessionToken } from "@/lib/auth";

type JobState = {
  id: string;
  status: string;
  latency_ms: number | null;
  sla_met: boolean | null;
  cost_usd: number | null;
  cached: boolean;
  result: Record<string, unknown> | null;
};

export function InferenceDemo() {
  const [modality, setModality] = useState<"text" | "multimodal">("text");
  const [modelId, setModelId] = useState("facebook/tribev2");
  const [job, setJob] = useState<JobState | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const pollJob = useCallback(async (jobId: string, token: string) => {
    for (let i = 0; i < 30; i++) {
      const res = await fetch(`${getApiUrl()}/inference/jobs/${jobId}`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (!res.ok) break;
      const data = await res.json();
      setJob(data);
      if (["completed", "cached", "failed"].includes(data.status)) return;
      await new Promise((r) => setTimeout(r, 500));
    }
  }, []);

  async function handleSubmit() {
    const token = getSessionToken();
    if (!token) {
      setError("Your session has expired. Please sign in again.");
      return;
    }
    setLoading(true);
    setError(null);
    setJob(null);
    try {
      const res = await fetch(`${getApiUrl()}/inference/jobs`, {
        method: "POST",
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          modality,
          model_id: modelId,
          payload: { sample: true, text: "Sample communication artifact" },
        }),
      });
      if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        throw new Error(err.detail ?? "Submit failed");
      }
      const data = await res.json();
      setJob(data);
      if (data.status === "queued") {
        await pollJob(data.id, token);
      }
    } catch (e) {
      setError(e instanceof Error ? e.message : "Submit failed");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="mt-4 space-y-4">
      <div className="flex flex-wrap items-center gap-3">
        <select
          value={modelId}
          onChange={(e) => setModelId(e.target.value)}
          className="rounded-md border border-neutral-300 px-3 py-2 text-sm"
        >
          <option value="facebook/tribev2">TRIBE v2 (facebook/tribev2)</option>
          <option value="tribe-v2-stub">Stub (no GPU)</option>
        </select>
        <select
          value={modality}
          onChange={(e) => setModality(e.target.value as "text" | "multimodal")}
          className="rounded-md border border-neutral-300 px-3 py-2 text-sm"
        >
          <option value="text">Text (SLA &lt; 2s)</option>
          <option value="multimodal">Multimodal (SLA &lt; 60s)</option>
        </select>
        <button
          type="button"
          onClick={handleSubmit}
          disabled={loading}
          className="rounded-md bg-brand-600 px-4 py-2 text-sm font-semibold text-white hover:bg-brand-700 disabled:opacity-50"
        >
          {loading ? "Running analysis…" : "Run sample analysis"}
        </button>
      </div>

      {error ? <p className="text-sm text-danger">{error}</p> : null}

      {job ? (
        <div className="rounded-lg border border-neutral-100 bg-neutral-50 p-4">
          <div className="flex flex-wrap items-center gap-2">
            <JobStatusBadge status={job.status} />
            {job.cached ? (
              <span className="text-xs text-brand-600">Retrieved from cache</span>
            ) : null}
            {job.sla_met != null && job.latency_ms != null ? (
              <SlaBadge slaMet={job.sla_met} latencyMs={job.latency_ms} />
            ) : null}
          </div>
          {job.cost_usd != null ? (
            <p className="mt-2 text-xs text-neutral-500">
              Estimated cost: ${job.cost_usd.toFixed(4)}
            </p>
          ) : null}
          {job.result ? (
            <pre className="mt-3 overflow-x-auto rounded bg-white p-2 text-xs text-neutral-700">
              {JSON.stringify(job.result, null, 2)}
            </pre>
          ) : null}
        </div>
      ) : null}
    </div>
  );
}
