import Link from "next/link";
import { cookies } from "next/headers";

import { UserMenu } from "@/components/user-menu";
import type { SessionUser } from "@/lib/auth";

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

async function getServerUser(): Promise<SessionUser | null> {
  const cookieStore = await cookies();
  const token = cookieStore.get("audira_session")?.value;
  if (!token) return null;

  try {
    const response = await fetch(`${API_URL}/auth/me`, {
      headers: { Authorization: `Bearer ${token}` },
      cache: "no-store",
    });
    if (!response.ok) return null;
    return response.json();
  } catch {
    return null;
  }
}

export async function AppHeader() {
  const user = await getServerUser();

  return (
    <header className="border-b border-neutral-200 bg-white">
      <div className="mx-auto flex h-14 max-w-6xl items-center justify-between px-6">
        <div className="flex items-center gap-3">
          <div className="flex h-8 w-8 items-center justify-center rounded-md bg-brand-600 text-sm font-bold text-white">
            A
          </div>
          <span className="font-semibold text-neutral-900">Audira.run</span>
          {user ? (
            <nav className="ml-6 flex gap-4 text-sm text-neutral-600">
              <Link href="/" className="hover:text-brand-600">
                Home
              </Link>
              <Link href="/analyze" className="hover:text-brand-600">
                Analyze
              </Link>
              <Link href="/analytics" className="hover:text-brand-600">
                Analytics
              </Link>
            </nav>
          ) : null}
        </div>
        {user ? (
          <UserMenu user={user} />
        ) : (
          <Link
            href="/login"
            className="rounded-md bg-brand-600 px-3 py-1.5 text-sm font-semibold text-white hover:bg-brand-700"
          >
            Sign in
          </Link>
        )}
      </div>
    </header>
  );
}
