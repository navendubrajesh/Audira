import { GitCompare, Loader2, Sparkles, Wand2 } from "lucide-react";
import { useState } from "react";

import { AntiGenericWizard, PersonaPicker } from "@studio/components/analyzer/persona-picker";
import { MultimodalDropZone } from "@studio/components/analyzer/multimodal-drop-zone";
import { Button } from "@studio/components/ui/button";
import { FeedbackCard } from "@studio/components/ui/feedback-card";
import { ScoreGauge } from "@studio/components/ui/score-chip";
import { StoryIdBadge } from "@studio/components/ui/badge";
import { cn } from "@studio/lib/utils";
import { rewriteAssist } from "@studio/services/analyzer";
import { useAnalyzerStore } from "@studio/store/analyzer-store";
import { useUiStore } from "@studio/store/ui-store";

// TODO(TCA-091): Persist split ratio per user
// TODO(TCA-092): Markdown toolbar with code-block insert
export function AnalyzerWorkspace() {
  const {
    draftText,
    setDraftText,
    compositeScore,
    feedback,
    highlightedCategoryId,
    setHighlightedCategoryId,
    isScoring,
    variant,
    setVariant,
  } = useAnalyzerStore();
  const { mainSplitRatio, setMainSplitRatio } = useUiStore();
  const [showWizard, setShowWizard] = useState(false);
  const [rewriteMsg, setRewriteMsg] = useState<string | null>(null);

  const activeHighlight = feedback.find((f) => f.id === highlightedCategoryId);

  return (
    <div className="flex h-full flex-col">
      <header className="flex flex-wrap items-center gap-4 border-b border-border bg-surface-raised px-4 py-3">
        <ScoreGauge score={compositeScore} label="Composite effectiveness (TCA-038)" size="sm" />
        <div className="flex items-center gap-2">
          <StoryIdBadge id="TCA-038" />
          <StoryIdBadge id="TCA-091" />
          <StoryIdBadge id="TCA-083" />
        </div>
        <div className="ml-auto flex flex-wrap gap-2">
          <Button
            variant={variant === "A" ? "default" : "outline"}
            size="sm"
            onClick={() => setVariant("A")}
            aria-pressed={variant === "A"}
          >
            <GitCompare className="h-3.5 w-3.5" />
            Variant A
          </Button>
          <Button
            variant={variant === "B" ? "default" : "outline"}
            size="sm"
            onClick={() => setVariant("B")}
            aria-pressed={variant === "B"}
          >
            Variant B
          </Button>
          <Button variant="outline" size="sm" onClick={() => setShowWizard(true)}>
            <Sparkles className="h-3.5 w-3.5" />
            Anti-generic
          </Button>
          <Button
            variant="secondary"
            size="sm"
            onClick={async () => {
              const msg = await rewriteAssist(draftText);
              setRewriteMsg(msg);
            }}
          >
            <Wand2 className="h-3.5 w-3.5" />
            Rewrite assist
          </Button>
        </div>
      </header>

      {rewriteMsg ? (
        <div className="border-b border-warning/30 bg-warning/10 px-4 py-2 text-xs text-warning">
          {rewriteMsg} — TCA-037 guardrail: human review required.
        </div>
      ) : null}

      <div className="flex min-h-0 flex-1">
        <div
          className="flex min-w-0 flex-col border-r border-border"
          style={{ width: `${mainSplitRatio * 100}%` }}
        >
          <div className="space-y-3 border-b border-border p-4">
            <PersonaPicker />
            <MultimodalDropZone />
          </div>
          <label className="sr-only" htmlFor="draft-editor">
            Draft editor
          </label>
          <textarea
            id="draft-editor"
            value={draftText}
            onChange={(e) => setDraftText(e.target.value)}
            className="min-h-0 flex-1 resize-none bg-surface p-4 font-mono text-sm leading-relaxed focus:outline-none"
            spellCheck
          />
          {activeHighlight ? (
            <p className="border-t border-border px-4 py-2 text-xs text-muted-foreground">
              Highlighting: {activeHighlight.category} (chars{" "}
              {activeHighlight.highlightStart}–{activeHighlight.highlightEnd})
            </p>
          ) : null}
        </div>

        <div
          className="w-1 shrink-0 cursor-col-resize bg-border hover:bg-primary/30"
          role="separator"
          aria-orientation="vertical"
          aria-label="Resize editor and feedback panels"
          onMouseDown={(e) => {
            e.preventDefault();
            const startX = e.clientX;
            const startR = mainSplitRatio;
            const onMove = (ev: MouseEvent) => {
              const container = (e.target as HTMLElement).parentElement;
              if (!container) return;
              const delta = (ev.clientX - startX) / container.clientWidth;
              setMainSplitRatio(startR + delta);
            };
            const onUp = () => {
              window.removeEventListener("mousemove", onMove);
              window.removeEventListener("mouseup", onUp);
            };
            window.addEventListener("mousemove", onMove);
            window.addEventListener("mouseup", onUp);
          }}
        />

        <aside
          className="flex min-w-0 flex-1 flex-col bg-surface-overlay/30"
          aria-label="Live feedback matrix"
          aria-live="polite"
        >
          <div className="flex items-center gap-2 border-b border-border px-4 py-2">
            <h3 className="font-display text-sm font-semibold">4-part feedback matrix</h3>
            {isScoring ? (
              <Loader2 className="h-4 w-4 animate-spin text-primary" aria-label="Scoring" />
            ) : null}
            <StoryIdBadge id="TCA-087" />
          </div>
          <div className="scrollbar-thin flex-1 space-y-3 overflow-y-auto p-4">
            {feedback.map((item) => (
              <FeedbackCard
                key={item.id}
                item={item}
                active={highlightedCategoryId === item.id}
                onClick={() =>
                  setHighlightedCategoryId(
                    highlightedCategoryId === item.id ? null : item.id,
                  )
                }
              />
            ))}
          </div>
        </aside>
      </div>

      {showWizard ? <AntiGenericWizard onClose={() => setShowWizard(false)} /> : null}
    </div>
  );
}

export function ComposeTab({ module }: { module: string }) {
  return (
    <div className="h-full overflow-y-auto p-6">
      <h2 className="font-display text-lg font-semibold">Compose — {module}</h2>
      <p className="mt-1 text-sm text-muted-foreground">
        Draft editor placeholder. Switch to Analyze for the signature split-panel workspace.
      </p>
      <textarea
        className="mt-4 h-64 w-full rounded-lg border border-border bg-surface-raised p-4 font-mono text-sm"
        defaultValue="Start composing your message…"
        aria-label="Compose editor"
      />
    </div>
  );
}

export function GenericTabPlaceholder({
  tab,
  storyIds,
  children,
}: {
  tab: string;
  storyIds: string[];
  children?: React.ReactNode;
}) {
  return (
    <div className={cn("h-full overflow-y-auto p-6")}>
      {children ?? (
        <>
          <h2 className="font-display text-lg font-semibold capitalize">{tab}</h2>
          <p className="mt-1 text-sm text-muted-foreground">
            Placeholder screen — wired to routing with mock data.
          </p>
        </>
      )}
      <div className="mt-4 grid gap-3 sm:grid-cols-2">
        {storyIds.map((id) => (
          <div key={id} className="rounded-lg border border-border p-3 text-xs">
            Feature stub — {id}
          </div>
        ))}
      </div>
    </div>
  );
}
