import { useCallback, useEffect, useState } from "react";

import { PermissionGate } from "@studio/components/auth/permission-gate";
import { Button } from "@studio/components/ui/button";
import { StoryIdBadge } from "@studio/components/ui/badge";
import { GlobalStatePanel } from "@studio/components/shared/global-states";
import { getBrandProfile, updateBrandProfile, type BrandProfile } from "@studio/services/context-api";
import { ApiError } from "@studio/lib/api-client";

/** TCA-002 — Brand voice & messaging codification */
export function BrandScreen() {
  const [brand, setBrand] = useState<BrandProfile | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [targetTone, setTargetTone] = useState("professional");
  const [doTerms, setDoTerms] = useState("");
  const [dontTerms, setDontTerms] = useState("");
  const [pillars, setPillars] = useState("");

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const data = await getBrandProfile();
      setBrand(data);
      setTargetTone(data.target_tone);
      setDoTerms(data.terminology_do.join(", "));
      setDontTerms(data.terminology_dont.join(", "));
      setPillars(data.messaging_pillars.join(", "));
    } catch (e) {
      setError(e instanceof ApiError ? e.message : "Failed to load brand profile");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void load();
  }, [load]);

  async function handleSave(e: React.FormEvent) {
    e.preventDefault();
    setSaving(true);
    setError(null);
    try {
      await updateBrandProfile({
        target_tone: targetTone,
        terminology_do: doTerms.split(",").map((s) => s.trim()).filter(Boolean),
        terminology_dont: dontTerms.split(",").map((s) => s.trim()).filter(Boolean),
        messaging_pillars: pillars.split(",").map((s) => s.trim()).filter(Boolean),
        voice_attributes: brand?.voice_attributes ?? {},
      });
      await load();
    } catch (e) {
      setError(e instanceof ApiError ? e.message : "Save failed");
    } finally {
      setSaving(false);
    }
  }

  if (loading) return <GlobalStatePanel variant="loading" />;

  return (
    <PermissionGate permission="brand.manage">
      <div>
        <div className="mb-4 flex items-center gap-2">
          <h2 className="font-display text-lg font-semibold">Brand voice</h2>
          <StoryIdBadge id="TCA-002" />
          {brand ? (
            <span className="text-xs text-muted-foreground">v{brand.version}</span>
          ) : null}
        </div>
        {error ? <p className="mb-3 text-sm text-danger">{error}</p> : null}

        <form onSubmit={(e) => void handleSave(e)} className="max-w-xl space-y-4">
          <label className="block text-sm font-medium">
            Target tone
            <input
              value={targetTone}
              onChange={(e) => setTargetTone(e.target.value)}
              className="mt-1 w-full rounded-lg border border-border px-3 py-2 text-sm"
            />
          </label>
          <label className="block text-sm font-medium">
            Terminology — do use
            <input
              value={doTerms}
              onChange={(e) => setDoTerms(e.target.value)}
              className="mt-1 w-full rounded-lg border border-border px-3 py-2 text-sm"
              placeholder="customers, team members"
            />
          </label>
          <label className="block text-sm font-medium">
            Terminology — avoid
            <input
              value={dontTerms}
              onChange={(e) => setDontTerms(e.target.value)}
              className="mt-1 w-full rounded-lg border border-border px-3 py-2 text-sm"
              placeholder="guys, rockstar"
            />
          </label>
          <label className="block text-sm font-medium">
            Messaging pillars
            <input
              value={pillars}
              onChange={(e) => setPillars(e.target.value)}
              className="mt-1 w-full rounded-lg border border-border px-3 py-2 text-sm"
            />
          </label>
          <Button type="submit" disabled={saving}>
            {saving ? "Saving…" : "Publish brand profile"}
          </Button>
        </form>
      </div>
    </PermissionGate>
  );
}
