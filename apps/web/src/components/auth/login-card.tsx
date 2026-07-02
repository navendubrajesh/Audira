"use client";

import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";

import { devLogin, getGoogleLoginUrl, setSessionToken } from "@/lib/auth";

function GoogleIcon() {
  return (
    <svg className="h-5 w-5 shrink-0" viewBox="0 0 24 24" aria-hidden="true">
      <path
        fill="#4285F4"
        d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
      />
      <path
        fill="#34A853"
        d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
      />
      <path
        fill="#FBBC05"
        d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"
      />
      <path
        fill="#EA4335"
        d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"
      />
    </svg>
  );
}

export function LoginCard({ devMode }: { devMode?: boolean }) {
  const router = useRouter();
  const [email, setEmail] = useState("admin@audira.run");
  const [role, setRole] = useState("admin");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function handleDevLogin(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      const token = await devLogin(email, role);
      setSessionToken(token);
      router.push("/");
      router.refresh();
    } catch {
      setError("We could not complete sign-in. Please try again.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="w-full max-w-md rounded-xl border border-neutral-200 bg-white p-8 shadow-sm">
      <div className="mb-6 flex items-center gap-3">
        <div className="flex h-10 w-10 items-center justify-center rounded-md bg-brand-600 text-lg font-bold text-white">
          A
        </div>
        <div>
          <h1 className="text-xl font-bold text-neutral-900">Sign in to Audira.run</h1>
          <p className="text-sm text-neutral-500">Sign in to access all free features</p>
        </div>
      </div>

      {devMode ? (
        <form onSubmit={handleDevLogin} className="space-y-4">
          <p className="rounded-md bg-amber-50 px-3 py-2 text-xs text-amber-800">
            Development mode — use configured test credentials
          </p>
          <label className="block text-sm font-medium text-neutral-700">
            Email
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="mt-1 w-full rounded-md border border-neutral-300 px-3 py-2 text-sm"
              required
            />
          </label>
          <label className="block text-sm font-medium text-neutral-700">
            Role
            <select
              value={role}
              onChange={(e) => setRole(e.target.value)}
              className="mt-1 w-full rounded-md border border-neutral-300 px-3 py-2 text-sm"
            >
              <option value="admin">Administrator</option>
              <option value="comms_manager">Comms Manager</option>
              <option value="security">Security / IT</option>
              <option value="brand_manager">Brand Manager</option>
            </select>
          </label>
          {error ? <p className="text-sm text-danger">{error}</p> : null}
          <button
            type="submit"
            disabled={loading}
            className="w-full rounded-md bg-brand-600 px-4 py-2.5 text-sm font-semibold text-white hover:bg-brand-700 focus:outline-none focus:ring-2 focus:ring-brand-500 focus:ring-offset-2 disabled:opacity-50"
          >
            {loading ? "Signing in…" : "Continue with SSO"}
          </button>
        </form>
      ) : (
        <a
          href={getGoogleLoginUrl()}
          className="flex w-full items-center justify-center gap-3 rounded-md border border-neutral-300 bg-white px-4 py-2.5 text-sm font-medium text-neutral-800 hover:bg-neutral-50 focus:outline-none focus:ring-2 focus:ring-brand-500 focus:ring-offset-2"
        >
          <GoogleIcon />
          Continue with Google
        </a>
      )}

      <p className="mt-6 text-xs text-neutral-500">
        Sign in with your Google account. We do not store your password. Once signed in, you
        can run communications analysis, submit inference jobs, and use all free-tier features.
      </p>
    </div>
  );
}

export function AuthCallbackClient({ token: queryToken }: { token: string | null }) {
  const router = useRouter();

  useEffect(() => {
    let token = queryToken;
    if (!token && typeof window !== "undefined") {
      const hash = window.location.hash.replace(/^#/, "");
      const params = new URLSearchParams(hash);
      token = params.get("token");
    }
    if (token) {
      setSessionToken(token);
      router.replace("/");
    } else {
      router.replace("/login");
    }
  }, [queryToken, router]);

  return (
    <div className="flex min-h-screen items-center justify-center">
      <p className="text-neutral-600">Completing sign-in…</p>
    </div>
  );
}
