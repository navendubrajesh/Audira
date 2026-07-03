import { GitCompare, Loader2, Sparkles, Wand2, Zap } from "lucide-react";
import { useEffect, useState } from "react";

import { DraftEditor } from "@studio/components/analyzer/draft-editor";
import { AntiGenericWizard } from "@studio/components/analyzer/anti-generic-wizard";
import { PersonaPicker } from "@studio/components/analyzer/persona-picker";
import { MultimodalDropZone } from "@studio/components/analyzer/multimodal-drop-zone";
import { PermissionGate } from "@studio/components/auth/permission-gate";
import { Button } from "@studio/components/ui/button";
import { FeedbackCard } from "@studio/components/ui/feedback-card";
import { ScoreGauge } from "@studio/components/ui/score-chip";
import { StoryIdBadge } from "@studio/components/ui/badge";
import { cn } from "@studio/lib/utils";
import { rewriteAssist } from "@studio/services/analyzer";
import { useAnalyzerStore } from "@studio/store/analyzer-store";
import { useUiStore } from "@studio/store/ui-store";
import type { ModuleId } from "@studio/types";

export function AnalyzerWorkspace({ module = "linkedin" }: { module?: ModuleId }) {
  const {
    draftText,
    draftTextB,
    setDraftText,
    setDraftTextB,
    compositeScore,
    feedback,
    highlightedCategoryId,
    setHighlightedCategoryId,
    isScoring,
    variant,
    setVariant,
    fullAnalysis,
    setFullAnalysis,
    setModule,
    loadAudiences,
    runScore,
    runCompare,
    scoreError,
    canUpgrade,
    verdict,
    modelId,
  } = useAnalyzerStore();
  const { mainSplitRatio, setMainSplitRatio } = useUiStore();
  const [showWizard, setShowWizard] = useState(false);
  const [rewriteMsg, setRewriteMsg] = useState<string | null>(null);

  useEffect(() => {
    setModule(module);
    void loadAudiences().then(() => runScore());
  }, [module, setModule, loadAudiences, runScore]);

  const activeHighlight = feedback.find((f) => f.id === highlightedCategoryId);
  const editorValue = variant === "B" ? draftTextB || draftText : draftText;
  const setEditorValue = variant === "B" ? setDraftTextB : setDraftText;

  return (
    <PermissionGate permission="analyses.run">
      <div className="flex h-full min-h-0 flex-col">
        <header className="flex flex-wrap items-center gap-4 border-b border-border bg-surface-raised px-4 py-3">
          <ScoreGauge score={compositeScore} label="Composite effectiveness (TCA-038)" size="sm" />
          <div className="flex flex-wrap items-center gap-2 text-xs text-muted-foreground">
            {verdict ? <span className="capitalize">Verdict: {verdict.replace("_", " ")}</span> : null}
            {modelId ? <span>Model: {modelId}</span> : null}
            <StoryIdBadge id="TCA-038" />
            <StoryIdBadge id="TCA-091" />
            <StoryIdBadge id="TCA-083" />
          </div>
          <div className="ml-auto flex flex-wrap gap-2">
            <label className="flex items-center gap-1.5 rounded-md border border-border px-2 py-1 text-xs">
              <input
                type="checkbox"
                checked={fullAnalysis}
                onChange={(e) => setFullAnalysis(e.target.checked)}
              />
              Full neuro (TRIBE)
            </label>
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
            {canUpgrade ? (
              <Button variant="outline" size="sm" onClick={() => setFullAnalysis(true)}>
                <Zap className="h-3.5 w-3.5" />
                Upgrade analysis
              </Button>
            ) : null}
            <Button variant="outline" size="sm" onClick={() => setShowWizard(true)}>
              <Sparkles className="h-3.5 w-3.5" />
              Anti-generic
            </Button>
            <Button
              variant="secondary"
              size="sm"
              onClick={async () => {
                const msg = await rewriteAssist(draftText, module);
                setRewriteMsg(msg);
              }}
            >
              <Wand2 className="h-3.5 w-3.5" />
              Rewrite assist
            </Button>
            {draftTextB ? (
              <Button variant="outline" size="sm" onClick={() => void runCompare()}>
                Compare A/B
              </Button>
            ) : null}
          </div>
        </header>

        {scoreError ? (
          <div className="border-b border-danger/30 bg-danger/5 px-4 py-2 text-xs text-danger">
            {scoreError}
          </div>
        ) : null}

        {rewriteMsg ? (
          <div className="border-b border-warning/30 bg-warning/10 px-4 py-2 text-xs text-warning">
            {rewriteMsg} — TCA-037 guardrail: human review required.
          </div>
        ) : null}

        <div className="flex min-h-0 flex-1">
          <div
            className="flex min-h-0 min-w-0 flex-col border-r border-border"
            style={{ width: `${mainSplitRatio * 100}%` }}
          >
            <div className="space-y-3 border-b border-border p-4">
              <PersonaPicker />
              <MultimodalDropZone />
            </div>
            <DraftEditor
              value={editorValue}
              onChange={setEditorValue}
              highlightStart={activeHighlight?.highlightStart}
              highlightEnd={activeHighlight?.highlightEnd}
              className="bg-surface"
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
            className="flex min-h-0 min-w-0 flex-1 flex-col bg-surface-overlay/30"
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
            <div
              className="scrollbar-thin min-h-0 flex-1 space-y-3 overflow-y-auto p-4 focus:outline-none focus-visible:ring-2 focus-visible:ring-primary/40"
              tabIndex={0}
            >
              {feedback.length === 0 && !isScoring ? (
                <p className="text-sm text-muted-foreground">
                  Edit the draft to run live analysis against the API.
                </p>
              ) : null}
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
    </PermissionGate>
  );
}

export function ComposeTab({ module }: { module: string }) {
  return (
    <div className="h-full min-h-0 overflow-y-auto p-6">
      <h2 className="font-display text-lg font-semibold">Compose — {module}</h2>
      <p className="mt-1 text-sm text-muted-foreground">
        Draft editor placeholder. Switch to Analyze for the split-panel workspace wired to{" "}
        <code className="text-xs">POST /analyze</code>.
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
    <div className={cn("h-full min-h-0 overflow-y-auto p-6")}>
      {children ?? (
        <>
          <h2 className="font-display text-lg font-semibold capitalize">{tab}</h2>
          <p className="mt-1 text-sm text-muted-foreground">Tab placeholder.</p>
        </>
      )}
      <div className="mt-4 grid gap-3 sm:grid-cols-2">
        {storyIds.map((id) => (
          <div key={id} className="rounded-lg border border-border p-3 text-xs">
            {id}
          </div>
        ))}
      </div>
    </div>
  );
}
