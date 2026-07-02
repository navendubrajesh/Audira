import { useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";

import { Button } from "@studio/components/ui/button";
import { PRODUCT_NAME } from "@studio/mock/fixtures";
import { getGoogleLoginUrl } from "@studio/lib/auth";
import { useAuthStore } from "@studio/store/auth-store";

const ROLES = [
  { value: "admin", label: "Administrator" },
  { value: "comms_manager", label: "Comms Manager" },
  { value: "brand_manager", label: "Brand Manager" },
  { value: "policy_compliance", label: "Policy / Compliance" },
  { value: "security", label: "Security / IT" },
  { value: "ml_platform_eng", label: "ML / Platform Engineer" },
  { value: "reviewer", label: "Reviewer" },
];

export function LoginPage() {
  const navigate = useNavigate();
  const location = useLocation();
  const signInDev = useAuthStore((s) => s.signInDev);
  const [email, setEmail] = useState("admin@audira.run");
  const [role, setRole] = useState("admin");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const from = (location.state as { from?: string } | null)?.from ?? "/home";
  const devMode = import.meta.env.DEV;

  async function handleDevLogin(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      await signInDev(email, role);
      navigate(from, { replace: true });
    } catch {
      setError("Sign-in failed. Is the API running on port 8000?");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-surface p-6">
      <div className="w-full max-w-md rounded-xl border border-border bg-surface-raised p-8 shadow-elevated">
        <div className="mb-6 flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-primary font-display text-lg font-bold text-primary-foreground">
            A
          </div>
          <div>
            <h1 className="font-display text-xl font-bold">Sign in to {PRODUCT_NAME}</h1>
            <p className="text-sm text-muted-foreground">Enterprise SSO & RBAC (TCA-067)</p>
          </div>
        </div>

        {devMode ? (
          <form onSubmit={(e) => void handleDevLogin(e)} className="space-y-4">
            <p className="rounded-md bg-warning/10 px-3 py-2 text-xs text-warning">
              Development mode — API dev-login. Start the backend:{" "}
              <code className="text-[11px]">uvicorn app.main:app</code>
            </p>
            <label className="block text-sm font-medium">
              Email
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="mt-1 w-full rounded-lg border border-border bg-surface px-3 py-2 text-sm"
                required
              />
            </label>
            <label className="block text-sm font-medium">
              Role
              <select
                value={role}
                onChange={(e) => setRole(e.target.value)}
                className="mt-1 w-full rounded-lg border border-border bg-surface px-3 py-2 text-sm"
              >
                {ROLES.map((r) => (
                  <option key={r.value} value={r.value}>
                    {r.label}
                  </option>
                ))}
              </select>
            </label>
            {error ? <p className="text-sm text-danger">{error}</p> : null}
            <Button type="submit" className="w-full" disabled={loading}>
              {loading ? "Signing in…" : "Continue with dev SSO"}
            </Button>
          </form>
        ) : (
          <a href={getGoogleLoginUrl(window.location.origin + "/auth/callback")}>
            <Button className="w-full">Continue with Google</Button>
          </a>
        )}
      </div>
    </div>
  );
}
