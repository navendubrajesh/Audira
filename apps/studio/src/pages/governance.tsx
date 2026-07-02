import { FeatureGrid } from "@/components/shared/feature-card";
import { storiesForEpic } from "@/mock/fixtures";

const EPIC_SECTIONS = [
  { epic: "E13", title: "Workflow, Review & Approval Gates" },
  { epic: "E15", title: "Compliance, Inclusivity & Risk Guardrails" },
  { epic: "E16", title: "Model Governance, Explainability & Validation" },
  { epic: "E17", title: "Security, Privacy, IP & Data Residency" },
  { epic: "E08", title: "Brand Voice, Tone & Consistency Governance" },
];

// TODO(TCA-013): Approval workflow board
// TODO(TCA-061): Audit log viewer
export function GovernancePage() {
  return (
    <div className="h-full overflow-y-auto p-6">
      <h1 className="font-display text-2xl font-bold">Governance & Admin</h1>
      <p className="text-sm text-muted-foreground">
        Standards library, quality gates, approval workflow, audit log, model cards.
      </p>

      <div className="mt-4 rounded-lg border border-primary/30 bg-primary/5 p-4 text-sm">
        <strong>Governance note (TCA-068):</strong> Data residency is tenant-configurable
        (India/EU). DPDP/GDPR compliance is not assumed — verify region pinning in Settings.
      </div>

      <div className="mt-4 rounded-lg border border-warning/30 bg-warning/10 p-4 text-sm">
        <strong>Licensing note (E03):</strong> Model-agnostic analyzer — non-commercial model
        licence flags surface here, not hardcoded vendor assumptions.
      </div>

      {EPIC_SECTIONS.map(({ epic, title }) => (
        <section key={epic} className="mt-8">
          <h2 className="mb-3 font-display text-sm font-semibold">
            {epic} — {title}
          </h2>
          <FeatureGrid storyIds={storiesForEpic(epic).map((s) => s.ID)} />
        </section>
      ))}
    </div>
  );
}

export function SettingsPage() {
  return (
    <div className="h-full overflow-y-auto p-6">
      <h1 className="font-display text-2xl font-bold">Settings</h1>
      <FeatureGrid
        storyIds={storiesForEpic("E17")
          .map((s) => s.ID)
          .concat(["TCA-067"])}
      />
    </div>
  );
}

export function AssetsPage() {
  return (
    <div className="h-full overflow-y-auto p-6">
      <h1 className="font-display text-2xl font-bold">Asset Library</h1>
      <p className="text-sm text-muted-foreground">
        Uploaded diagrams, images, and code snippets with type routing (TCA-079).
      </p>
      <div className="mt-4 rounded-lg border border-danger/20 bg-danger/5 p-3 text-xs">
        Engineering artifacts are out of scope per TCA-004 — uploads flagged as code repos will be
        rejected.
      </div>
      <div className="mt-6">
        <FeatureGrid storyIds={storiesForEpic("E02").map((s) => s.ID)} />
      </div>
    </div>
  );
}

export function VerticalEpicGrid({ epicPrefixes }: { epicPrefixes: string[] }) {
  const ids = epicPrefixes.flatMap((e) => storiesForEpic(e).map((s) => s.ID));
  return (
    <div className="mt-6">
      <FeatureGrid storyIds={ids.slice(0, 12)} />
      {ids.length > 12 ? (
        <p className="mt-2 text-xs text-muted-foreground">+ {ids.length - 12} more stories mapped</p>
      ) : null}
    </div>
  );
}
