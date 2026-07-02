import { Sparkles, UserCircle2 } from "lucide-react";

import { Button } from "@studio/components/ui/button";
import { StoryIdBadge } from "@studio/components/ui/badge";
import { useAnalyzerStore } from "@studio/store/analyzer-store";

// TODO(TCA-077): Persist persona preferences per tenant; fetch from audience library
export function PersonaPicker() {
  const { personas, personaId, setPersonaId } = useAnalyzerStore();

  return (
    <div className="rounded-lg border border-border bg-surface-raised p-3">
      <div className="mb-2 flex items-center gap-2">
        <UserCircle2 className="h-4 w-4 text-primary" />
        <h3 className="font-display text-sm font-semibold">Target persona</h3>
        <StoryIdBadge id="TCA-077" />
      </div>
      <div className="flex flex-wrap gap-2" role="radiogroup" aria-label="Target persona">
        {personas.map((p) => (
          <button
            key={p.id}
            type="button"
            role="radio"
            aria-checked={personaId === p.id}
            onClick={() => setPersonaId(p.id)}
            className={`rounded-full border px-3 py-1.5 text-xs font-medium transition ${
              personaId === p.id
                ? "border-primary bg-primary/10 text-primary"
                : "border-border hover:border-primary/40"
            }`}
          >
            {p.label}
          </button>
        ))}
      </div>
      <p className="mt-2 text-xs text-muted-foreground">
        {personas.find((p) => p.id === personaId)?.description}
      </p>
    </div>
  );
}

// TODO(TCA-078): Full wizard flow with saved anti-generic templates
export function AntiGenericWizard({ onClose }: { onClose: () => void }) {
  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4"
      role="dialog"
      aria-modal
      aria-labelledby="anti-generic-title"
    >
      <div className="max-w-md rounded-xl border border-border bg-surface-raised p-6 shadow-elevated">
        <div className="mb-3 flex items-center gap-2">
          <Sparkles className="h-5 w-5 text-accent" />
          <h2 id="anti-generic-title" className="font-display text-lg font-semibold">
            Anti-Generic prompter
          </h2>
          <StoryIdBadge id="TCA-078" />
        </div>
        <ol className="list-decimal space-y-2 pl-5 text-sm text-muted-foreground">
          <li>What did you ship or observe firsthand?</li>
          <li>What trade-off did you accept (latency, cost, compliance)?</li>
          <li>What would a sceptical peer push back on?</li>
        </ol>
        <div className="mt-4 flex justify-end gap-2">
          <Button variant="outline" onClick={onClose}>
            Skip
          </Button>
          <Button onClick={onClose}>Apply to draft</Button>
        </div>
      </div>
    </div>
  );
}
