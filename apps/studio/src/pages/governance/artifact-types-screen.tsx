import { useCallback, useEffect, useState } from "react";

import { StoryIdBadge } from "@studio/components/ui/badge";
import { GlobalStatePanel } from "@studio/components/shared/global-states";
import { listArtifactTypes, type ArtifactType } from "@studio/services/context-api";
import { ApiError } from "@studio/lib/api-client";

/** TCA-004 — Artifact taxonomy & engineering exclusion */
export function ArtifactTypesScreen() {
  const [types, setTypes] = useState<ArtifactType[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async () => {
    setLoading(true);
    try {
      setTypes(await listArtifactTypes());
    } catch (e) {
      setError(e instanceof ApiError ? e.message : "Failed to load artifact types");
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
        <h2 className="font-display text-lg font-semibold">Artifact taxonomy</h2>
        <StoryIdBadge id="TCA-004" />
      </div>
      <p className="mb-4 text-sm text-muted-foreground">
        Engineering artifacts are blocked from comms analysis per scope policy.
      </p>
      <div className="overflow-x-auto rounded-lg border border-border">
        <table className="w-full text-left text-sm">
          <thead className="bg-surface-overlay text-xs uppercase text-muted-foreground">
            <tr>
              <th className="px-4 py-3">Code</th>
              <th className="px-4 py-3">Label</th>
              <th className="px-4 py-3">Checks</th>
              <th className="px-4 py-3">Engineering</th>
            </tr>
          </thead>
          <tbody>
            {types.map((t) => (
              <tr
                key={t.id}
                className={`border-t border-border ${t.block_engineering ? "bg-danger/5" : ""}`}
              >
                <td className="px-4 py-3 font-mono text-xs">{t.code}</td>
                <td className="px-4 py-3 font-medium">{t.label}</td>
                <td className="px-4 py-3 text-xs">{t.checks.join(", ") || "—"}</td>
                <td className="px-4 py-3">
                  {t.block_engineering ? (
                    <span className="text-xs font-semibold text-danger">Blocked</span>
                  ) : (
                    <span className="text-xs text-success">In scope</span>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
