import Link from "next/link";
import { cookies } from "next/headers";
import { productName, productTagline } from "@resonode/design-tokens";

import { AppHeader } from "@/components/app-header";
import { InferencePanel } from "@/components/inference/inference-panel";
import { ScoreGauge } from "@/components/score-gauge";
import { StatusBadge } from "@/components/status-badge";
import type { SessionUser } from "@/lib/auth";

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

async function getServerUser(): Promise<SessionUser | null> {
  const cookieStore = await cookies();
  const token = cookieStore.get("resonode_session")?.value;
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

export default async function HomePage() {
  const user = await getServerUser();

  return (
    <main className="min-h-screen">
      <AppHeader />

      <section className="mx-auto max-w-6xl px-6 py-16">
        <div className="mb-6 flex flex-wrap gap-2">
          <StatusBadge label="TCA-067 — SSO & RBAC" variant="success" />
          <StatusBadge label="TCA-072 — Inference queue" variant="success" />
        </div>
        <div className="grid gap-12 lg:grid-cols-2 lg:items-center">
          <div>
            <p className="mb-3 text-sm font-medium uppercase tracking-wide text-brand-600">
              Enterprise Communications Neuro-Analyzer
            </p>
            <h1 className="text-4xl font-bold tracking-tight text-neutral-900">
              {productName}
            </h1>
            <p className="mt-4 text-lg text-neutral-600">{productTagline}</p>
            <p className="mt-6 text-sm text-neutral-500">
              {user ? (
                <>Inference jobs run on a decoupled GPU tier via Redis queue.</>
              ) : (
                <>
                  <Link href="/login" className="font-medium text-brand-600 hover:underline">
                    Sign in
                  </Link>{" "}
                  to submit analyses to the inference queue.
                </>
              )}
            </p>
          </div>

          <div className="rounded-xl border border-neutral-200 bg-white p-8 shadow-sm">
            <p className="mb-6 text-sm font-medium text-neutral-500">
              Preview — composite effectiveness score
            </p>
            <ScoreGauge score={72} label="Sample analysis" />
          </div>
        </div>

        {user ? <InferencePanel user={user} /> : null}
      </section>
    </main>
  );
}
