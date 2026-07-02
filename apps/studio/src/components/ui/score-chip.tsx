import { cn } from "@/lib/utils";
import { scoreTone, scoreToneClass } from "@/lib/utils";

export function ScoreChip({
  score,
  max = 10,
  label,
  className,
}: {
  score: number;
  max?: number;
  label?: string;
  className?: string;
}) {
  const tone = scoreTone(score, max);
  const display = max === 10 ? `${score.toFixed(1)}/10` : `${Math.round(score)}`;

  return (
    <span
      className={cn(
        "inline-flex items-center gap-1 rounded-md border px-2 py-0.5 font-mono text-xs font-semibold tabular-nums",
        scoreToneClass(tone),
        className,
      )}
      role="status"
      aria-label={label ?? `Score ${display}`}
    >
      {display}
    </span>
  );
}

export function ScoreGauge({
  score,
  max = 100,
  label,
  size = "lg",
}: {
  score: number;
  max?: number;
  label?: string;
  size?: "sm" | "lg";
}) {
  const clamped = Math.max(0, Math.min(max, score));
  const tone = scoreTone(clamped, max);
  const dim = size === "lg" ? "h-28 w-28 text-4xl border-[6px]" : "h-16 w-16 text-xl border-4";

  return (
    <div className="flex flex-col items-center gap-2" role="img" aria-label={`${label ?? "Score"} ${clamped} of ${max}`}>
      <div
        className={cn(
          "flex items-center justify-center rounded-full border-surface-overlay bg-surface-raised font-display font-bold tabular-nums shadow-card",
          dim,
          tone === "success" && "text-success",
          tone === "warning" && "text-warning",
          tone === "danger" && "text-danger",
        )}
      >
        {clamped}
      </div>
      {label ? (
        <p className="max-w-[12rem] text-center text-xs text-muted-foreground">{label}</p>
      ) : null}
    </div>
  );
}
