import { create } from "zustand";

import {
  clearSession,
  devLogin,
  fetchMe,
  getSessionToken,
  logout,
  setSessionToken,
  type SessionUser,
} from "@studio/lib/auth";
import { hasPermission } from "@studio/lib/permissions";

interface AuthState {
  user: SessionUser | null;
  loading: boolean;
  error: string | null;
  initialized: boolean;
  initialize: () => Promise<void>;
  signInDev: (email: string, role: string) => Promise<void>;
  signInWithToken: (token: string) => Promise<void>;
  signOut: () => Promise<void>;
  can: (permission: string) => boolean;
}

export const useAuthStore = create<AuthState>((set, get) => ({
  user: null,
  loading: true,
  error: null,
  initialized: false,

  initialize: async () => {
    set({ loading: true, error: null });
    try {
      const token = getSessionToken();
      if (!token) {
        set({ user: null, loading: false, initialized: true });
        return;
      }
      const user = await fetchMe(token);
      if (!user) {
        clearSession();
      }
      set({ user, loading: false, initialized: true });
    } catch {
      set({
        user: null,
        loading: false,
        initialized: true,
        error: "Could not reach the API. Check your connection and try again.",
      });
    }
  },

  signInDev: async (email, role) => {
    set({ loading: true, error: null });
    try {
      const token = await devLogin(email, role);
      setSessionToken(token);
      const user = await fetchMe(token);
      set({ user, loading: false, initialized: true });
    } catch {
      set({ error: "Sign-in failed.", loading: false });
      throw new Error("Sign-in failed");
    }
  },

  signInWithToken: async (token) => {
    set({ loading: true, error: null });
    setSessionToken(token);
    try {
      const user = await fetchMe(token);
      if (!user) {
        clearSession();
        set({ user: null, loading: false, initialized: true, error: "Sign-in failed." });
        return;
      }
      set({ user, loading: false, initialized: true, error: null });
    } catch {
      set({
        user: null,
        loading: false,
        initialized: true,
        error: "Could not reach the API. Check your connection and try again.",
      });
    }
  },

  signOut: async () => {
    await logout();
    set({ user: null });
  },

  can: (permission) => {
    const { user } = get();
    if (!user) return false;
    return hasPermission(user.roles, permission);
  },
}));
