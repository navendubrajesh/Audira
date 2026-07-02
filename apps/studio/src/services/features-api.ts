import { apiFetch } from "@studio/lib/api-client";

export async function getAnalyticsDashboard() {
  return apiFetch<{
    avg_composite_score: number;
    analyses_count: number;
    recent_trend: Array<{ id: string; score: number; at: string }>;
    by_channel: Array<{ channel: string; avg_score: number; count: number }>;
  }>("/features/analytics/dashboard");
}

export async function getTeamScorecards() {
  return apiFetch<{
    scorecards: Array<{ author_id: string; avg_score: number; analyses: number }>;
  }>("/features/scorecards");
}

export async function listCampaigns() {
  return apiFetch<{ campaigns: Array<{ id: string; title: string; status: string; composite_score: number }> }>(
    "/features/campaigns",
  );
}

export async function listIntegrations() {
  return apiFetch<{ integrations: Array<{ id: string; status: string; endpoint?: string }> }>(
    "/features/integrations",
  );
}

export async function getGuardrailSettings() {
  return apiFetch<{
    generative_governance: boolean;
    rewrite_assist: boolean;
    regulated_claims: boolean;
    block_on_fail: boolean;
  }>("/guardrails/settings");
}

export async function updateGuardrailSettings(body: {
  generative_governance?: boolean;
  rewrite_assist?: boolean;
  regulated_claims?: boolean;
  block_on_fail?: boolean;
}) {
  return apiFetch("/guardrails/settings", { method: "PATCH", body: JSON.stringify(body) });
}

export async function proposeRewrite(text: string, suggestion: string) {
  return apiFetch<{ proposed: string; status: string; message: string }>(
    "/guardrails/rewrite/propose",
    { method: "POST", body: JSON.stringify({ text, suggestion }) },
  );
}

export async function listAnalysisRuns() {
  return apiFetch<
    Array<{ id: string; composite_score: number; artifact_type_code: string; objective: string; verdict: string; created_at: string }>
  >("/analyze/runs");
}

export async function listRunComments(runId: string) {
  return apiFetch<Array<{ id: string; body: string; author_email: string; resolved: boolean }>>(
    `/features/comments/${runId}`,
  );
}

export async function addRunComment(runId: string, body: string) {
  return apiFetch(`/features/comments/${runId}`, {
    method: "POST",
    body: JSON.stringify({ body }),
  });
}

export async function runWhatIf(text: string, changes: string[]) {
  return apiFetch<{ baseline_score: number; projected_score: number; delta: number }>(
    "/features/simulations/what-if",
    { method: "POST", body: JSON.stringify({ text, changes }) },
  );
}

export async function checkBias(text: string) {
  return apiFetch<Record<string, unknown>>("/features/bias-check", {
    method: "POST",
    body: JSON.stringify({ text }),
  });
}
