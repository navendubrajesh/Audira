import { apiFetch } from "@studio/lib/api-client";

export type ModelEntry = {
  model_id: string;
  version: string;
  licence: string;
  commercial_ok: boolean;
  status: string;
  modalities: string[];
  legal_signoff: boolean;
  changelog: Array<{ version: string; note: string }>;
};

export type ValidationMetric = {
  metric_name: string;
  accuracy: number;
  sample_size: number;
  methodology: string;
};

export type AuditEntry = {
  id: string;
  action: string;
  actor_email: string | null;
  resource: string | null;
  created_at: string;
};

export async function listModels() {
  return apiFetch<ModelEntry[]>("/governance/models");
}

export async function listValidationMetrics() {
  return apiFetch<ValidationMetric[]>("/governance/validation-metrics");
}

export async function listAuditLog(limit = 50, offset = 0) {
  return apiFetch<{ entries: AuditEntry[]; total: number }>(
    `/admin/audit?limit=${limit}&offset=${offset}`,
  );
}

export async function getInferenceMetrics() {
  return apiFetch<{
    tenant_id: string;
    monthly_spend_usd: number;
    monthly_cap_usd: number;
    jobs_completed: number;
    jobs_sla_breach: number;
    p95_latency_ms: number;
  }>("/inference/metrics");
}

export async function getHealth() {
  return apiFetch<{ status: string }>("/health");
}

export async function getInferenceHealth() {
  return apiFetch<{ status: string; inference_configured?: boolean }>("/health/inference");
}
