import { cva, type VariantProps } from "class-variance-authority";

import { cn } from "@studio/lib/utils";

const badgeVariants = cva(
  "inline-flex items-center rounded-full border px-2 py-0.5 text-[11px] font-semibold uppercase tracking-wide",
  {
    variants: {
      variant: {
        default: "border-border bg-surface-overlay text-muted-foreground",
        done: "border-success/30 bg-success/10 text-success",
        partial: "border-warning/30 bg-warning/10 text-warning",
        todo: "border-border bg-muted text-muted-foreground",
        story: "border-primary/30 bg-primary/10 text-primary font-mono normal-case",
        phase: "border-accent/30 bg-accent/10 text-accent",
      },
    },
    defaultVariants: { variant: "default" },
  },
);

export function Badge({
  className,
  variant,
  ...props
}: React.HTMLAttributes<HTMLSpanElement> & VariantProps<typeof badgeVariants>) {
  return (
    <span className={cn(badgeVariants({ variant }), className)} {...props} />
  );
}

export function BacklogStatusBadge({ status }: { status: string }) {
  const variant =
    status === "Done" ? "done" : status === "Partial" ? "partial" : "todo";
  return <Badge variant={variant}>{status}</Badge>;
}

export function StoryIdBadge({ id }: { id: string }) {
  return (
    <Badge variant="story" title={`Backlog story ${id}`}>
      {id}
    </Badge>
  );
}
