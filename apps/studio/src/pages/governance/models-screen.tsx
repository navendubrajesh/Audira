import { useCallback, useEffect, useState } from "react";

import { StoryIdBadge } from "@studio/components/ui/badge";
import { GlobalStatePanel } from "@studio/components/shared/global-states";
import { listModels, listValidationMetrics, type ModelEntry } from "@studio/services/governance-api";
import { ApiError } from "@studio/lib/api-client";

/** TCA-016 / TCA-019 — Model registry & validation */
export function ModelsScreen() {
  const [models, setModels] = useState<ModelEntry[]>([]);
  const [metrics, setMetrics] = useState<
    Array<{ metric_name: string; accuracy: number; sample_size: number; methodology: string }>
  >([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const [m, v] = await Promise.all([listModels(), listValidationMetrics()]);
      setModels(m);
      setMetrics(v);
    } catch (e) {
      setError(e instanceof ApiError ? e.message : "Failed to load model registry");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void load();
  }, [load]);

  if (loading) return <GlobalStatePanel variant="loading" />;
  if (error) {
    return (
      <GlobalStatePanel variant="error" actionLabel="Retry" onAction={() => void load()} />
    );
  }

  return (
    <div>
      <div className="mb-4 flex items-center gap-2">
        <h2 className="font-display text-lg font-semibold">Model registry</h2>
        <StoryIdBadge id="TCA-016" />
        <StoryIdBadge id="TCA-019" />
      </div>

      <div className="space-y-3">
        {models.map((m) => (
          <div key={m.model_id} className="rounded-lg border border-border p-4">
            <div className="flex flex-wrap items-center justify-between gap-2">
              <p className="font-mono text-sm font-semibold">{m.model_id}</p>
              <span className="text-xs text-muted-foreground">v{m.version}</span>
            </div>
            <dl className="mt-2 grid gap-2 text-xs sm:grid-cols-2">
              <div>
                <dt className="text-muted-foreground">Licence</dt>
                <dd>{m.licence}</dd>
              </div>
              <div>
                <dt className="text-muted-foreground">Commercial OK</dt>
                <dd className={m.commercial_ok ? "text-success" : "text-danger"}>
                  {m.commercial_ok ? "Yes" : "Review required"}
                </dd>
              </div>
              <div>
                <dt className="text-muted-foreground">Modalities</dt>
                <dd>{m.modalities.join(", ")}</dd>
              </div>
              <div>
                <dt className="text-muted-foreground">Status</dt>
                <dd>{m.status}</dd>
              </div>
            </dl>
          </div>
        ))}
      </div>

      {metrics.length ? (
        <section className="mt-8">
          <h3 className="mb-3 text-sm font-semibold">Validation metrics (TCA-063)</h3>
          <div className="overflow-x-auto rounded-lg border border-border">
            <table className="w-full text-left text-sm">
              <thead className="bg-surface-overlay text-xs uppercase text-muted-foreground">
                <tr>
                  <th className="px-4 py-3">Metric</th>
                  <th className="px-4 py-3">Accuracy</th>
                  <th className="px-4 py-3">Sample</th>
                  <th className="px-4 py-3">Method</th>
                </tr>
              </thead>
              <tbody>
                {metrics.map((v) => (
                  <tr key={v.metric_name} className="border-t border-border">
                    <td className="px-4 py-3">{v.metric_name}</td>
                    <td className="px-4 py-3">{(v.accuracy * 100).toFixed(1)}%</td>
                    <td className="px-4 py-3">{v.sample_size}</td>
                    <td className="px-4 py-3 text-xs">{v.methodology}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>
      ) : null}
    </div>
  );
}
