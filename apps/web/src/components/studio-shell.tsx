"use client";

import dynamic from "next/dynamic";

const StudioApp = dynamic(
  () => import("@audira/studio").then((mod) => mod.StudioApp),
  {
    ssr: false,
    loading: () => (
      <div className="flex h-screen items-center justify-center bg-surface text-sm text-muted-foreground">
        Loading Audira Studio…
      </div>
    ),
  },
);

export function StudioShell() {
  return <StudioApp />;
}
