import { cn } from "@/lib/utils";

export function RoleBadge({ label }: { label: string }) {
  return (
    <span
      className={cn(
        "inline-flex items-center rounded-full bg-brand-50 px-2 py-0.5 text-xs font-medium text-brand-700 ring-1 ring-inset ring-brand-200",
      )}
    >
      {label}
    </span>
  );
}
