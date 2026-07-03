import { resolveFetchApiUrl, resolveOAuthApiUrl } from "@studio/lib/env-config";

const SESSION_COOKIE = "audira_session";

let cachedApiUrl: string | undefined;

function apiUrl(): string {
  if (cachedApiUrl === undefined) {
    cachedApiUrl = resolveFetchApiUrl();
  }
  return cachedApiUrl;
}

function readCookieToken(): string | null {
  if (typeof document === "undefined") return null;
  const match = document.cookie
    .split("; ")
    .find((row) => row.startsWith(`${SESSION_COOKIE}=`));
  return match ? decodeURIComponent(match.split("=")[1]) : null;
}

export type SessionUser = {
  user_id: string;
  email: string;
  tenant_id: string;
  roles: string[];
  role_labels: string[];
};

export function getApiUrl(): string {
  return apiUrl();
}

export function getSessionToken(): string | null {
  const fromCookie = readCookieToken();
  if (fromCookie) return fromCookie;

  // Migrate legacy Vite sessions stored in localStorage.
  if (typeof localStorage !== "undefined") {
    const legacy = localStorage.getItem(SESSION_COOKIE);
    if (legacy) {
      setSessionToken(legacy);
      localStorage.removeItem(SESSION_COOKIE);
      return legacy;
    }
  }

  return null;
}

export function setSessionToken(token: string): void {
  if (typeof document !== "undefined") {
    document.cookie = `${SESSION_COOKIE}=${encodeURIComponent(token)}; path=/; max-age=86400; SameSite=Lax`;
  }
}

export function clearSession(): void {
  if (typeof document !== "undefined") {
    document.cookie = `${SESSION_COOKIE}=; path=/; max-age=0`;
  }
  if (typeof localStorage !== "undefined") {
    localStorage.removeItem(SESSION_COOKIE);
  }
}

export async function fetchMe(token?: string): Promise<SessionUser | null> {
  const authToken = token ?? getSessionToken();
  if (!authToken) return null;

  const response = await fetch(`${apiUrl()}/auth/me`, {
    headers: { Authorization: `Bearer ${authToken}` },
  });

  if (!response.ok) return null;
  return response.json();
}

export async function devLogin(email: string, role: string): Promise<string> {
  const response = await fetch(
    `${apiUrl()}/auth/dev-login?email=${encodeURIComponent(email)}&role=${encodeURIComponent(role)}`,
    { method: "POST" },
  );
  if (!response.ok) throw new Error("Dev login failed");
  const data = await response.json();
  return data.token as string;
}

export async function logout(): Promise<void> {
  const token = getSessionToken();
  if (token) {
    await fetch(`${apiUrl()}/auth/logout`, {
      method: "POST",
      headers: { Authorization: `Bearer ${token}` },
    });
  }
  clearSession();
}

export function getGoogleLoginUrl(returnUrl?: string): string {
  const base = `${resolveOAuthApiUrl()}/auth/login`;
  if (returnUrl) {
    return `${base}?return_url=${encodeURIComponent(returnUrl)}`;
  }
  return base;
}
