import { create } from "zustand";

import type { FeedbackCategory, Persona } from "@/types";
import { scoreDraft } from "@/services/analyzer";
import { LINKEDIN_SAMPLE_DRAFT, DEFAULT_PERSONAS } from "@/mock/fixtures";

interface AnalyzerState {
  draftText: string;
  personaId: string;
  variant: "A" | "B";
  compositeScore: number;
  feedback: FeedbackCategory[];
  highlightedCategoryId: string | null;
  isScoring: boolean;
  attachedAssets: string[];
  setDraftText: (text: string) => void;
  setPersonaId: (id: string) => void;
  setVariant: (v: "A" | "B") => void;
  setHighlightedCategoryId: (id: string | null) => void;
  addAsset: (name: string) => void;
  runScore: () => Promise<void>;
  personas: Persona[];
}

let debounceTimer: ReturnType<typeof setTimeout> | null = null;

export const useAnalyzerStore = create<AnalyzerState>((set, get) => ({
  draftText: LINKEDIN_SAMPLE_DRAFT,
  personaId: "technical-peer",
  variant: "A",
  compositeScore: 72,
  feedback: [],
  highlightedCategoryId: null,
  isScoring: false,
  attachedAssets: ["architecture-diagram.png"],
  personas: DEFAULT_PERSONAS,
  setDraftText: (draftText) => {
    set({ draftText });
    if (debounceTimer) clearTimeout(debounceTimer);
    debounceTimer = setTimeout(() => {
      void get().runScore();
    }, 600);
  },
  setPersonaId: (personaId) => {
    set({ personaId });
    void get().runScore();
  },
  setVariant: (variant) => set({ variant }),
  setHighlightedCategoryId: (highlightedCategoryId) => set({ highlightedCategoryId }),
  addAsset: (name) =>
    set((s) => ({
      attachedAssets: s.attachedAssets.includes(name)
        ? s.attachedAssets
        : [...s.attachedAssets, name],
    })),
  runScore: async () => {
    const { draftText, personaId, variant } = get();
    set({ isScoring: true });
    try {
      const result = await scoreDraft({ text: draftText, personaId, variant });
      set({
        compositeScore: result.compositeScore,
        feedback: result.categories,
        isScoring: false,
      });
    } catch {
      set({ isScoring: false });
    }
  },
}));

void useAnalyzerStore.getState().runScore();
