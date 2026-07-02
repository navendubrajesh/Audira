import { apiFetch } from "@studio/lib/api-client";
import { analysisContextForModule } from "@studio/lib/channel-config";
import { proposeRewrite } from "@studio/services/features-api";
import type { FeedbackCategory, ModuleId } from "@studio/types";

export interface ScoreRequest {
  text: string;
  personaId: string;
  audienceId?: string;
  variant: "A" | "B";
  module?: ModuleId;
  fullAnalysis?: boolean;
  variantBText?: string;
}

export interface ScoreResult {
  compositeScore: number;
  categories: FeedbackCategory[];
  analysisId?: string;
  canUpgrade?: boolean;
  verdict?: string;
  rewriteSuggestions?: Array<{ type: string; suggestion: string; original?: string }>;
  modelId?: string;
  latencyMs?: number;
}

type MetricValue = { score?: number; flags?: string[]; [key: string]: unknown };

type AnalyzeResponse = {
  id: string;
  composite_score: number | null;
  latency_ms: number | null;
  model_id: string;
  result: {
    metrics: Record<string, MetricValue>;
    verdict?: { label: string };
    rewrite_suggestions?: Array<{ type: string; suggestion: string; original?: string }>;
    can_upgrade?: boolean;
    checks_run?: string[];
  };
};

function metricScore(metrics: Record<string, MetricValue>, key: string): number | null {
  const score = metrics[key]?.score;
  return typeof score === "number" ? score : null;
}

function avgScores(...scores: (number | null)[]): number {
  const valid = scores.filter((s): s is number => s != null);
  if (!valid.length) return 5;
  return valid.reduce((a, b) => a + b, 0) / valid.length;
}

function flagsText(metrics: Record<string, MetricValue>, key: string): string {
  const flags = metrics[key]?.flags;
  if (Array.isArray(flags) && flags.length) return flags.slice(0, 2).join("; ");
  return "";
}

function mapMetricsToFeedback(
  text: string,
  metrics: Record<string, MetricValue>,
): FeedbackCategory[] {
  const readability = metricScore(metrics, "readability");
  const jargon = metricScore(metrics, "jargon");
  const cognitive = metricScore(metrics, "cognitive_load");
  const structure = metricScore(metrics, "structure");
  const brand = metricScore(metrics, "brand");
  const tone = metricScore(metrics, "tone");
  const inclusive = metricScore(metrics, "inclusive");
  const engagement = metricScore(metrics, "engagement");
  const clarity = metricScore(metrics, "clarity");

  const technicalScore = avgScores(readability, jargon, cognitive, clarity);
  const structureScore = avgScores(readability, structure, cognitive);
  const alignmentScore = avgScores(structure, engagement, clarity);
  const authenticityScore = avgScores(brand, tone, inclusive);

  const len = text.length;

  return [
    {
      id: "technical-depth",
      category: "Technical Depth & Authenticity",
      score: Math.round(technicalScore * 10) / 10,
      maxScore: 10,
      insight:
        flagsText(metrics, "jargon") ||
        (jargon != null && jargon < 6
          ? "Undefined acronyms or off-list jargon detected for this audience."
          : "Vocabulary depth and readability are calibrated for the selected audience."),
      recommendedFix:
        jargon != null && jargon < 7
          ? "Define acronyms on first use and replace buzzwords with specific frameworks or benchmarks."
          : "Add one concrete implementation detail — latency, cost, or a failure mode you observed.",
      highlightStart: 0,
      highlightEnd: Math.min(180, len),
      storyIds: ["TCA-086", "TCA-083", "TCA-029"],
    },
    {
      id: "visual-alignment",
      category: "Visual-Text Alignment",
      score: Math.round(alignmentScore * 10) / 10,
      maxScore: 10,
      insight:
        structure != null && structure < 6
          ? "Structure score suggests the narrative does not walk the reader through key points in order."
          : "Text structure supports scannability; attach diagrams for full multimodal alignment scoring.",
      recommendedFix:
        "Add a numbered walkthrough matching any attached diagram zones, or break dense blocks into headings.",
      highlightStart: Math.min(120, len),
      highlightEnd: Math.min(320, len),
      storyIds: ["TCA-084", "TCA-083"],
    },
    {
      id: "structure",
      category: "Structure & Readability",
      score: Math.round(structureScore * 10) / 10,
      maxScore: 10,
      insight:
        cognitive != null && cognitive < 6
          ? "Cognitive load is high — dense paragraph blocks may cause technical readers to skim."
          : flagsText(metrics, "readability") ||
            "Readability and structure are within target for the artifact type.",
      recommendedFix:
        len > 600
          ? "Move the outcome metric into the first 210 characters; add a line break before code blocks."
          : "Use short paragraphs and one H2-style break before supporting evidence.",
      highlightStart: 0,
      highlightEnd: Math.min(210, len),
      storyIds: ["TCA-085", "TCA-083", "TCA-027"],
    },
    {
      id: "authenticity",
      category: "Anti-Generic Authenticity",
      score: Math.round(authenticityScore * 10) / 10,
      maxScore: 10,
      insight:
        flagsText(metrics, "inclusive") ||
        flagsText(metrics, "brand") ||
        (brand != null && brand < 6
          ? "Brand voice deviation detected — tone may read as generic marketing."
          : "Voice aligns with codified brand standards for this artifact type."),
      recommendedFix:
        inclusive != null && inclusive < 7
          ? "Replace exclusionary phrasing flagged by inclusive-language checks."
          : "Replace abstract benefits with one shipped constraint you traded off (cost, latency, compliance).",
      highlightStart: Math.max(0, len - 280),
      highlightEnd: len,
      storyIds: ["TCA-078", "TCA-059", "TCA-034"],
    },
  ];
}

export async function scoreDraft(req: ScoreRequest): Promise<ScoreResult> {
  const ctx = analysisContextForModule(req.module ?? "linkedin");

  const body = {
    text: req.text,
    audience_id: req.audienceId || undefined,
    artifact_type_code: ctx.artifact_type_code,
    objective: ctx.objective,
    channel: ctx.channel,
    fast_lane: !req.fullAnalysis,
    full_analysis: req.fullAnalysis ?? false,
  };

  const data = await apiFetch<AnalyzeResponse>("/analyze", {
    method: "POST",
    body: JSON.stringify(body),
  });

  const composite = data.composite_score ?? 0;
  const categories = mapMetricsToFeedback(req.text, data.result.metrics);

  return {
    compositeScore: Math.round(composite),
    categories,
    analysisId: data.id,
    canUpgrade: data.result.can_upgrade,
    verdict: data.result.verdict?.label,
    rewriteSuggestions: data.result.rewrite_suggestions,
    modelId: data.model_id,
    latencyMs: data.latency_ms ?? undefined,
  };
}

export async function compareVariants(
  variantA: string,
  variantB: string,
  module: ModuleId = "linkedin",
): Promise<{
  winner: "a" | "b";
  delta: number;
  scoreA: number;
  scoreB: number;
}> {
  const ctx = analysisContextForModule(module);
  const data = await apiFetch<{
    variant_a: { composite_score: number };
    variant_b: { composite_score: number };
    winner: "a" | "b";
    delta: number;
  }>("/analyze/compare", {
    method: "POST",
    body: JSON.stringify({
      variant_a: variantA,
      variant_b: variantB,
      objective: ctx.objective,
      artifact_type_code: ctx.artifact_type_code,
    }),
  });

  return {
    winner: data.winner,
    delta: data.delta,
    scoreA: data.variant_a.composite_score,
    scoreB: data.variant_b.composite_score,
  };
}

export async function rewriteAssist(text: string, module: ModuleId = "linkedin"): Promise<string> {
  try {
    const result = await proposeRewrite(text, "Improve clarity and technical depth for peer audience.");
    return result.proposed ?? "Rewrite proposed — pending human approval.";
  } catch {
    const result = await scoreDraft({ text, personaId: "", variant: "A", module });
    const first = result.rewriteSuggestions?.[0];
    return first?.suggestion ?? "Enable rewrite assist in Governance → Guardrails.";
  }
}

export async function uploadArtifact(file: File, artifactTypeCode = "email") {
  const form = new FormData();
  form.append("file", file);
  form.append("artifact_type_code", artifactTypeCode);
  return apiFetch<{
    upload_id?: string;
    analysis_id?: string;
    composite_score?: number;
    status?: string;
    reason?: string;
  }>("/analyze/upload", { method: "POST", body: form });
}
