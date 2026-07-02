import { create } from "zustand";
import { persist } from "zustand/middleware";

import type { ModuleId, WorkspaceTab } from "@/types";

interface UiState {
  theme: "light" | "dark";
  railExpanded: boolean;
  contextWidth: number;
  mainSplitRatio: number;
  activeModule: ModuleId;
  activeContextId: string | null;
  activeTab: WorkspaceTab;
  activeFilter: string;
  setTheme: (theme: "light" | "dark") => void;
  toggleTheme: () => void;
  setRailExpanded: (v: boolean) => void;
  setContextWidth: (w: number) => void;
  setMainSplitRatio: (r: number) => void;
  setActiveModule: (m: ModuleId) => void;
  setActiveContextId: (id: string | null) => void;
  setActiveTab: (t: WorkspaceTab) => void;
  setActiveFilter: (f: string) => void;
}

export const useUiStore = create<UiState>()(
  persist(
    (set, get) => ({
      theme: "light",
      railExpanded: false,
      contextWidth: 288,
      mainSplitRatio: 0.58,
      activeModule: "home",
      activeContextId: "attention-queue",
      activeTab: "compose",
      activeFilter: "All",
      setTheme: (theme) => {
        document.documentElement.classList.toggle("dark", theme === "dark");
        set({ theme });
      },
      toggleTheme: () => {
        const next = get().theme === "light" ? "dark" : "light";
        get().setTheme(next);
      },
      setRailExpanded: (railExpanded) => set({ railExpanded }),
      setContextWidth: (contextWidth) =>
        set({ contextWidth: Math.max(220, Math.min(420, contextWidth)) }),
      setMainSplitRatio: (mainSplitRatio) =>
        set({ mainSplitRatio: Math.max(0.35, Math.min(0.75, mainSplitRatio)) }),
      setActiveModule: (activeModule) => set({ activeModule }),
      setActiveContextId: (activeContextId) => set({ activeContextId }),
      setActiveTab: (activeTab) => set({ activeTab }),
      setActiveFilter: (activeFilter) => set({ activeFilter }),
    }),
    {
      name: "audira-studio-ui",
      partialize: (s) => ({
        theme: s.theme,
        railExpanded: s.railExpanded,
        contextWidth: s.contextWidth,
        mainSplitRatio: s.mainSplitRatio,
      }),
    },
  ),
);
