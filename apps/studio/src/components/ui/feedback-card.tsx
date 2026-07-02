import { ChevronRight } from "lucide-react";

import { ScoreChip } from "@studio/components/ui/score-chip";
import { StoryIdBadge } from "@studio/components/ui/badge";
import type { FeedbackCategory } from "@studio/types";
import { cn, scoreTone } from "@studio/lib/utils";

export function FeedbackCard({
  item,
  active,
  onClick,
}: {
  item: FeedbackCategory;
  active?: boolean;
  onClick?: () => void;
}) {
  const tone = scoreTone(item.score, item.maxScore);

  return (
    <button
      type="button"
      onClick={onClick}
      className={cn(
        "w-full rounded-lg border bg-surface-raised p-4 text-left shadow-card transition hover:border-primary/40",
        active && "border-primary ring-1 ring-primary/30",
        tone === "danger" && !active && "border-danger/20",
      )}
      aria-pressed={active}
      aria-label={`${item.category}, score ${item.score} of ${item.maxScore}`}
    >
      <div className="mb-2 flex items-start justify-between gap-2">
        <h4 className="font-display text-sm font-semibold leading-snug">{item.category}</h4>
        <ScoreChip score={item.score} max={item.maxScore} />
      </div>
      <p className="mb-2 text-sm text-muted-foreground">{item.insight}</p>
      <div className="flex items-start gap-1.5 rounded-md bg-surface-overlay p-2 text-xs">
        <ChevronRight className="mt-0.5 h-3.5 w-3.5 shrink-0 text-primary" aria-hidden />
        <p>
          <span className="font-semibold text-slate-800 dark:text-slate-100">Fix: </span>
          {item.recommendedFix}
        </p>
      </div>
      <div className="mt-2 flex flex-wrap gap-1">
        {item.storyIds.map((id) => (
          <StoryIdBadge key={id} id={id} />
        ))}
      </div>
    </button>
  );
}
