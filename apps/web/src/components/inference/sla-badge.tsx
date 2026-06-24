export function SlaBadge({
  slaMet,
  latencyMs,
}: {
  slaMet: boolean;
  latencyMs: number;
}) {
  return (
    <span
      className={
        slaMet
          ? "text-xs text-emerald-700"
          : "text-xs text-amber-700"
      }
    >
      {slaMet
        ? `Completed within target latency (${latencyMs} ms)`
        : `Completed outside target latency (${latencyMs} ms) — flagged for review`}
    </span>
  );
}
