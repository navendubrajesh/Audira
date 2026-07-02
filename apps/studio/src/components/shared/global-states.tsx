import type { ComponentType } from "react";
import { AlertTriangle, Inbox, Loader2, Lock, WifiOff } from "lucide-react";

import { Button } from "@studio/components/ui/button";
import { cn } from "@studio/lib/utils";

type GlobalStateVariant = "empty" | "loading" | "error" | "no-connection" | "permission-denied";

const CONFIG: Record<
  GlobalStateVariant,
  { icon: ComponentType<{ className?: string }>; title: string; description: string }
> = {
  empty: {
    icon: Inbox,
    title: "Nothing here yet",
    description: "Create a draft or connect a channel to get started.",
  },
  loading: {
    icon: Loader2,
    title: "Loading",
    description: "Fetching the latest scores and context…",
  },
  error: {
    icon: AlertTriangle,
    title: "Something went wrong",
    description: "We could not load this view. Your draft content is preserved.",
  },
  "no-connection": {
    icon: WifiOff,
    title: "No connection",
    description: "Integrations are offline. Publish and live scoring are disabled until reconnected.",
  },
  "permission-denied": {
    icon: Lock,
    title: "Permission denied",
    description: "Your role does not include access to this module. Contact an admin (TCA-067).",
  },
};

export function GlobalStatePanel({
  variant,
  actionLabel,
  onAction,
  className,
}: {
  variant: GlobalStateVariant;
  actionLabel?: string;
  onAction?: () => void;
  className?: string;
}) {
  const { icon: Icon, title, description } = CONFIG[variant];
  const spinning = variant === "loading";

  return (
    <div
      className={cn(
        "flex flex-col items-center justify-center px-6 py-16 text-center",
        className,
      )}
      role={variant === "loading" ? "status" : "alert"}
      aria-live="polite"
    >
      <Icon
        className={cn(
          "mb-4 h-10 w-10 text-muted-foreground",
          spinning && "animate-spin text-primary",
        )}
        aria-hidden
      />
      <h3 className="font-display text-lg font-semibold">{title}</h3>
      <p className="mt-2 max-w-sm text-sm text-muted-foreground">{description}</p>
      {actionLabel && onAction ? (
        <Button className="mt-6" onClick={onAction}>
          {actionLabel}
        </Button>
      ) : null}
    </div>
  );
}
