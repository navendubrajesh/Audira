import { useCallback, useEffect, useState } from "react";

import { PermissionGate } from "@studio/components/auth/permission-gate";
import { Button } from "@studio/components/ui/button";
import { StoryIdBadge } from "@studio/components/ui/badge";
import { GlobalStatePanel } from "@studio/components/shared/global-states";
import { listAuditLog, type AuditEntry } from "@studio/services/governance-api";
import { ApiError } from "@studio/lib/api-client";

/** TCA-061 / audit — append-only access log */
export function AuditLogScreen() {
  const [entries, setEntries] = useState<AuditEntry[]>([]);
  const [total, setTotal] = useState(0);
  const [offset, setOffset] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const limit = 25;

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const data = await listAuditLog(limit, offset);
      setEntries(data.entries);
      setTotal(data.total);
    } catch (e) {
      setError(e instanceof ApiError ? e.message : "Failed to load audit log");
    } finally {
      setLoading(false);
    }
  }, [offset]);

  useEffect(() => {
    void load();
  }, [load]);

  return (
    <PermissionGate permission="audit.view">
      <div>
        <div className="mb-4 flex items-center gap-2">
          <h2 className="font-display text-lg font-semibold">Audit log</h2>
          <StoryIdBadge id="TCA-061" />
        </div>
        {loading ? <GlobalStatePanel variant="loading" /> : null}
        {error ? <p className="mb-3 text-sm text-danger">{error}</p> : null}

        {!loading && !error ? (
          <>
            <div className="overflow-x-auto rounded-lg border border-border">
              <table className="w-full text-left text-sm">
                <thead className="bg-surface-overlay text-xs uppercase text-muted-foreground">
                  <tr>
                    <th className="px-4 py-3">Time</th>
                    <th className="px-4 py-3">Action</th>
                    <th className="px-4 py-3">Actor</th>
                    <th className="px-4 py-3">Resource</th>
                  </tr>
                </thead>
                <tbody>
                  {entries.map((e) => (
                    <tr key={e.id} className="border-t border-border">
                      <td className="px-4 py-3 text-xs whitespace-nowrap">
                        {new Date(e.created_at).toLocaleString()}
                      </td>
                      <td className="px-4 py-3 font-mono text-xs">{e.action}</td>
                      <td className="px-4 py-3 text-xs">{e.actor_email ?? "—"}</td>
                      <td className="px-4 py-3 text-xs text-muted-foreground">{e.resource ?? "—"}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
            <div className="mt-4 flex items-center gap-2">
              <Button
                variant="outline"
                size="sm"
                disabled={offset === 0}
                onClick={() => setOffset(Math.max(0, offset - limit))}
              >
                Previous
              </Button>
              <span className="text-xs text-muted-foreground">
                {offset + 1}–{Math.min(offset + limit, total)} of {total}
              </span>
              <Button
                variant="outline"
                size="sm"
                disabled={offset + limit >= total}
                onClick={() => setOffset(offset + limit)}
              >
                Next
              </Button>
            </div>
          </>
        ) : null}
      </div>
    </PermissionGate>
  );
}
