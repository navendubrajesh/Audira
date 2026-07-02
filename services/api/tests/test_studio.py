"""Tests for /studio content API."""

import pytest
from httpx import AsyncClient

AUTH = {"Authorization": "Bearer dev:admin@audira.run:admin"}


@pytest.mark.asyncio
async def test_list_drafts_seeded(client: AsyncClient):
    r = await client.get("/studio/drafts", headers=AUTH)
    assert r.status_code == 200
    drafts = r.json()
    assert len(drafts) >= 1
    assert drafts[0]["vertical"] in ("linkedin", "social", "placement", "blog")


@pytest.mark.asyncio
async def test_create_and_patch_draft(client: AsyncClient):
    r = await client.post(
        "/studio/drafts",
        headers=AUTH,
        json={"vertical": "linkedin", "title": "Test post", "body": "Hello world"},
    )
    assert r.status_code == 201
    draft_id = r.json()["id"]
    r2 = await client.patch(
        f"/studio/drafts/{draft_id}",
        headers=AUTH,
        json={"composite_score": 80.0, "status": "review"},
    )
    assert r2.status_code == 200
    assert r2.json()["composite_score"] == 80.0


@pytest.mark.asyncio
async def test_schedule_and_publish(client: AsyncClient):
    drafts = (await client.get("/studio/drafts?vertical=linkedin", headers=AUTH)).json()
    draft_id = drafts[0]["id"]
    r = await client.post(
        "/studio/schedule",
        headers=AUTH,
        json={
            "draft_id": draft_id,
            "channel": "linkedin",
            "scheduled_at": "2026-08-01T09:00:00+00:00",
        },
    )
    assert r.status_code == 201
    sched = (await client.get("/studio/schedule", headers=AUTH)).json()
    assert any(s["draft_id"] == draft_id for s in sched)
    pub = await client.post(f"/studio/publish/{draft_id}", headers=AUTH)
    assert pub.status_code == 200
    assert pub.json()["status"] == "published"


@pytest.mark.asyncio
async def test_approvals_and_engagement(client: AsyncClient):
    approvals = (await client.get("/studio/approvals", headers=AUTH)).json()
    assert len(approvals) >= 1
    queue = (await client.get("/studio/engagement/queue", headers=AUTH)).json()
    assert len(queue) >= 1
    post_id = queue[0]["id"]
    draft = await client.post(
        "/studio/engagement/draft-comment",
        headers=AUTH,
        json={"post_id": post_id},
    )
    assert draft.status_code == 200
    assert "comment" in draft.json()
    guard = await client.post(
        "/studio/engagement/guardrail",
        headers=AUTH,
        json={"comment": draft.json()["comment"]},
    )
    assert guard.status_code == 200
    assert "passed" in guard.json()


@pytest.mark.asyncio
async def test_analytics_dashboard(client: AsyncClient):
    r = await client.get("/features/analytics/dashboard", headers=AUTH)
    assert r.status_code == 200
    data = r.json()
    assert "avg_composite_score" in data
    assert "analyses_count" in data
