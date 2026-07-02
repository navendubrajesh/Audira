import type { BacklogStory, CompetitorRow, DraftItem, Persona } from "@studio/types";
import rawBacklog from "./backlog-data.json";

export const PRODUCT_NAME = "Audira.run";
export const PRODUCT_TAGLINE =
  "Pre-send neuro-grounded analysis for enterprise communications";

export const backlogStories = rawBacklog.backlog as BacklogStory[];
export const competitors = rawBacklog.competitors as CompetitorRow[];

export const DEFAULT_PERSONAS: Persona[] = [
  {
    id: "technical-peer",
    label: "Technical Peer",
    description: "Senior engineer evaluating architecture claims and code snippets.",
    storyId: "TCA-077",
  },
  {
    id: "engineering-leader",
    label: "Engineering Leader",
    description: "Director/VP scanning for ROI, risk, and team impact signals.",
    storyId: "TCA-077",
  },
  {
    id: "platform-architect",
    label: "Platform Architect",
    description: "Cross-stack reviewer focused on integration patterns and scale.",
    storyId: "TCA-077",
  },
  {
    id: "hiring-manager",
    label: "Hiring Manager",
    description: "Evaluates clarity and inclusivity of job posts (Placement vertical).",
    storyId: "TCA-077",
  },
];

export const LINKEDIN_SAMPLE_DRAFT = `We shipped a split-panel analyzer for enterprise comms last sprint.

The architecture routes draft edits through a debounced scoring loop — authors see a 4-part feedback matrix (technical depth, visual alignment, structure, authenticity) without leaving the editor.

\`\`\`python
# Inference orchestration sketch
async def score_draft(text: str, persona: str) -> FeedbackMatrix:
    features = await tribe_v2.encode(text, assets=attached)
    return matrix.from_features(features, persona_weights=persona)
\`\`\`

See the attached architecture diagram for the ingress → GPU tier → feedback path.

Key outcome: composite effectiveness score moved from 61 → 78 on pilot drafts after one revision cycle.`;

export const socialDrafts: DraftItem[] = [
  {
    id: "soc-001",
    title: "Q3 platform launch — Instagram carousel",
    vertical: "social",
    status: "draft",
    compositeScore: 68,
    updatedAt: "2026-07-02T14:20:00Z",
    excerpt: "Hook frame needs saliency boost on product badge…",
    storyIds: ["TCA-029", "TCA-004"],
  },
  {
    id: "soc-002",
    title: "Engineering culture — TikTok short",
    vertical: "social",
    status: "review",
    compositeScore: 54,
    updatedAt: "2026-07-01T09:10:00Z",
    excerpt: "First 3 seconds below attention threshold for Gen-Z IT audience.",
    storyIds: ["TCA-029"],
  },
  {
    id: "soc-003",
    title: "Thought leadership clip — YouTube Shorts",
    vertical: "social",
    status: "scheduled",
    compositeScore: 81,
    updatedAt: "2026-06-30T16:00:00Z",
    excerpt: "Scheduled for Fri 09:00 IST — caption optimized for mobile.",
    storyIds: ["TCA-011"],
  },
];

export const linkedinDrafts: DraftItem[] = [
  {
    id: "li-001",
    title: "TRIBE v2 split-panel analyzer walkthrough",
    vertical: "linkedin",
    status: "draft",
    compositeScore: 72,
    updatedAt: "2026-07-03T08:00:00Z",
    excerpt: LINKEDIN_SAMPLE_DRAFT.slice(0, 90) + "…",
    storyIds: ["TCA-091", "TCA-083"],
  },
  {
    id: "li-002",
    title: "Counter-perspective: microservices vs modular monolith",
    vertical: "linkedin",
    status: "review",
    compositeScore: 65,
    updatedAt: "2026-07-02T11:30:00Z",
    excerpt: "Engagement helper draft — tone guardrail flagged assertiveness.",
    storyIds: ["TCA-089", "TCA-090"],
  },
  {
    id: "li-003",
    title: "Published — DPDP-ready comms governance",
    vertical: "linkedin",
    status: "published",
    compositeScore: 88,
    updatedAt: "2026-06-28T10:00:00Z",
    excerpt: "Live post — 412 reactions, prediction accuracy within 8%.",
    storyIds: ["TCA-068"],
  },
];

export const placementDrafts: DraftItem[] = [
  {
    id: "pl-001",
    title: "Senior ML Platform Engineer — Naukri",
    vertical: "placement",
    status: "draft",
    compositeScore: 71,
    updatedAt: "2026-07-02T13:00:00Z",
    excerpt: "Bias check flagged 'rockstar' — inclusive language suggestion ready.",
    storyIds: ["TCA-059", "TCA-006"],
  },
  {
    id: "pl-002",
    title: "Candidate nurture — interview scheduling",
    vertical: "placement",
    status: "review",
    compositeScore: 79,
    updatedAt: "2026-07-01T15:45:00Z",
    excerpt: "Template clarity score 8.2/10 — readability pass.",
    storyIds: ["TCA-006"],
  },
];

export const blogDrafts: DraftItem[] = [
  {
    id: "bl-001",
    title: "Series: Neuro-grounded comms — Part 2",
    vertical: "blog",
    status: "draft",
    compositeScore: 74,
    updatedAt: "2026-07-02T10:00:00Z",
    excerpt: "SEO queue: meta description exceeds pixel width on mobile SERP.",
    storyIds: ["TCA-007", "TCA-034"],
  },
  {
    id: "bl-002",
    title: "Measuring memorability in internal town halls",
    vertical: "blog",
    status: "scheduled",
    compositeScore: 82,
    updatedAt: "2026-06-29T12:00:00Z",
    excerpt: "WordPress publish scheduled — key message findability 8.6/10.",
    storyIds: ["TCA-034"],
  },
];

export const engagementQueue = [
  {
    id: "eng-001",
    author: "Priya Sharma",
    title: "Why most LLM eval pipelines miss audience emotion",
    relevance: 92,
    topic: "ML evaluation",
    storyIds: ["TCA-088"],
  },
  {
    id: "eng-002",
    author: "Marcus Chen",
    title: "We moved inference off Vercel — here's the cost curve",
    relevance: 87,
    topic: "Platform scale",
    storyIds: ["TCA-088", "TCA-072"],
  },
  {
    id: "eng-003",
    author: "Anika Patel",
    title: "DPDP compliance for comms analytics — practical checklist",
    relevance: 78,
    topic: "Compliance",
    storyIds: ["TCA-088", "TCA-068"],
  },
];

export function storiesForEpic(epicPrefix: string): BacklogStory[] {
  return backlogStories.filter((s) => s.Epic.startsWith(epicPrefix));
}

export function storyById(id: string): BacklogStory | undefined {
  return backlogStories.find((s) => s.ID === id);
}

export function storiesByStatus(status: BacklogStory["Status"]) {
  return backlogStories.filter((s) => s.Status === status);
}
