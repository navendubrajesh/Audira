import type { SessionUser } from "@/lib/auth";

import { InferenceDemo } from "@/components/inference/inference-demo";

export function InferencePanel({ user }: { user: SessionUser }) {
  return (
    <section className="mt-12 rounded-xl border border-neutral-200 bg-white p-6 shadow-sm">
      <h2 className="text-lg font-semibold text-neutral-900">Analysis queue</h2>
      <p className="mt-1 text-sm text-neutral-500">
        Signed in as {user.email} — submit a sample job to the inference queue (GPU tier
        decoupled).
      </p>
      <InferenceDemo />
    </section>
  );
}
