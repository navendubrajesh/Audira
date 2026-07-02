const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";
const SESSION_COOKIE = "audira_session";

export type SessionUser = {
  user_id: string;
  email: string;
  tenant_id: string;
  roles: string[];
  role_labels: string[];
};

export function getApiUrl(): string {
  return API_URL;
}

export function getSessionToken(): string | null {
  if (typeof document === "undefined") return null;
  const match = document.cookie
    .split("; ")
    .find((row) => row.startsWith(`${SESSION_COOKIE}=`));
  return match ? decodeURIComponent(match.split("=")[1]) : null;
}

export function setSessionToken(token: string): void {
  document.cookie = `${SESSION_COOKIE}=${encodeURIComponent(token)}; path=/; max-age=86400; SameSite=Lax`;
}

export function clearSession(): void {
  document.cookie = `${SESSION_COOKIE}=; path=/; max-age=0`;
}

export async function fetchMe(token?: string): Promise<SessionUser | null> {
  const authToken = token ?? getSessionToken();
  if (!authToken) return null;

  const response = await fetch(`${API_URL}/auth/me`, {
    headers: { Authorization: `Bearer ${authToken}` },
    cache: "no-store",
  });

  if (!response.ok) return null;
  return response.json();
}

export async function devLogin(email: string, role: string): Promise<string> {
  const response = await fetch(
    `${API_URL}/auth/dev-login?email=${encodeURIComponent(email)}&role=${encodeURIComponent(role)}`,
    { method: "POST" },
  );
  if (!response.ok) throw new Error("Dev login failed");
  const data = await response.json();
  return data.token as string;
}

export async function logout(): Promise<void> {
  const token = getSessionToken();
  if (token) {
    await fetch(`${API_URL}/auth/logout`, {
      method: "POST",
      headers: { Authorization: `Bearer ${token}` },
    });
  }
  clearSession();
}

export function getGoogleLoginUrl(): string {
  return `${API_URL}/auth/login`;
}
