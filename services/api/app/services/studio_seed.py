"""Seed studio drafts, schedule, approvals, engagement queue per tenant."""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.studio import ApprovalRequest, ContentDraft, EngagementPeerPost, ScheduledPublish

DEFAULT_DRAFTS = [
    {
        "vertical": "linkedin",
        "title": "TRIBE v2 split-panel analyzer walkthrough",
        "body": "We shipped a split-panel analyzer for enterprise comms last sprint.\n\nThe architecture routes draft edits through a debounced scoring loop.",
        "status": "draft",
        "composite_score": 72.0,
        "excerpt": "Debounced scoring loop — 4-part feedback matrix…",
        "story_ids": ["TCA-091", "TCA-083"],
        "objective": "engage",
    },
    {
        "vertical": "linkedin",
        "title": "Counter-perspective: microservices vs modular monolith",
        "body": "Appreciate the framing on service boundaries — we saw similar trade-offs when scaling inference.",
        "status": "review",
        "composite_score": 65.0,
        "excerpt": "Engagement helper draft — tone guardrail flagged assertiveness.",
        "story_ids": ["TCA-089", "TCA-090"],
        "objective": "engage",
    },
    {
        "vertical": "social",
        "title": "Q3 platform launch — Instagram carousel",
        "body": "Hook frame needs saliency boost on product badge for mobile feed.",
        "status": "draft",
        "composite_score": 68.0,
        "excerpt": "Hook frame needs saliency boost…",
        "story_ids": ["TCA-029"],
        "objective": "engage",
    },
    {
        "vertical": "placement",
        "title": "Senior ML Platform Engineer — Naukri",
        "body": "Join our platform team building neuro-grounded comms tooling. Inclusive language verified.",
        "status": "draft",
        "composite_score": 71.0,
        "excerpt": "Bias check flagged inclusive language suggestions.",
        "story_ids": ["TCA-059"],
        "objective": "drive_action",
    },
    {
        "vertical": "blog",
        "title": "Series: Neuro-grounded comms — Part 2",
        "body": "Long-form exploration of attention proxies in enterprise comms analysis.",
        "status": "draft",
        "composite_score": 74.0,
        "excerpt": "SEO queue: meta description review pending.",
        "story_ids": ["TCA-034"],
        "objective": "inform",
    },
]

DEFAULT_PEER_POSTS = [
    {
        "author": "Priya Sharma",
        "title": "Why most LLM eval pipelines miss audience emotion",
        "body": "Most benchmarks optimize for accuracy on static sets, not predicted reader response in enterprise comms.",
        "topic": "ML evaluation",
        "relevance_score": 92.0,
    },
    {
        "author": "Marcus Chen",
        "title": "We moved inference off Vercel — here's the cost curve",
        "body": "GPU autoscaling changed our unit economics — happy to share latency percentiles from our pilot.",
        "topic": "Platform scale",
        "relevance_score": 87.0,
    },
    {
        "author": "Anika Patel",
        "title": "DPDP compliance for comms analytics — practical checklist",
        "body": "Tenant isolation and residency pinning are table stakes for India enterprise pilots.",
        "topic": "Compliance",
        "relevance_score": 78.0,
    },
]


async def seed_studio_content(db: AsyncSession, tenant_id: UUID, user_id: UUID) -> None:
    existing = await db.scalar(
        select(ContentDraft.id).where(ContentDraft.tenant_id == tenant_id).limit(1)
    )
    if existing:
        return

    draft_rows: list[ContentDraft] = []
    for item in DEFAULT_DRAFTS:
        d = ContentDraft(tenant_id=tenant_id, user_id=user_id, **item)
        db.add(d)
        draft_rows.append(d)
    await db.flush()

    if draft_rows:
        from datetime import UTC, datetime, timedelta

        sched = ScheduledPublish(
            tenant_id=tenant_id,
            draft_id=draft_rows[0].id,
            channel="linkedin",
            scheduled_at=datetime.now(UTC) + timedelta(days=2),
            status="scheduled",
        )
        db.add(sched)

        approval = ApprovalRequest(
            tenant_id=tenant_id,
            draft_id=draft_rows[1].id if len(draft_rows) > 1 else draft_rows[0].id,
            title=draft_rows[1].title if len(draft_rows) > 1 else draft_rows[0].title,
            status="pending_review",
            requested_by="comms@audira.run",
        )
        db.add(approval)

    for post in DEFAULT_PEER_POSTS:
        db.add(EngagementPeerPost(tenant_id=tenant_id, **post))

    await db.commit()
