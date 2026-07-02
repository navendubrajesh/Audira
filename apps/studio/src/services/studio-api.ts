import { apiFetch } from "@studio/lib/api-client";
import type { DraftItem, ModuleId } from "@studio/types";

export type ApiDraft = {
  id: string;
  vertical: string;
  title: string;
  body: string;
  status: DraftItem["status"];
  composite_score: number | null;
  excerpt: string;
  story_ids: string[];
  objective: string | null;
  updated_at: string;
};

export function toDraftItem(d: ApiDraft): DraftItem {
  return {
    id: d.id,
    title: d.title,
    vertical: d.vertical as ModuleId,
    status: d.status,
    compositeScore: d.composite_score ?? undefined,
    updatedAt: d.updated_at,
    excerpt: d.excerpt,
    storyIds: d.story_ids,
  };
}

export async function listDrafts(vertical?: ModuleId) {
  const q = vertical ? `?vertical=${vertical}` : "";
  const rows = await apiFetch<ApiDraft[]>(`/studio/drafts${q}`);
  return rows.map(toDraftItem);
}

export async function createDraft(body: {
  vertical: ModuleId;
  title: string;
  body?: string;
  objective?: string;
}) {
  return apiFetch<ApiDraft>("/studio/drafts", {
    method: "POST",
    body: JSON.stringify(body),
  });
}

export async function updateDraft(
  id: string,
  patch: Partial<{
    title: string;
    body: string;
    status: string;
    composite_score: number;
    analysis_run_id: string;
    objective: string;
  }>,
) {
  return apiFetch<ApiDraft>(`/studio/drafts/${id}`, {
    method: "PATCH",
    body: JSON.stringify(patch),
  });
}

export type ScheduleItem = {
  id: string;
  draft_id: string;
  title: string;
  vertical: string;
  channel: string;
  scheduled_at: string;
  status: string;
  excerpt?: string;
};

export async function listSchedule() {
  return apiFetch<ScheduleItem[]>("/studio/schedule");
}

export async function scheduleDraft(body: {
  draft_id: string;
  channel: string;
  scheduled_at: string;
}) {
  return apiFetch<{ id: string; status: string }>("/studio/schedule", {
    method: "POST",
    body: JSON.stringify(body),
  });
}

export async function publishDraft(draftId: string) {
  return apiFetch<{ queued: boolean; status: string }>(`/studio/publish/${draftId}`, {
    method: "POST",
  });
}

export type ApprovalItem = {
  id: string;
  draft_id: string;
  title: string;
  status: string;
  requested_by: string;
  reviewer_email: string | null;
  notes: string | null;
};

export async function listApprovals() {
  return apiFetch<ApprovalItem[]>("/studio/approvals");
}

export async function transitionApproval(id: string, status: string, notes?: string) {
  return apiFetch<{ id: string; status: string }>(`/studio/approvals/${id}/transition`, {
    method: "POST",
    body: JSON.stringify({ status, notes }),
  });
}

export type EngagementPost = {
  id: string;
  author: string;
  title: string;
  body: string;
  topic: string;
  relevance: number;
};

export async function listEngagementQueue() {
  return apiFetch<EngagementPost[]>("/studio/engagement/queue");
}

export async function draftComment(postId: string, context?: string) {
  return apiFetch<{ comment: string }>("/studio/engagement/draft-comment", {
    method: "POST",
    body: JSON.stringify({ post_id: postId, draft_context: context }),
  });
}

export async function checkCommentGuardrail(comment: string) {
  return apiFetch<{ passed: boolean; message: string }>("/studio/engagement/guardrail", {
    method: "POST",
    body: JSON.stringify({ comment }),
  });
}

export async function listAssetUploads() {
  return apiFetch<
    Array<{ id: string; filename: string; content_type: string; is_engineering: boolean }>
  >("/studio/assets");
}
