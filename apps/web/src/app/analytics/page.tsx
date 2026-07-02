import Link from "next/link";
import { cookies } from "next/headers";

import { AppHeader } from "@/components/app-header";

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

async function getDashboard(token: string) {
  try {
    const res = await fetch(`${API_URL}/features/analytics/dashboard`, {
      headers: { Authorization: `Bearer ${token}` },
      cache: "no-store",
    });
    if (!res.ok) return null;
    return res.json();
  } catch {
    return null;
  }
}

export default async function AnalyticsPage() {
  const cookieStore = await cookies();
  const token = cookieStore.get("resonode_session")?.value;

  if (!token) {
    return (
      <main className="min-h-screen">
        <AppHeader />
        <div className="mx-auto max-w-6xl px-6 py-16">
          <Link href="/login" className="text-brand-600 hover:underline">
            Sign in
          </Link>{" "}
          to view analytics.
        </div>
      </main>
    );
  }

  const dash = await getDashboard(token);

  return (
    <main className="min-h-screen">
      <AppHeader />
      <section className="mx-auto max-w-6xl px-6 py-12">
        <h1 className="text-2xl font-bold text-neutral-900">Analytics</h1>
        <p className="mt-1 text-sm text-neutral-500">TCA-039 / TCA-055 — org insights</p>
        {dash ? (
          <div className="mt-8 grid gap-6 sm:grid-cols-3">
            <div className="rounded-xl border border-neutral-200 bg-white p-6 shadow-sm">
              <p className="text-sm text-neutral-500">Avg composite score</p>
              <p className="mt-2 text-3xl font-bold text-brand-600">{dash.avg_composite_score}</p>
            </div>
            <div className="rounded-xl border border-neutral-200 bg-white p-6 shadow-sm">
              <p className="text-sm text-neutral-500">Analyses run</p>
              <p className="mt-2 text-3xl font-bold text-neutral-900">{dash.analyses_count}</p>
            </div>
            <div className="rounded-xl border border-neutral-200 bg-white p-6 shadow-sm">
              <p className="text-sm text-neutral-500">Channels tracked</p>
              <p className="mt-2 text-3xl font-bold text-neutral-900">{dash.by_channel?.length ?? 0}</p>
            </div>
          </div>
        ) : (
          <p className="mt-8 text-neutral-600">Could not load dashboard.</p>
        )}
      </section>
    </main>
  );
}
