import { useCallback, useEffect, useState } from "react";

import { PermissionGate } from "@studio/components/auth/permission-gate";
import { Button } from "@studio/components/ui/button";
import { StoryIdBadge } from "@studio/components/ui/badge";
import { GlobalStatePanel } from "@studio/components/shared/global-states";
import {
  getResidency,
  updateResidency,
  verifyIsolation,
  type Residency,
} from "@studio/services/context-api";
import { ApiError } from "@studio/lib/api-client";

/** TCA-068 — Data residency & tenant isolation */
export function ResidencyScreen() {
  const [data, setData] = useState<Residency | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isolationOk, setIsolationOk] = useState<boolean | null>(null);

  const load = useCallback(async () => {
    setLoading(true);
    try {
      setData(await getResidency());
    } catch (e) {
      setError(e instanceof ApiError ? e.message : "Failed to load residency");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void load();
  }, [load]);

  async function handleRegionChange(field: "storage_region" | "processing_region", value: string) {
    try {
      setData(await updateResidency({ [field]: value }));
    } catch (e) {
      setError(e instanceof ApiError ? e.message : "Update failed");
    }
  }

  async function runIsolationCheck() {
    try {
      const result = await verifyIsolation();
      setIsolationOk(result.cross_tenant_access_blocked);
    } catch {
      setIsolationOk(false);
    }
  }

  if (loading) return <GlobalStatePanel variant="loading" />;
  if (!data) {
    return (
      <GlobalStatePanel variant="error" actionLabel="Retry" onAction={() => void load()} />
    );
  }

  return (
    <div>
      <div className="mb-4 flex items-center gap-2">
        <h2 className="font-display text-lg font-semibold">Data residency</h2>
        <StoryIdBadge id="TCA-068" />
      </div>
      {error ? <p className="mb-3 text-sm text-danger">{error}</p> : null}

      <dl className="grid gap-4 sm:grid-cols-2">
        <div className="rounded-lg border border-border p-4">
          <dt className="text-xs font-medium text-muted-foreground">Storage region</dt>
          <dd className="mt-1 font-medium">{data.storage_region_label}</dd>
          <PermissionGate permission="users.manage" fallback={null}>
            <select
              className="mt-2 rounded-md border border-border px-2 py-1 text-sm"
              value={data.storage_region}
              onChange={(e) => void handleRegionChange("storage_region", e.target.value)}
            >
              <option value="in">India (Mumbai)</option>
              <option value="eu">European Union</option>
            </select>
          </PermissionGate>
        </div>
        <div className="rounded-lg border border-border p-4">
          <dt className="text-xs font-medium text-muted-foreground">Processing region</dt>
          <dd className="mt-1 font-medium">{data.processing_region_label}</dd>
          <PermissionGate permission="users.manage" fallback={null}>
            <select
              className="mt-2 rounded-md border border-border px-2 py-1 text-sm"
              value={data.processing_region}
              onChange={(e) => void handleRegionChange("processing_region", e.target.value)}
            >
              <option value="in">India (Mumbai)</option>
              <option value="eu">European Union</option>
            </select>
          </PermissionGate>
        </div>
        <div className="rounded-lg border border-border p-4">
          <dt className="text-xs font-medium text-muted-foreground">Encryption at rest</dt>
          <dd className="mt-1">{data.encryption_at_rest}</dd>
        </div>
        <div className="rounded-lg border border-border p-4">
          <dt className="text-xs font-medium text-muted-foreground">TLS minimum</dt>
          <dd className="mt-1">{data.tls_min_version}+</dd>
        </div>
      </dl>

      <div className="mt-4 flex flex-wrap items-center gap-3">
        {data.tenant_isolation ? (
          <span className="text-sm font-medium text-success">Tenant isolation active</span>
        ) : null}
        <PermissionGate permission="audit.view">
          <Button variant="outline" size="sm" onClick={() => void runIsolationCheck()}>
            Verify isolation
          </Button>
          {isolationOk != null ? (
            <span className="text-xs text-muted-foreground">
              Cross-tenant blocked: {isolationOk ? "yes" : "no"}
            </span>
          ) : null}
        </PermissionGate>
      </div>

      <p className="mt-4 rounded-lg border border-primary/30 bg-primary/5 p-3 text-xs">
        DPDP/GDPR: residency is tenant-configurable — not assumed. Confirm region pinning before
        processing sensitive comms.
      </p>
    </div>
  );
}
