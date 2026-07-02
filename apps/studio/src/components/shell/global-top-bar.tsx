import { Moon, Search, Sun, Wifi, WifiOff } from "lucide-react";
import { useEffect, useState } from "react";

import { Button } from "@studio/components/ui/button";
import { PRODUCT_NAME } from "@studio/mock/fixtures";
import { getConnectionStatus } from "@studio/services/integrations";
import { useUiStore } from "@studio/store/ui-store";

export function GlobalTopBar() {
  const { theme, toggleTheme } = useUiStore();
  const [connected, setConnected] = useState(true);

  useEffect(() => {
    void getConnectionStatus().then((s) => setConnected(s.connected));
  }, []);

  return (
    <header className="flex h-12 shrink-0 items-center gap-3 border-b border-border bg-surface-raised px-4">
      <div className="relative flex-1 max-w-xl">
        <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
        <input
          type="search"
          placeholder={`Search or ask ${PRODUCT_NAME} (Ctrl+E)`}
          className="h-9 w-full rounded-lg border border-border bg-surface pl-9 pr-3 text-sm placeholder:text-muted-foreground focus:border-primary"
          aria-label={`Search or ask ${PRODUCT_NAME}`}
        />
      </div>

      <div
        className="flex items-center gap-1.5 text-xs text-muted-foreground"
        role="status"
        aria-live="polite"
      >
        {connected ? (
          <>
            <Wifi className="h-3.5 w-3.5 text-success" aria-hidden />
            <span className="hidden sm:inline">Connected</span>
          </>
        ) : (
          <>
            <WifiOff className="h-3.5 w-3.5 text-warning" aria-hidden />
            <span>No connection</span>
          </>
        )}
      </div>

      <Button
        variant="ghost"
        size="icon"
        onClick={toggleTheme}
        aria-label={theme === "light" ? "Switch to dark mode" : "Switch to light mode"}
      >
        {theme === "light" ? <Moon className="h-4 w-4" /> : <Sun className="h-4 w-4" />}
      </Button>

      <button
        type="button"
        className="flex h-8 w-8 items-center justify-center rounded-full bg-primary text-xs font-bold text-primary-foreground"
        aria-label="User menu"
      >
        NB
      </button>
    </header>
  );
}
