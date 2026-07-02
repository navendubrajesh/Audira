import { useEffect, useState } from "react";

import { StoryIdBadge } from "@studio/components/ui/badge";
import { listIntegrations } from "@studio/services/features-api";

export function IntegrationsScreen() {
  const [items, setItems] = useState<Array<{ id: string; status: string; endpoint?: string }>>([]);

  useEffect(() => {
    void listIntegrations().then((r) => setItems(r.integrations));
  }, []);

  return (
    <div>
      <div className="mb-4 flex items-center gap-2">
        <h2 className="font-display text-lg font-semibold">Integrations</h2>
        <StoryIdBadge id="TCA-036" />
        <StoryIdBadge id="TCA-048" />
      </div>
      <ul className="space-y-2">
        {items.map((i) => (
          <li
            key={i.id}
            className="flex items-center justify-between rounded-lg border border-border p-3 text-sm"
          >
            <span className="font-medium">{i.id}</span>
            <span className="text-xs capitalize text-muted-foreground">{i.status}</span>
          </li>
        ))}
      </ul>
    </div>
  );
}
