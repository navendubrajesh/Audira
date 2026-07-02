import { UserCircle2 } from "lucide-react";
import { useEffect } from "react";

import { StoryIdBadge } from "@studio/components/ui/badge";
import { useAnalyzerStore } from "@studio/store/analyzer-store";

/** TCA-077 — Dynamic target persona / audience picker (API-backed) */
export function PersonaPicker() {
  const { audiences, audienceId, setAudienceId, loadAudiences } = useAnalyzerStore();

  useEffect(() => {
    void loadAudiences();
  }, [loadAudiences]);

  return (
    <div className="rounded-lg border border-border bg-surface-raised p-3">
      <div className="mb-2 flex items-center gap-2">
        <UserCircle2 className="h-4 w-4 text-primary" />
        <h3 className="font-display text-sm font-semibold">Target audience</h3>
        <StoryIdBadge id="TCA-077" />
      </div>
      {audiences.length ? (
        <div className="flex flex-wrap gap-2" role="radiogroup" aria-label="Target audience">
          {audiences.map((a) => (
            <button
              key={a.id}
              type="button"
              role="radio"
              aria-checked={audienceId === a.id}
              onClick={() => setAudienceId(a.id)}
              className={`rounded-full border px-3 py-1.5 text-xs font-medium transition ${
                audienceId === a.id
                  ? "border-primary bg-primary/10 text-primary"
                  : "border-border hover:border-primary/40"
              }`}
            >
              {a.name}
            </button>
          ))}
        </div>
      ) : (
        <p className="text-xs text-muted-foreground">
          Sign in to load audience library (TCA-001).
        </p>
      )}
      {audiences.find((a) => a.id === audienceId) ? (
        <p className="mt-2 text-xs text-muted-foreground">
          {audiences.find((a) => a.id === audienceId)?.role} ·{" "}
          {audiences.find((a) => a.id === audienceId)?.region}
        </p>
      ) : null}
    </div>
  );
}

export { AntiGenericWizard } from "@studio/components/analyzer/anti-generic-wizard";
