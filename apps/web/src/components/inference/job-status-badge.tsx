import { cn } from "@/lib/utils";

const STATUS_STYLES: Record<string, string> = {
  queued: "bg-neutral-100 text-neutral-700 ring-neutral-200",
  running: "bg-brand-50 text-brand-700 ring-brand-200",
  completed: "bg-emerald-50 text-emerald-700 ring-emerald-200",
  cached: "bg-brand-50 text-brand-700 ring-brand-200",
  failed: "bg-red-50 text-red-700 ring-red-200",
};

const STATUS_LABELS: Record<string, string> = {
  queued: "Queued",
  running: "Running analysis",
  completed: "Complete",
  cached: "Retrieved from cache",
  failed: "Failed",
};

export function JobStatusBadge({ status }: { status: string }) {
  return (
    <span
      className={cn(
        "inline-flex rounded-full px-2 py-0.5 text-xs font-medium ring-1 ring-inset",
        STATUS_STYLES[status] ?? STATUS_STYLES.queued,
      )}
    >
      {STATUS_LABELS[status] ?? status}
    </span>
  );
}
