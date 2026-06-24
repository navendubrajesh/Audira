import { cn } from "@/lib/utils";

type Variant = "info" | "success" | "warning";

const variants: Record<Variant, string> = {
  info: "bg-brand-50 text-brand-700 ring-brand-200",
  success: "bg-emerald-50 text-emerald-700 ring-emerald-200",
  warning: "bg-amber-50 text-amber-700 ring-amber-200",
};

export function StatusBadge({
  label,
  variant = "info",
}: {
  label: string;
  variant?: Variant;
}) {
  return (
    <span
      className={cn(
        "inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium ring-1 ring-inset",
        variants[variant],
      )}
    >
      {label}
    </span>
  );
}
