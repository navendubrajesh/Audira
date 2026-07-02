import { create } from "zustand";

import type { DraftItem, ModuleId } from "@studio/types";
import { listDrafts } from "@studio/services/studio-api";
import {
  blogDrafts,
  linkedinDrafts,
  placementDrafts,
  socialDrafts,
} from "@studio/mock/fixtures";

const FALLBACK: Record<string, DraftItem[]> = {
  social: socialDrafts,
  linkedin: linkedinDrafts,
  placement: placementDrafts,
  blog: blogDrafts,
};

interface DraftsState {
  byVertical: Partial<Record<ModuleId, DraftItem[]>>;
  loading: boolean;
  load: (vertical?: ModuleId) => Promise<void>;
  getForModule: (module: ModuleId) => DraftItem[];
}

export const useDraftsStore = create<DraftsState>((set, get) => ({
  byVertical: {},
  loading: false,

  load: async (vertical) => {
    set({ loading: true });
    try {
      const drafts = await listDrafts(vertical);
      if (vertical) {
        set((s) => ({ byVertical: { ...s.byVertical, [vertical]: drafts }, loading: false }));
      } else {
        const grouped: Partial<Record<ModuleId, DraftItem[]>> = {};
        for (const d of drafts) {
          const v = d.vertical;
          grouped[v] = grouped[v] ? [...grouped[v], d] : [d];
        }
        set({ byVertical: grouped, loading: false });
      }
    } catch {
      if (vertical) {
        set((s) => ({
          byVertical: { ...s.byVertical, [vertical]: FALLBACK[vertical] ?? [] },
          loading: false,
        }));
      } else {
        set({
          byVertical: {
            social: socialDrafts,
            linkedin: linkedinDrafts,
            placement: placementDrafts,
            blog: blogDrafts,
          },
          loading: false,
        });
      }
    }
  },

  getForModule: (module) => {
    const { byVertical } = get();
    return byVertical[module] ?? FALLBACK[module] ?? [];
  },
}));
