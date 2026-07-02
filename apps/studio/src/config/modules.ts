import type { ModuleConfig, ModuleId } from "@studio/types";
import {
  blogDrafts,
  linkedinDrafts,
  placementDrafts,
  socialDrafts,
} from "@studio/mock/fixtures";

export const MODULES: {
  id: ModuleId;
  label: string;
  path: string;
  badge?: number;
}[] = [
  { id: "home", label: "Command Center", path: "/home", badge: 5 },
  { id: "social", label: "Social", path: "/social", badge: 2 },
  { id: "linkedin", label: "LinkedIn", path: "/linkedin", badge: 3 },
  { id: "placement", label: "Placement", path: "/placement", badge: 1 },
  { id: "blog", label: "Blog", path: "/blog" },
  { id: "analytics", label: "Analytics", path: "/analytics" },
  { id: "assets", label: "Asset Library", path: "/assets", badge: 4 },
  { id: "governance", label: "Governance", path: "/governance", badge: 2 },
  { id: "settings", label: "Settings", path: "/settings" },
];

export const MODULE_CONFIG: Record<ModuleId, ModuleConfig> = {
  home: {
    id: "home",
    label: "Command Center",
    icon: "home",
    badge: 5,
    filterPills: ["All", "Attention", "Drafts", "Scheduled"],
    sections: [
      {
        id: "attention",
        label: "Attention queue",
        items: [
          ...socialDrafts.filter((d) => d.status === "review"),
          ...linkedinDrafts.filter((d) => d.compositeScore != null && d.compositeScore < 70),
        ],
      },
      {
        id: "recent",
        label: "Recent drafts",
        collapsible: true,
        items: [...linkedinDrafts.slice(0, 2), ...socialDrafts.slice(0, 1)],
      },
    ],
    tabs: ["compose", "insights", "activity"],
  },
  social: {
    id: "social",
    label: "Social",
    icon: "share2",
    badge: 2,
    filterPills: ["Drafts", "Scheduled", "Published", "Needs review"],
    sections: [
      { id: "accounts", label: "Connected accounts", items: [] },
      { id: "drafts", label: "Drafts", items: socialDrafts },
    ],
    tabs: ["compose", "analyze", "schedule", "insights", "assets", "activity"],
  },
  linkedin: {
    id: "linkedin",
    label: "LinkedIn",
    icon: "linkedin",
    badge: 3,
    filterPills: ["Drafts", "Scheduled", "Published", "Engagement"],
    sections: [
      { id: "personas", label: "Personas", items: [] },
      { id: "drafts", label: "Drafts", items: linkedinDrafts },
    ],
    tabs: ["compose", "analyze", "schedule", "insights", "assets", "activity"],
  },
  placement: {
    id: "placement",
    label: "Placement",
    icon: "briefcase",
    badge: 1,
    filterPills: ["Drafts", "In review", "Live"],
    sections: [
      { id: "jobs", label: "Job posts", items: placementDrafts },
      { id: "comms", label: "Candidate comms", items: [] },
    ],
    tabs: ["compose", "analyze", "schedule", "insights", "activity"],
  },
  blog: {
    id: "blog",
    label: "Blog",
    icon: "file-text",
    filterPills: ["Drafts", "Scheduled", "Published", "SEO"],
    sections: [
      { id: "series", label: "Series", items: [] },
      { id: "drafts", label: "Drafts", items: blogDrafts },
    ],
    tabs: ["compose", "analyze", "schedule", "insights", "assets", "activity"],
  },
  analytics: {
    id: "analytics",
    label: "Analytics",
    icon: "bar-chart3",
    filterPills: ["Dashboards", "Scorecards", "Benchmarks"],
    sections: [
      {
        id: "dashboards",
        label: "Dashboards",
        items: [
          {
            id: "an-dash-1",
            title: "Program health — Q2",
            vertical: "analytics",
            status: "published",
            updatedAt: "2026-07-01T00:00:00Z",
            excerpt: "Cross-channel effectiveness trend + team scorecards.",
            storyIds: ["TCA-014"],
          },
        ],
      },
    ],
    tabs: ["insights", "activity"],
  },
  assets: {
    id: "assets",
    label: "Asset Library",
    icon: "folder",
    badge: 4,
    filterPills: ["All", "Images", "Code", "Diagrams"],
    sections: [
      {
        id: "recent-uploads",
        label: "Recent uploads",
        items: [
          {
            id: "asset-001",
            title: "architecture-diagram.png",
            vertical: "assets",
            status: "draft",
            updatedAt: "2026-07-03T07:30:00Z",
            excerpt: "Routed to visual-text alignment scorer (TCA-084).",
            storyIds: ["TCA-079"],
          },
        ],
      },
    ],
    tabs: ["assets", "activity"],
  },
  governance: {
    id: "governance",
    label: "Governance & Admin",
    icon: "shield",
    badge: 2,
    filterPills: ["Standards", "Approvals", "Audit", "Models"],
    sections: [
      {
        id: "approvals",
        label: "Pending approvals",
        items: [
          {
            id: "gov-001",
            title: "Social carousel — Q3 launch",
            vertical: "governance",
            status: "review",
            updatedAt: "2026-07-02T17:00:00Z",
            excerpt: "Awaiting brand manager sign-off (E13).",
            storyIds: ["TCA-013"],
          },
        ],
      },
    ],
    tabs: ["activity", "insights"],
  },
  settings: {
    id: "settings",
    label: "Settings",
    icon: "settings",
    filterPills: ["General", "Integrations", "Security"],
    sections: [
      {
        id: "config",
        label: "Configuration",
        items: [
          {
            id: "set-residency",
            title: "Data residency — India (Mumbai)",
            vertical: "settings",
            status: "published",
            updatedAt: "2026-06-15T00:00:00Z",
            excerpt: "TCA-068 — tenant-pinned storage; DPDP/GDPR note visible.",
            storyIds: ["TCA-068", "TCA-067"],
          },
        ],
      },
    ],
    tabs: ["activity"],
  },
  competitors: {
    id: "competitors",
    label: "Competitor Landscape",
    icon: "table",
    filterPills: ["All", "Neuro-Predictive", "Governance"],
    sections: [],
    tabs: ["insights"],
  },
};

export function getDefaultContextId(module: ModuleId): string {
  const config = MODULE_CONFIG[module];
  for (const section of config.sections) {
    if (section.items.length > 0) return section.items[0].id;
  }
  return `${module}-default`;
}
