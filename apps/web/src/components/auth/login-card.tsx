"use client";

import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";

import { devLogin, getLoginUrl, setSessionToken } from "@/lib/auth";

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
          <p className="text-sm text-neutral-500">Enterprise SSO for your organisation</p>
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
          href={getLoginUrl()}
          className="block w-full rounded-md bg-brand-600 px-4 py-2.5 text-center text-sm font-semibold text-white hover:bg-brand-700 focus:outline-none focus:ring-2 focus:ring-brand-500 focus:ring-offset-2"
        >
          Continue with SSO
        </a>
      )}

      <p className="mt-6 text-xs text-neutral-500">
        Audira.run uses your organisation&apos;s identity provider. We do not store your SSO
        password. Access is logged for security and compliance purposes.
      </p>
    </div>
  );
}

export function AuthCallbackClient({ token }: { token: string | null }) {
  const router = useRouter();

  useEffect(() => {
    if (token) {
      setSessionToken(token);
      router.replace("/");
    } else {
      router.replace("/login");
    }
  }, [token, router]);

  return (
    <div className="flex min-h-screen items-center justify-center">
      <p className="text-neutral-600">Completing sign-in…</p>
    </div>
  );
}
