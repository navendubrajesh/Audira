import type { FeedbackCategory } from "@/types";

export interface ScoreRequest {
  text: string;
  personaId: string;
  variant: "A" | "B";
}

export interface ScoreResult {
  compositeScore: number;
  categories: FeedbackCategory[];
}

// TODO(TCA-083): Wire to neuro engine 4-part feedback matrix API
// TODO(TCA-087): Replace mock with streaming real-time feedback endpoint
export async function scoreDraft(req: ScoreRequest): Promise<ScoreResult> {
  await new Promise((r) => setTimeout(r, 280));

  const len = req.text.length;
  const depthBase = req.text.includes("```") ? 7.8 : 6.2;
  const personaBoost = req.personaId === "engineering-leader" ? 0.4 : 0;
  const variantPenalty = req.variant === "B" ? -3 : 0;

  const categories: FeedbackCategory[] = [
    {
      id: "technical-depth",
      category: "Technical Depth & Authenticity",
      score: Math.min(10, depthBase + personaBoost + (len > 400 ? 0.8 : -0.5)),
      maxScore: 10,
      insight:
        req.text.includes("tribe")
          ? "Strong reference to TRIBE v2 methodology; peer engineers will recognize the framework."
          : "Post reads approachable but lacks a concrete technical anchor for senior peers.",
      recommendedFix:
        "Add one specific implementation detail — latency numbers, model routing decision, or failure mode you observed.",
      highlightStart: 0,
      highlightEnd: 120,
      storyIds: ["TCA-086", "TCA-083"],
    },
    {
      id: "visual-alignment",
      category: "Visual-Text Alignment",
      score: req.text.toLowerCase().includes("diagram") ? 8.1 : 5.4,
      maxScore: 10,
      insight:
        "Architecture diagram is referenced but the narrative does not walk the reader through layers top-to-bottom.",
      recommendedFix:
        "Add a numbered walkthrough matching diagram zones: ingress → inference tier → feedback loop.",
      highlightStart: 180,
      highlightEnd: 320,
      storyIds: ["TCA-084", "TCA-083"],
    },
    {
      id: "structure",
      category: "Structure & Readability",
      score: len > 600 ? 6.8 : 8.2,
      maxScore: 10,
      insight:
        len > 600
          ? "LinkedIn feed truncation risk — key insight buried after paragraph three."
          : "Scannable opening hook with clear section breaks.",
      recommendedFix:
        "Move the outcome metric into the first 210 characters; use a single H2-style line break before the code block.",
      highlightStart: 0,
      highlightEnd: 210,
      storyIds: ["TCA-085", "TCA-083"],
    },
    {
      id: "authenticity",
      category: "Anti-Generic Authenticity",
      score: req.text.includes("we shipped") ? 8.6 : 5.9,
      maxScore: 10,
      insight:
        req.text.includes("we shipped")
          ? "First-person delivery signal reads credible for a practitioner audience."
          : "Tone skews vendor-marketing; Technical Peer persona will discount claims without evidence.",
      recommendedFix:
        "Replace abstract benefits with one shipped constraint you traded off (cost, latency, or compliance).",
      highlightStart: 320,
      highlightEnd: len,
      storyIds: ["TCA-078", "TCA-086", "TCA-083"],
    },
  ];

  const avg =
    categories.reduce((s, c) => s + c.score, 0) / categories.length;
  const compositeScore = Math.round(
    Math.max(0, Math.min(100, avg * 10 + variantPenalty)),
  );

  return { compositeScore, categories };
}

// TODO(TCA-044): AI rewrite assist with guardrails
export async function rewriteAssist(_text: string): Promise<string> {
  await new Promise((r) => setTimeout(r, 400));
  return "Rewrite suggestion stub — human review required per TCA-037 guardrails.";
}

// TODO(TCA-088): Peer-post relevance ranker
export async function rankPeerPosts(): Promise<unknown[]> {
  return [];
}
