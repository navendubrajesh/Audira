import { useCallback, useEffect, useState } from "react";

import { PermissionGate } from "@studio/components/auth/permission-gate";
import { StoryIdBadge } from "@studio/components/ui/badge";
import { GlobalStatePanel } from "@studio/components/shared/global-states";
import { uploadArtifact } from "@studio/services/analyzer";
import { listAssetUploads } from "@studio/services/studio-api";
import { ApiError } from "@studio/lib/api-client";

/** TCA-007 / TCA-008 / TCA-079 — Multimodal upload + asset library */
export function AssetsPage() {
  const [library, setLibrary] = useState<
    Array<{ id: string; filename: string; content_type: string; is_engineering: boolean }>
  >([]);
  const [result, setResult] = useState<{
    composite_score?: number;
    status?: string;
    reason?: string;
    analysis_id?: string;
  } | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const loadLibrary = useCallback(async () => {
    try {
      setLibrary(await listAssetUploads());
    } catch {
      setLibrary([]);
    }
  }, []);

  useEffect(() => {
    void loadLibrary();
  }, [loadLibrary]);

  const onUpload = useCallback(
    async (file: File) => {
      setLoading(true);
      setError(null);
      setResult(null);
      try {
        const data = await uploadArtifact(file);
        setResult(data);
        await loadLibrary();
      } catch (e) {
        setError(e instanceof ApiError ? e.message : "Upload failed");
      } finally {
        setLoading(false);
      }
    },
    [loadLibrary],
  );

  return (
    <PermissionGate permission="analyses.run">
      <div className="h-full overflow-y-auto p-6">
        <h1 className="font-display text-2xl font-bold">Asset Library</h1>
        <p className="text-sm text-muted-foreground">
          Upload Word, PDF, or PowerPoint for parsing and analysis (TCA-007).
        </p>
        <div className="mt-2 flex gap-2">
          <StoryIdBadge id="TCA-007" />
          <StoryIdBadge id="TCA-008" />
          <StoryIdBadge id="TCA-079" />
        </div>

        <div className="mt-4 rounded-lg border border-danger/20 bg-danger/5 p-3 text-xs">
          Engineering artifacts are out of scope per TCA-004 — uploads flagged as code repos will
          be rejected.
        </div>

        <label className="mt-6 flex cursor-pointer flex-col items-center rounded-xl border-2 border-dashed border-border p-8 hover:border-primary/40">
          <input
            type="file"
            accept=".doc,.docx,.pdf,.ppt,.pptx,.txt,.png,.jpg"
            className="sr-only"
            onChange={(e) => {
              const f = e.target.files?.[0];
              if (f) void onUpload(f);
            }}
          />
          <span className="text-sm font-medium">Drop or select a document</span>
        </label>

        {loading ? <GlobalStatePanel variant="loading" className="py-8" /> : null}
        {error ? (
          <p className="mt-4 rounded-lg border border-danger/30 bg-danger/5 p-3 text-sm text-danger">
            {error}
          </p>
        ) : null}
        {result ? (
          <div className="mt-4 rounded-lg border border-border bg-surface-raised p-4 text-sm">
            {result.status === "excluded" ? (
              <p className="text-danger">{result.reason ?? "Artifact excluded from scope."}</p>
            ) : (
              <p className="font-display text-2xl font-bold tabular-nums">
                Score: {result.composite_score ?? "—"} / 100
              </p>
            )}
          </div>
        ) : null}

        {library.length ? (
          <div className="mt-8">
            <h2 className="mb-3 font-display text-sm font-semibold">Recent uploads</h2>
            <ul className="space-y-2">
              {library.map((a) => (
                <li key={a.id} className="rounded-lg border border-border px-3 py-2 text-sm">
                  {a.filename}
                  {a.is_engineering ? (
                    <span className="ml-2 text-xs text-danger">blocked</span>
                  ) : null}
                </li>
              ))}
            </ul>
          </div>
        ) : null}
      </div>
    </PermissionGate>
  );
}
