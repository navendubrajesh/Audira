"use client";

import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";

import {
  devLogin,
  getLoginUrl,
  setSessionToken,
  type OAuthProvider,
  type OAuthProviderId,
} from "@/lib/auth";

function ProviderIcon({ provider }: { provider: OAuthProviderId }) {
  const className = "h-5 w-5 shrink-0";
  switch (provider) {
    case "google":
      return (
        <svg className={className} viewBox="0 0 24 24" aria-hidden="true">
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
    case "apple":
      return (
        <svg className={className} viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">
          <path d="M17.05 20.28c-.98.95-2.05.88-3.08.4-1.09-.5-2.08-.48-3.24 0-1.44.62-2.2.44-3.06-.4C2.79 15.25 3.51 7.59 9.05 7.31c1.35.07 2.29.74 3.08.8 1.18-.24 2.31-.93 3.57-.84 1.51.12 2.65.72 3.4 1.8-3.12 1.87-2.38 5.98.48 7.13-.57 1.5-1.31 2.99-2.54 4.09zM12.03 7.25c-.15-2.23 1.66-4.07 3.74-4.25.29 2.58-2.34 4.5-3.74 4.25z" />
        </svg>
      );
    case "github":
      return (
        <svg className={className} viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">
          <path d="M12 0C5.37 0 0 5.37 0 12c0 5.31 3.435 9.795 8.205 11.385.6.105.825-.255.825-.57 0-.285-.015-1.23-.015-2.235-3.015.555-3.795-.735-4.035-1.41-.135-.345-.72-1.41-1.23-1.695-.42-.225-1.02-.78-.015-.795.945-.015 1.62.87 1.845 1.23 1.08 1.815 2.805 1.305 3.495.99.105-.78.42-1.305.765-1.605-2.67-.3-5.46-1.335-5.46-5.925 0-1.305.465-2.385 1.23-3.225-.12-.3-.54-1.53.12-3.18 0 0 1.005-.315 3.3 1.23.96-.27 1.98-.405 3-.405s2.04.135 3 .405c2.295-1.56 3.3-1.23 3.3-1.23.66 1.65.24 2.88.12 3.18.765.84 1.23 1.905 1.23 3.225 0 4.605-2.805 5.625-5.475 5.925.435.375.81 1.095.81 2.22 0 1.605-.015 2.895-.015 3.3 0 .315.225.69.825.57A12.02 12.02 0 0024 12c0-6.63-5.37-12-12-12z" />
        </svg>
      );
    case "linkedin":
      return (
        <svg className={className} viewBox="0 0 24 24" fill="#0A66C2" aria-hidden="true">
          <path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433a2.062 2.062 0 01-2.063-2.065 2.064 2.064 0 114.126 0 2.063 2.063 0 01-2.063 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z" />
        </svg>
      );
  }
}

function SocialLoginButtons({ providers }: { providers: OAuthProvider[] }) {
  if (providers.length === 0) {
    return (
      <p className="rounded-md bg-neutral-50 px-3 py-3 text-sm text-neutral-600">
        No sign-in providers are configured yet. Please try again later.
      </p>
    );
  }

  return (
    <div className="space-y-3">
      {providers.map(({ id, label }) => (
        <a
          key={id}
          href={getLoginUrl(id)}
          className="flex w-full items-center justify-center gap-3 rounded-md border border-neutral-300 bg-white px-4 py-2.5 text-sm font-medium text-neutral-800 hover:bg-neutral-50 focus:outline-none focus:ring-2 focus:ring-brand-500 focus:ring-offset-2"
        >
          <ProviderIcon provider={id} />
          Continue with {label}
        </a>
      ))}
    </div>
  );
}

export function LoginCard({
  devMode,
  providers = [],
}: {
  devMode?: boolean;
  providers?: OAuthProvider[];
}) {
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
        <SocialLoginButtons providers={providers} />
      )}

      <p className="mt-6 text-xs text-neutral-500">
        Audira.run uses your chosen identity provider. We do not store your password. Once signed
        in, you can run communications analysis, submit inference jobs, and use all free-tier
        features.
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
