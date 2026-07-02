const API_URL = import.meta.env.VITE_API_URL ?? "http://localhost:8000";
const SESSION_KEY = "audira_session";

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
  if (typeof localStorage === "undefined") return null;
  return localStorage.getItem(SESSION_KEY);
}

export function setSessionToken(token: string): void {
  localStorage.setItem(SESSION_KEY, token);
}

export function clearSession(): void {
  localStorage.removeItem(SESSION_KEY);
}

export async function fetchMe(token?: string): Promise<SessionUser | null> {
  const authToken = token ?? getSessionToken();
  if (!authToken) return null;

  const response = await fetch(`${API_URL}/auth/me`, {
    headers: { Authorization: `Bearer ${authToken}` },
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

export function getGoogleLoginUrl(returnUrl?: string): string {
  const base = `${API_URL}/auth/login`;
  if (returnUrl) {
    return `${base}?return_url=${encodeURIComponent(returnUrl)}`;
  }
  return base;
}
