import { useCallback, useEffect, useState } from "react";

import { PermissionGate } from "@studio/components/auth/permission-gate";
import { Button } from "@studio/components/ui/button";
import { StoryIdBadge } from "@studio/components/ui/badge";
import { listApprovals, transitionApproval, type ApprovalItem } from "@studio/services/studio-api";

export function ApprovalsBoard() {
  const [items, setItems] = useState<ApprovalItem[]>([]);

  const load = useCallback(async () => {
    try {
      setItems(await listApprovals());
    } catch {
      setItems([]);
    }
  }, []);

  useEffect(() => {
    void load();
  }, [load]);

  const lanes = [
    { key: "pending_review", label: "Pending review" },
    { key: "in_approval", label: "In approval" },
    { key: "approved", label: "Approved" },
    { key: "rejected", label: "Rejected" },
  ] as const;

  return (
    <PermissionGate permission="standards.manage">
      <section className="mt-8 rounded-lg border border-border bg-surface-raised p-4 shadow-card">
        <div className="mb-3 flex items-center gap-2">
          <h2 className="font-display text-sm font-semibold">Approval workflow board (E13)</h2>
          <StoryIdBadge id="TCA-013" />
        </div>
        <div className="grid gap-3 md:grid-cols-4">
          {lanes.map((lane) => (
            <div key={lane.key} className="rounded-md border border-border bg-surface p-3">
              <h3 className="text-xs font-semibold uppercase text-muted-foreground">{lane.label}</h3>
              <ul className="mt-2 space-y-2">
                {items
                  .filter((i) => i.status === lane.key)
                  .map((item) => (
                    <li key={item.id} className="rounded border border-border bg-surface-raised p-2 text-xs">
                      <p className="font-medium">{item.title}</p>
                      {lane.key === "pending_review" ? (
                        <div className="mt-2 flex gap-1">
                          <Button
                            size="sm"
                            variant="outline"
                            onClick={() =>
                              void transitionApproval(item.id, "approved").then(load)
                            }
                          >
                            Approve
                          </Button>
                          <Button
                            size="sm"
                            variant="ghost"
                            onClick={() =>
                              void transitionApproval(item.id, "rejected").then(load)
                            }
                          >
                            Reject
                          </Button>
                        </div>
                      ) : null}
                    </li>
                  ))}
              </ul>
            </div>
          ))}
        </div>
      </section>
    </PermissionGate>
  );
}
