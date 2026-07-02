import { Sparkles } from "lucide-react";

import { Button } from "@studio/components/ui/button";
import { StoryIdBadge } from "@studio/components/ui/badge";

/** TCA-078 — Anti-generic frictionless prompter wizard */
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
