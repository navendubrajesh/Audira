import { useCallback, useEffect, useState } from "react";

import { PermissionGate } from "@studio/components/auth/permission-gate";
import { Button } from "@studio/components/ui/button";
import { StoryIdBadge } from "@studio/components/ui/badge";
import { GlobalStatePanel } from "@studio/components/shared/global-states";
import {
  createStandard,
  listStandards,
  publishStandard,
  type StandardsRule,
} from "@studio/services/context-api";
import { ApiError } from "@studio/lib/api-client";

/** TCA-005 — Standards & policy library */
export function StandardsScreen() {
  const [rules, setRules] = useState<StandardsRule[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [pattern, setPattern] = useState("");
  const [replacement, setReplacement] = useState("");

  const load = useCallback(async () => {
    setLoading(true);
    try {
      setRules(await listStandards());
    } catch (e) {
      setError(e instanceof ApiError ? e.message : "Failed to load standards");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void load();
  }, [load]);

  async function handleCreate(e: React.FormEvent) {
    e.preventDefault();
    try {
      await createStandard({
        rule_type: "inclusive",
        pattern,
        replacement: replacement || undefined,
        status: "draft",
      });
      setPattern("");
      setReplacement("");
      await load();
    } catch (e) {
      setError(e instanceof ApiError ? e.message : "Create failed");
    }
  }

  if (loading) return <GlobalStatePanel variant="loading" />;

  return (
    <div>
      <div className="mb-4 flex items-center gap-2">
        <h2 className="font-display text-lg font-semibold">Standards library</h2>
        <StoryIdBadge id="TCA-005" />
      </div>
      {error ? <p className="mb-3 text-sm text-danger">{error}</p> : null}

      <PermissionGate permission="standards.manage">
        <form onSubmit={(e) => void handleCreate(e)} className="mb-6 flex flex-wrap gap-2">
          <input
            value={pattern}
            onChange={(e) => setPattern(e.target.value)}
            placeholder="Pattern to flag"
            className="h-9 min-w-[12rem] rounded-lg border border-border px-3 text-sm"
            required
          />
          <input
            value={replacement}
            onChange={(e) => setReplacement(e.target.value)}
            placeholder="Suggested replacement"
            className="h-9 min-w-[12rem] rounded-lg border border-border px-3 text-sm"
          />
          <Button type="submit" size="sm">
            Add rule
          </Button>
        </form>
      </PermissionGate>

      <div className="space-y-2">
        {rules.map((r) => (
          <div
            key={r.id}
            className="flex flex-wrap items-center justify-between gap-2 rounded-lg border border-border p-3 text-sm"
          >
            <div>
              <span className="font-mono text-xs">{r.pattern}</span>
              {r.replacement ? (
                <span className="ml-2 text-muted-foreground">→ {r.replacement}</span>
              ) : null}
              <p className="text-xs text-muted-foreground">
                {r.rule_type} · v{r.version} · {r.status}
              </p>
            </div>
            {r.status === "draft" ? (
              <PermissionGate permission="standards.manage" fallback={null}>
                <Button size="sm" variant="outline" onClick={() => void publishStandard(r.id).then(load)}>
                  Publish
                </Button>
              </PermissionGate>
            ) : null}
          </div>
        ))}
      </div>
    </div>
  );
}
