import { useCallback, useEffect, useState } from "react";

import { PermissionGate } from "@studio/components/auth/permission-gate";
import { Button } from "@studio/components/ui/button";
import { StoryIdBadge } from "@studio/components/ui/badge";
import {
  getGuardrailSettings,
  updateGuardrailSettings,
} from "@studio/services/features-api";

export function GuardrailsScreen() {
  const [settings, setSettings] = useState({
    generative_governance: false,
    rewrite_assist: false,
    regulated_claims: false,
    block_on_fail: false,
  });

  const load = useCallback(async () => {
    const s = await getGuardrailSettings();
    setSettings(s);
  }, []);

  useEffect(() => {
    void load();
  }, [load]);

  async function toggle(key: keyof typeof settings) {
    const next = { ...settings, [key]: !settings[key] };
    await updateGuardrailSettings(next);
    setSettings(next);
  }

  return (
    <PermissionGate permission="standards.manage">
      <div>
        <div className="mb-4 flex items-center gap-2">
          <h2 className="font-display text-lg font-semibold">AI guardrails</h2>
          <StoryIdBadge id="TCA-037" />
          <StoryIdBadge id="TCA-044" />
          <StoryIdBadge id="TCA-060" />
        </div>
        <div className="max-w-lg space-y-3">
          {(
            [
              ["generative_governance", "Generative AI governance (TCA-037)"],
              ["rewrite_assist", "Rewrite assist — human in loop (TCA-044)"],
              ["regulated_claims", "Regulated claims detection (TCA-060)"],
              ["block_on_fail", "Block publish on guardrail fail"],
            ] as const
          ).map(([key, label]) => (
            <label key={key} className="flex items-center justify-between rounded-lg border border-border p-3 text-sm">
              {label}
              <input
                type="checkbox"
                checked={settings[key]}
                onChange={() => void toggle(key)}
              />
            </label>
          ))}
        </div>
        <Button className="mt-4" variant="outline" onClick={() => void load()}>
          Refresh
        </Button>
      </div>
    </PermissionGate>
  );
}
