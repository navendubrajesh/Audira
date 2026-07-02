import { Calendar, Clock } from "lucide-react";
import { useCallback, useEffect, useState } from "react";

import { Button } from "@studio/components/ui/button";
import { GlobalStatePanel } from "@studio/components/shared/global-states";
import { StoryIdBadge } from "@studio/components/ui/badge";
import { listSchedule, publishDraft, type ScheduleItem } from "@studio/services/studio-api";
import type { ModuleId } from "@studio/types";

export function ScheduleTabPlaceholder({ module }: { module: ModuleId | string }) {
  const [items, setItems] = useState<ScheduleItem[]>([]);
  const [loading, setLoading] = useState(true);

  const load = useCallback(async () => {
    setLoading(true);
    try {
      setItems(await listSchedule());
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void load();
  }, [load]);

  const filtered = items.filter((i) => i.vertical === module || module === "home");

  if (loading) return <GlobalStatePanel variant="loading" />;

  return (
    <div className="h-full overflow-y-auto p-6">
      <div className="flex items-center gap-2">
        <h2 className="font-display text-lg font-semibold">Schedule — {module}</h2>
        <StoryIdBadge id="TCA-011" />
      </div>
      <p className="mt-1 text-sm text-muted-foreground">
        Publishing queue from <code className="text-xs">/studio/schedule</code>
      </p>

      <div className="mt-6 grid gap-4 lg:grid-cols-2">
        <div className="rounded-lg border border-border bg-surface-raised p-4 shadow-card">
          <div className="mb-4 flex items-center gap-2">
            <Calendar className="h-4 w-4 text-primary" />
            <h3 className="text-sm font-semibold">Scheduled items</h3>
          </div>
          <ul className="space-y-3">
            {filtered.map((item) => (
              <li key={item.id} className="rounded-md border border-border p-3 text-sm">
                <p className="font-medium">{item.title}</p>
                <p className="text-xs text-muted-foreground">
                  {item.channel} · {new Date(item.scheduled_at).toLocaleString()}
                </p>
                <Button
                  size="sm"
                  variant="outline"
                  className="mt-2"
                  onClick={() => void publishDraft(item.draft_id).then(load)}
                >
                  Publish now
                </Button>
              </li>
            ))}
            {filtered.length === 0 ? (
              <li className="text-xs text-muted-foreground">No scheduled items for this vertical.</li>
            ) : null}
          </ul>
        </div>
        <div className="rounded-lg border border-border bg-surface-raised p-4 shadow-card">
          <div className="mb-3 flex items-center gap-2">
            <Clock className="h-4 w-4 text-accent" />
            <h3 className="text-sm font-semibold">All channels</h3>
          </div>
          <ul className="space-y-2 text-sm">
            {items.map((item) => (
              <li key={item.id} className="flex justify-between gap-2 border-b border-border py-2">
                <span className="truncate">{item.title}</span>
                <span className="shrink-0 text-xs text-muted-foreground">{item.vertical}</span>
              </li>
            ))}
          </ul>
        </div>
      </div>
    </div>
  );
}
