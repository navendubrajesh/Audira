import { apiFetch } from "@studio/lib/api-client";

export type Audience = {
  id: string;
  name: string;
  role: string | null;
  region: string | null;
  language: string | null;
  seniority: string | null;
  attributes: Record<string, unknown>;
  is_default: boolean;
};

export type ArtifactType = {
  id: string;
  code: string;
  label: string;
  checks: string[];
  block_engineering: boolean;
  is_active: boolean;
};

export type StandardsRule = {
  id: string;
  version: number;
  status: string;
  artifact_type_code: string | null;
  rule_type: string;
  pattern: string;
  replacement: string | null;
  metadata: Record<string, unknown>;
};

export type BrandProfile = {
  id: string;
  version: number;
  status: string;
  voice_attributes: Record<string, unknown>;
  terminology_do: string[];
  terminology_dont: string[];
  messaging_pillars: string[];
  target_tone: string;
};

export type QualityGates = {
  pass_threshold: number;
  needs_work_threshold: number;
  block_publish_on_fail: boolean;
  tenant_id: string;
};

export async function listAudiences() {
  return apiFetch<Audience[]>("/audiences");
}

export async function createAudience(body: Omit<Audience, "id" | "attributes" | "is_default"> & { attributes?: Record<string, unknown> }) {
  return apiFetch<Audience>("/audiences", { method: "POST", body: JSON.stringify(body) });
}

export async function deleteAudience(id: string) {
  return apiFetch<void>(`/audiences/${id}`, { method: "DELETE" });
}

export async function listArtifactTypes() {
  return apiFetch<ArtifactType[]>("/context/artifact-types");
}

export async function listStandards() {
  return apiFetch<StandardsRule[]>("/context/standards");
}

export async function createStandard(body: {
  artifact_type_code?: string;
  rule_type: string;
  pattern: string;
  replacement?: string;
  status?: string;
}) {
  return apiFetch<{ id: string; status: string }>("/context/standards", {
    method: "POST",
    body: JSON.stringify(body),
  });
}

export async function publishStandard(ruleId: string) {
  return apiFetch<{ id: string; status: string; version: number }>(
    `/context/standards/${ruleId}/publish`,
    { method: "POST" },
  );
}

export async function getBrandProfile() {
  return apiFetch<BrandProfile>("/context/brand");
}

export async function updateBrandProfile(body: {
  voice_attributes?: Record<string, unknown>;
  terminology_do?: string[];
  terminology_dont?: string[];
  messaging_pillars?: string[];
  target_tone?: string;
}) {
  return apiFetch<{ id: string; version: number; status: string }>("/context/brand", {
    method: "PUT",
    body: JSON.stringify(body),
  });
}

export async function getQualityGates() {
  return apiFetch<QualityGates>("/context/quality-gates");
}

export async function updateQualityGates(body: Partial<QualityGates>) {
  return apiFetch<QualityGates>("/context/quality-gates", {
    method: "PATCH",
    body: JSON.stringify(body),
  });
}

export type Residency = {
  tenant_id: string;
  tenant_name: string;
  storage_region: string;
  storage_region_label: string;
  storage_cloud_region: string;
  processing_region: string;
  processing_region_label: string;
  processing_cloud_region: string;
  encryption_at_rest: string;
  tls_min_version: string;
  encryption_key_id: string | null;
  tenant_isolation: boolean;
};

export async function getResidency() {
  return apiFetch<Residency>("/tenant/residency");
}

export async function updateResidency(body: {
  storage_region?: string;
  processing_region?: string;
  encryption_key_id?: string;
}) {
  return apiFetch<Residency>("/tenant/residency", {
    method: "PATCH",
    body: JSON.stringify(body),
  });
}

export async function verifyIsolation() {
  return apiFetch<{ status: string; cross_tenant_access_blocked: boolean }>(
    "/tenant/residency/verify",
  );
}
