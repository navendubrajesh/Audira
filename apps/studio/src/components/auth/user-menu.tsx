import { LogOut, Shield } from "lucide-react";
import { useState } from "react";

import { Button } from "@studio/components/ui/button";
import { useAuthStore } from "@studio/store/auth-store";

export function UserMenu() {
  const user = useAuthStore((s) => s.user);
  const signOut = useAuthStore((s) => s.signOut);
  const [open, setOpen] = useState(false);

  if (!user) return null;

  const initials = user.email.slice(0, 2).toUpperCase();

  return (
    <div className="relative">
      <button
        type="button"
        onClick={() => setOpen(!open)}
        className="flex h-8 w-8 items-center justify-center rounded-full bg-primary text-xs font-bold text-primary-foreground"
        aria-label="User menu"
        aria-expanded={open}
      >
        {initials}
      </button>
      {open ? (
        <>
          <button
            type="button"
            className="fixed inset-0 z-40"
            aria-label="Close menu"
            onClick={() => setOpen(false)}
          />
          <div className="absolute right-0 z-50 mt-2 w-64 rounded-lg border border-border bg-surface-raised p-3 shadow-elevated">
            <p className="truncate text-sm font-semibold">{user.email}</p>
            <div className="mt-2 flex flex-wrap gap-1">
              {user.role_labels.map((label) => (
                <span
                  key={label}
                  className="inline-flex items-center gap-1 rounded-full bg-primary/10 px-2 py-0.5 text-[10px] font-medium text-primary"
                >
                  <Shield className="h-3 w-3" />
                  {label}
                </span>
              ))}
            </div>
            <Button
              variant="outline"
              size="sm"
              className="mt-3 w-full"
              onClick={() => void signOut().then(() => window.location.assign("/login"))}
            >
              <LogOut className="h-3.5 w-3.5" />
              Sign out
            </Button>
          </div>
        </>
      ) : null}
    </div>
  );
}
