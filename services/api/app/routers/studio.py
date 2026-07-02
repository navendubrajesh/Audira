"""Studio content API — drafts, schedule, approvals, assets, LinkedIn engagement."""

from datetime import UTC, datetime
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import get_current_user, require_permission
from app.auth.principal import Principal
from app.db.session import get_db
from app.models.analysis import ArtifactUpload
from app.models.studio import (
    ApprovalRequest,
    ContentDraft,
    EngagementPeerPost,
    ScheduledPublish,
)
from app.services.audit import record_audit
from app.services.guardrails import check_generative_governance
from app.services.studio_seed import seed_studio_content
from app.services.tenant_service import assert_tenant_resource, TenantIsolationError

router = APIRouter(prefix="/studio", tags=["studio"])


class DraftBody(BaseModel):
    vertical: str = Field(..., min_length=1, max_length=32)
    title: str = Field(..., min_length=1, max_length=512)
    body: str = ""
    status: str = "draft"
    objective: str | None = None
    excerpt: str | None = None
    story_ids: list[str] = Field(default_factory=list)


class DraftPatch(BaseModel):
    title: str | None = None
    body: str | None = None
    status: str | None = None
    composite_score: float | None = None
    objective: str | None = None
    excerpt: str | None = None
    analysis_run_id: str | None = None


class ScheduleBody(BaseModel):
    draft_id: str
    channel: str
    scheduled_at: datetime


class ApprovalTransition(BaseModel):
    status: str = Field(..., pattern="^(pending_review|in_approval|approved|rejected)$")
    notes: str | None = None


class CommentDraftRequest(BaseModel):
    post_id: str
    perspective: str | None = "counter"
    draft_context: str | None = None


class CommentGuardrailRequest(BaseModel):
    comment: str


def _draft_dict(d: ContentDraft) -> dict:
    return {
        "id": str(d.id),
        "vertical": d.vertical,
        "title": d.title,
        "body": d.body,
        "status": d.status,
        "composite_score": d.composite_score,
        "excerpt": d.excerpt or d.body[:90] + "…",
        "story_ids": d.story_ids or [],
        "objective": d.objective,
        "analysis_run_id": str(d.analysis_run_id) if d.analysis_run_id else None,
        "updated_at": d.updated_at.isoformat(),
    }


async def _ensure_seeded(db: AsyncSession, principal: Principal) -> None:
    await seed_studio_content(db, principal.tenant_id, principal.user_id)


@router.get("/drafts")
async def list_drafts(
    principal: Annotated[Principal, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    vertical: str | None = None,
):
    """TCA-006 / vertical workspaces — list content drafts."""
    await _ensure_seeded(db, principal)
    stmt = select(ContentDraft).where(ContentDraft.tenant_id == principal.tenant_id)
    if vertical:
        stmt = stmt.where(ContentDraft.vertical == vertical)
    stmt = stmt.order_by(ContentDraft.updated_at.desc())
    result = await db.execute(stmt)
    return [_draft_dict(d) for d in result.scalars().all()]


@router.post("/drafts", status_code=status.HTTP_201_CREATED)
async def create_draft(
    body: DraftBody,
    principal: Annotated[Principal, Depends(require_permission("analyses.run"))],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    draft = ContentDraft(
        tenant_id=principal.tenant_id,
        user_id=principal.user_id,
        vertical=body.vertical,
        title=body.title,
        body=body.body,
        status=body.status,
        objective=body.objective,
        excerpt=body.excerpt,
        story_ids=body.story_ids,
    )
    db.add(draft)
    await db.commit()
    await db.refresh(draft)
    return _draft_dict(draft)


@router.get("/drafts/{draft_id}")
async def get_draft(
    draft_id: UUID,
    principal: Annotated[Principal, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    draft = await db.get(ContentDraft, draft_id)
    if not draft:
        raise HTTPException(status_code=404, detail="Draft not found")
    try:
        assert_tenant_resource(draft.tenant_id, principal.tenant_id)
    except TenantIsolationError:
        raise HTTPException(status_code=404, detail="Draft not found") from None
    return _draft_dict(draft)


@router.patch("/drafts/{draft_id}")
async def patch_draft(
    draft_id: UUID,
    body: DraftPatch,
    principal: Annotated[Principal, Depends(require_permission("analyses.run"))],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    draft = await db.get(ContentDraft, draft_id)
    if not draft:
        raise HTTPException(status_code=404, detail="Draft not found")
    try:
        assert_tenant_resource(draft.tenant_id, principal.tenant_id)
    except TenantIsolationError:
        raise HTTPException(status_code=404, detail="Draft not found") from None
    data = body.model_dump(exclude_unset=True)
    if "analysis_run_id" in data and data["analysis_run_id"]:
        data["analysis_run_id"] = UUID(data["analysis_run_id"])
    for key, val in data.items():
        setattr(draft, key, val)
    draft.updated_at = datetime.now(UTC)
    await db.commit()
    await db.refresh(draft)
    return _draft_dict(draft)


@router.delete("/drafts/{draft_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_draft(
    draft_id: UUID,
    principal: Annotated[Principal, Depends(require_permission("analyses.run"))],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    draft = await db.get(ContentDraft, draft_id)
    if not draft:
        raise HTTPException(status_code=404, detail="Draft not found")
    try:
        assert_tenant_resource(draft.tenant_id, principal.tenant_id)
    except TenantIsolationError:
        raise HTTPException(status_code=404, detail="Draft not found") from None
    await db.delete(draft)
    await db.commit()


@router.get("/schedule")
async def list_schedule(
    principal: Annotated[Principal, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """TCA-011 — scheduled publish queue."""
    await _ensure_seeded(db, principal)
    result = await db.execute(
        select(ScheduledPublish, ContentDraft)
        .join(ContentDraft, ContentDraft.id == ScheduledPublish.draft_id)
        .where(ScheduledPublish.tenant_id == principal.tenant_id)
        .order_by(ScheduledPublish.scheduled_at)
    )
    rows = []
    for sched, draft in result.all():
        rows.append(
            {
                "id": str(sched.id),
                "draft_id": str(draft.id),
                "title": draft.title,
                "vertical": draft.vertical,
                "channel": sched.channel,
                "scheduled_at": sched.scheduled_at.isoformat(),
                "status": sched.status,
                "excerpt": draft.excerpt,
            }
        )
    return rows


@router.post("/schedule", status_code=status.HTTP_201_CREATED)
async def create_schedule(
    body: ScheduleBody,
    principal: Annotated[Principal, Depends(require_permission("analyses.run"))],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    draft = await db.get(ContentDraft, UUID(body.draft_id))
    if not draft or draft.tenant_id != principal.tenant_id:
        raise HTTPException(status_code=404, detail="Draft not found")
    sched = ScheduledPublish(
        tenant_id=principal.tenant_id,
        draft_id=draft.id,
        channel=body.channel,
        scheduled_at=body.scheduled_at,
    )
    draft.status = "scheduled"
    db.add(sched)
    await db.commit()
    await record_audit(
        db,
        tenant_id=principal.tenant_id,
        action="publish.scheduled",
        actor_user_id=principal.user_id,
        actor_email=principal.email,
        resource=f"draft:{draft.id}",
        metadata={"channel": body.channel, "at": body.scheduled_at.isoformat()},
    )
    return {"id": str(sched.id), "status": "scheduled"}


@router.post("/publish/{draft_id}")
async def publish_draft(
    draft_id: UUID,
    principal: Annotated[Principal, Depends(require_permission("analyses.run"))],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """TCA-011 — channel publish stub (queues + audit; external OAuth not required for MVP)."""
    draft = await db.get(ContentDraft, draft_id)
    if not draft or draft.tenant_id != principal.tenant_id:
        raise HTTPException(status_code=404, detail="Draft not found")
    draft.status = "published"
    await db.commit()
    await record_audit(
        db,
        tenant_id=principal.tenant_id,
        action="publish.completed",
        actor_user_id=principal.user_id,
        actor_email=principal.email,
        resource=f"draft:{draft.id}",
        metadata={"vertical": draft.vertical, "channel_stub": True},
    )
    return {"queued": True, "status": "published", "draft_id": str(draft.id)}


@router.get("/approvals")
async def list_approvals(
    principal: Annotated[Principal, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """TCA-013 — approval workflow board."""
    await _ensure_seeded(db, principal)
    result = await db.execute(
        select(ApprovalRequest)
        .where(ApprovalRequest.tenant_id == principal.tenant_id)
        .order_by(ApprovalRequest.updated_at.desc())
    )
    return [
        {
            "id": str(a.id),
            "draft_id": str(a.draft_id),
            "title": a.title,
            "status": a.status,
            "requested_by": a.requested_by,
            "reviewer_email": a.reviewer_email,
            "notes": a.notes,
            "updated_at": a.updated_at.isoformat(),
        }
        for a in result.scalars().all()
    ]


@router.post("/approvals/{approval_id}/transition")
async def transition_approval(
    approval_id: UUID,
    body: ApprovalTransition,
    principal: Annotated[Principal, Depends(require_permission("standards.manage"))],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    row = await db.get(ApprovalRequest, approval_id)
    if not row or row.tenant_id != principal.tenant_id:
        raise HTTPException(status_code=404, detail="Approval not found")
    row.status = body.status
    row.notes = body.notes
    row.reviewer_email = principal.email
    row.updated_at = datetime.now(UTC)
    draft = await db.get(ContentDraft, row.draft_id)
    if draft:
        if body.status == "approved":
            draft.status = "review"
        elif body.status == "rejected":
            draft.status = "draft"
    await db.commit()
    await record_audit(
        db,
        tenant_id=principal.tenant_id,
        action="approval.transition",
        actor_user_id=principal.user_id,
        actor_email=principal.email,
        resource=f"approval:{row.id}",
        metadata={"status": body.status},
    )
    return {"id": str(row.id), "status": row.status}


@router.get("/assets")
async def list_assets(
    principal: Annotated[Principal, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """TCA-079 — asset library from uploads."""
    result = await db.execute(
        select(ArtifactUpload)
        .where(ArtifactUpload.tenant_id == principal.tenant_id)
        .order_by(ArtifactUpload.created_at.desc())
        .limit(50)
    )
    return [
        {
            "id": str(u.id),
            "filename": u.filename,
            "content_type": u.content_type,
            "is_engineering": u.is_engineering,
            "created_at": u.created_at.isoformat(),
            "story_ids": ["TCA-079"],
        }
        for u in result.scalars().all()
    ]


@router.get("/engagement/queue")
async def engagement_queue(
    principal: Annotated[Principal, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """TCA-088 — peer-post relevance queue."""
    await _ensure_seeded(db, principal)
    result = await db.execute(
        select(EngagementPeerPost)
        .where(EngagementPeerPost.tenant_id == principal.tenant_id)
        .order_by(EngagementPeerPost.relevance_score.desc())
    )
    return [
        {
            "id": str(p.id),
            "author": p.author,
            "title": p.title,
            "body": p.body,
            "topic": p.topic,
            "relevance": p.relevance_score,
            "story_ids": ["TCA-088"],
        }
        for p in result.scalars().all()
    ]


@router.post("/engagement/draft-comment")
async def draft_comment(
    body: CommentDraftRequest,
    principal: Annotated[Principal, Depends(require_permission("analyses.run"))],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """TCA-089 — counter-perspective comment draft."""
    post = await db.get(EngagementPeerPost, UUID(body.post_id))
    if not post or post.tenant_id != principal.tenant_id:
        raise HTTPException(status_code=404, detail="Post not found")
    first = post.author.split()[0]
    draft = (
        f"Appreciate the {post.topic.lower()} framing, {first}. "
        f"Re: {post.title} — {body.draft_context or 'we saw similar patterns in our pilot'}. "
        "Curious how you controlled for audience segment in the benchmark?"
    )
    return {"comment": draft, "post_id": body.post_id, "story_ids": ["TCA-089"]}


@router.post("/engagement/guardrail")
async def comment_guardrail(
    body: CommentGuardrailRequest,
    principal: Annotated[Principal, Depends(get_current_user)],
):
    """TCA-090 — tone & authority guardrail for comments."""
    gov = check_generative_governance(body.comment)
    promo_words = ("buy", "discount", "limited offer", "sign up now")
    has_promo = any(w in body.comment.lower() for w in promo_words)
    authority_ok = len(body.comment.split()) >= 12 and not has_promo
    passed = authority_ok and not gov.get("blocked", False)
    return {
        "passed": passed,
        "authority_ok": authority_ok,
        "promotional_language": has_promo,
        "governance": gov,
        "message": (
            "Assertiveness within authority band — ready to post."
            if passed
            else "Adjust tone: avoid promotional phrasing; add substantive peer perspective."
        ),
        "story_ids": ["TCA-090"],
    }
