import { cn } from "@/lib/utils";

export function ScoreGauge({
  score,
  label,
  className,
}: {
  score: number;
  label?: string;
  className?: string;
}) {
  const clamped = Math.max(0, Math.min(100, score));
  const tone =
    clamped >= 75 ? "text-success" : clamped >= 50 ? "text-warning" : "text-danger";

  return (
    <div className={cn("flex flex-col items-center gap-4", className)}>
      <div
        className="relative flex h-40 w-40 items-center justify-center rounded-full border-8 border-neutral-100"
        role="img"
        aria-label={`Score ${clamped} out of 100`}
      >
        <span className={cn("text-5xl font-bold tabular-nums", tone)}>
          {clamped}
        </span>
      </div>
      {label ? (
        <p className="text-sm font-medium text-neutral-600">{label}</p>
      ) : null}
    </div>
  );
}
