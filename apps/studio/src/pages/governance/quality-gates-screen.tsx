import { useCallback, useEffect, useState } from "react";

import { PermissionGate } from "@studio/components/auth/permission-gate";
import { StoryIdBadge } from "@studio/components/ui/badge";
import { GlobalStatePanel } from "@studio/components/shared/global-states";
import { getQualityGates, updateQualityGates, type QualityGates } from "@studio/services/context-api";
import { ApiError } from "@studio/lib/api-client";

/** Quality gates — org publish thresholds */
export function QualityGatesScreen() {
  const [gates, setGates] = useState<QualityGates | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async () => {
    setLoading(true);
    try {
      setGates(await getQualityGates());
    } catch (e) {
      setError(e instanceof ApiError ? e.message : "Failed to load quality gates");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void load();
  }, [load]);

  async function save(updates: Partial<QualityGates>) {
    try {
      setGates(await updateQualityGates(updates));
    } catch (e) {
      setError(e instanceof ApiError ? e.message : "Update failed");
    }
  }

  if (loading) return <GlobalStatePanel variant="loading" />;
  if (!gates) return <GlobalStatePanel variant="error" actionLabel="Retry" onAction={() => void load()} />;

  return (
    <PermissionGate permission="standards.manage">
      <div>
        <div className="mb-4 flex items-center gap-2">
          <h2 className="font-display text-lg font-semibold">Quality gates</h2>
          <StoryIdBadge id="TCA-052" />
        </div>
        {error ? <p className="mb-3 text-sm text-danger">{error}</p> : null}

        <div className="max-w-md space-y-4">
          <label className="block text-sm">
            Pass threshold (composite score)
            <input
              type="number"
              min={0}
              max={100}
              value={gates.pass_threshold}
              onChange={(e) => void save({ pass_threshold: Number(e.target.value) })}
              className="mt-1 w-full rounded-lg border border-border px-3 py-2"
            />
          </label>
          <label className="block text-sm">
            Needs-work threshold
            <input
              type="number"
              min={0}
              max={100}
              value={gates.needs_work_threshold}
              onChange={(e) => void save({ needs_work_threshold: Number(e.target.value) })}
              className="mt-1 w-full rounded-lg border border-border px-3 py-2"
            />
          </label>
          <label className="flex items-center gap-2 text-sm">
            <input
              type="checkbox"
              checked={gates.block_publish_on_fail}
              onChange={(e) => void save({ block_publish_on_fail: e.target.checked })}
            />
            Block publish when below pass threshold
          </label>
        </div>
      </div>
    </PermissionGate>
  );
}
