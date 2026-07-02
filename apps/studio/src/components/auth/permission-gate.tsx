import type { ReactNode } from "react";

import { GlobalStatePanel } from "@studio/components/shared/global-states";
import { useAuthStore } from "@studio/store/auth-store";

export function PermissionGate({
  permission,
  children,
  fallback,
}: {
  permission: string;
  children: ReactNode;
  fallback?: ReactNode;
}) {
  const can = useAuthStore((s) => s.can(permission));

  if (!can) {
    return (
      fallback ?? (
        <GlobalStatePanel
          variant="permission-denied"
          actionLabel="Back to Command Center"
          onAction={() => {
            window.location.href = "/home";
          }}
        />
      )
    );
  }

  return <>{children}</>;
}
