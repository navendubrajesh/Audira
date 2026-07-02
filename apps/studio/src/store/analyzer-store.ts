import { create } from "zustand";

import type { FeedbackCategory, ModuleId } from "@studio/types";
import { scoreDraft, compareVariants } from "@studio/services/analyzer";
import { LINKEDIN_SAMPLE_DRAFT } from "@studio/mock/fixtures";
import { listAudiences, type Audience } from "@studio/services/context-api";
import { ApiError } from "@studio/lib/api-client";

interface AnalyzerState {
  draftText: string;
  draftTextB: string;
  audienceId: string;
  audiences: Audience[];
  module: ModuleId;
  variant: "A" | "B";
  fullAnalysis: boolean;
  compositeScore: number;
  feedback: FeedbackCategory[];
  highlightedCategoryId: string | null;
  isScoring: boolean;
  scoreError: string | null;
  canUpgrade: boolean;
  verdict: string | null;
  analysisId: string | null;
  modelId: string | null;
  attachedAssets: string[];
  setDraftText: (text: string) => void;
  setDraftTextB: (text: string) => void;
  setAudienceId: (id: string) => void;
  setModule: (module: ModuleId) => void;
  setVariant: (v: "A" | "B") => void;
  setFullAnalysis: (v: boolean) => void;
  setHighlightedCategoryId: (id: string | null) => void;
  addAsset: (name: string) => void;
  loadAudiences: () => Promise<void>;
  runScore: () => Promise<void>;
  runCompare: () => Promise<void>;
}

let debounceTimer: ReturnType<typeof setTimeout> | null = null;

export const useAnalyzerStore = create<AnalyzerState>((set, get) => ({
  draftText: LINKEDIN_SAMPLE_DRAFT,
  draftTextB: "",
  audienceId: "",
  audiences: [],
  module: "linkedin",
  variant: "A",
  fullAnalysis: false,
  compositeScore: 0,
  feedback: [],
  highlightedCategoryId: null,
  isScoring: false,
  scoreError: null,
  canUpgrade: false,
  verdict: null,
  analysisId: null,
  modelId: null,
  attachedAssets: ["architecture-diagram.png"],

  setDraftText: (draftText) => {
    set({ draftText });
    if (debounceTimer) clearTimeout(debounceTimer);
    debounceTimer = setTimeout(() => {
      void get().runScore();
    }, 600);
  },

  setDraftTextB: (draftTextB) => set({ draftTextB }),
  setAudienceId: (audienceId) => {
    set({ audienceId });
    void get().runScore();
  },
  setModule: (module) => {
    set({ module });
    void get().runScore();
  },
  setVariant: (variant) => set({ variant }),
  setFullAnalysis: (fullAnalysis) => {
    set({ fullAnalysis });
    void get().runScore();
  },
  setHighlightedCategoryId: (highlightedCategoryId) => set({ highlightedCategoryId }),

  addAsset: (name) =>
    set((s) => ({
      attachedAssets: s.attachedAssets.includes(name)
        ? s.attachedAssets
        : [...s.attachedAssets, name],
    })),

  loadAudiences: async () => {
    try {
      const audiences = await listAudiences();
      const defaultAudience = audiences.find((a) => a.is_default) ?? audiences[0];
      set({
        audiences,
        audienceId: defaultAudience?.id ?? "",
      });
    } catch {
      /* auth may not be ready yet */
    }
  },

  runScore: async () => {
    const { draftText, audienceId, variant, module, fullAnalysis, draftTextB } = get();
    const text = variant === "B" && draftTextB ? draftTextB : draftText;
    if (!text.trim()) return;

    set({ isScoring: true, scoreError: null });
    try {
      const result = await scoreDraft({
        text,
        personaId: audienceId,
        audienceId,
        variant,
        module,
        fullAnalysis,
      });
      set({
        compositeScore: result.compositeScore,
        feedback: result.categories,
        isScoring: false,
        canUpgrade: result.canUpgrade ?? false,
        verdict: result.verdict ?? null,
        analysisId: result.analysisId ?? null,
        modelId: result.modelId ?? null,
      });
    } catch (e) {
      const message =
        e instanceof ApiError
          ? e.status === 401
            ? "Sign in required to run analysis."
            : e.message
          : "Analysis failed — is the API running?";
      set({ isScoring: false, scoreError: message });
    }
  },

  runCompare: async () => {
    const { draftText, draftTextB, module } = get();
    if (!draftTextB.trim()) return;
    set({ isScoring: true, scoreError: null });
    try {
      const cmp = await compareVariants(draftText, draftTextB, module);
      set({
        variant: cmp.winner === "a" ? "A" : "B",
        compositeScore: cmp.winner === "a" ? cmp.scoreA : cmp.scoreB,
        isScoring: false,
      });
      void get().runScore();
    } catch (e) {
      set({
        isScoring: false,
        scoreError: e instanceof ApiError ? e.message : "Compare failed",
      });
    }
  },
}));
