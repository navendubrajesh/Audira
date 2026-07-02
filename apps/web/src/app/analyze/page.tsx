import Link from "next/link";
import { cookies } from "next/headers";

import { AnalyzePanel } from "@/components/analyze-panel";
import { AppHeader } from "@/components/app-header";
import { InferencePanel } from "@/components/inference/inference-panel";
import { ResidencyCard } from "@/components/residency-card";
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

export default async function AnalyzePage() {
  const cookieStore = await cookies();
  const token = cookieStore.get("audira_session")?.value;
  const user = await getServerUser();

  if (!user || !token) {
    return (
      <main className="min-h-screen">
        <AppHeader />
        <div className="mx-auto max-w-6xl px-6 py-16">
          <p>
            <Link href="/login" className="text-brand-600 hover:underline">
              Sign in
            </Link>{" "}
            to run communications analysis.
          </p>
        </div>
      </main>
    );
  }

  return (
    <main className="min-h-screen">
      <AppHeader />
      <section className="mx-auto max-w-6xl px-6 py-12">
        <AnalyzePanel token={token} user={user} />
        <InferencePanel user={user} />
        <ResidencyCard />
      </section>
    </main>
  );
}
