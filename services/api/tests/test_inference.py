"""Inference architecture tests (TCA-072)."""

import uuid

import pytest
from httpx import AsyncClient

from app.services.inference_runner import run_inference_job_by_id


@pytest.fixture(autouse=True)
def mock_redis_enqueue(monkeypatch):
    async def noop(*_args, **_kwargs):
        return None

    monkeypatch.setattr("app.routers.inference.enqueue_inference_job", noop)
    monkeypatch.setattr("app.routers.inference.enqueue_batch_jobs", noop)


async def _token(client: AsyncClient, role: str = "comms_manager") -> str:
    login = await client.post(
        "/auth/dev-login",
        params={"email": f"inf-{role}@test.com", "role": role},
    )
    return login.json()["token"]


@pytest.mark.asyncio
async def test_submit_and_process_job(client: AsyncClient) -> None:
    token = await _token(client)
    headers = {"Authorization": f"Bearer {token}"}

    submit = await client.post(
        "/inference/jobs",
        json={"modality": "text", "payload": {"text": "Hello world"}},
        headers=headers,
    )
    assert submit.status_code == 202
    job = submit.json()
    assert job["status"] == "queued"
    job_id = job["id"]

    await run_inference_job_by_id(uuid.UUID(job_id))

    poll = await client.get(f"/inference/jobs/{job_id}", headers=headers)
    assert poll.status_code == 200
    body = poll.json()
    assert body["status"] == "completed"
    assert body["latency_ms"] is not None
    assert body["cost_usd"] is not None
    assert body["sla_met"] is True
    assert body["provider"] == "mock-gpu"


@pytest.mark.asyncio
async def test_cache_hit_on_duplicate_payload(client: AsyncClient) -> None:
    token = await _token(client)
    headers = {"Authorization": f"Bearer {token}"}
    payload = {"modality": "text", "payload": {"text": "Cache me"}}

    first = await client.post("/inference/jobs", json=payload, headers=headers)
    job_id = first.json()["id"]
    await run_inference_job_by_id(uuid.UUID(job_id))

    second = await client.post("/inference/jobs", json=payload, headers=headers)
    assert second.status_code == 202
    assert second.json()["status"] == "cached"
    assert second.json()["cost_usd"] == 0.0


@pytest.mark.asyncio
async def test_batch_submit(client: AsyncClient) -> None:
    token = await _token(client)
    headers = {"Authorization": f"Bearer {token}"}

    batch = await client.post(
        "/inference/batches",
        json={
            "modality": "text",
            "items": [{"text": "a"}, {"text": "b"}],
        },
        headers=headers,
    )
    assert batch.status_code == 202
    body = batch.json()
    assert body["total_jobs"] == 2
    assert len(body["job_ids"]) == 2

    for jid in body["job_ids"]:
        await run_inference_job_by_id(uuid.UUID(jid))

    poll = await client.get(f"/inference/batches/{body['id']}", headers=headers)
    assert poll.json()["completed_jobs"] == 2


@pytest.mark.asyncio
async def test_metrics_endpoint(client: AsyncClient) -> None:
    token = await _token(client, "security")
    headers = {"Authorization": f"Bearer {token}"}

    metrics = await client.get("/inference/metrics", headers=headers)
    assert metrics.status_code == 200
    body = metrics.json()
    assert "monthly_spend_usd" in body
    assert "monthly_cap_usd" in body


@pytest.mark.asyncio
async def test_cost_cap_rejects_job(client: AsyncClient, monkeypatch) -> None:
    monkeypatch.setattr("app.config.settings.inference_monthly_cost_cap_usd", 0.003)
    monkeypatch.setattr("app.services.inference_service.settings.inference_monthly_cost_cap_usd", 0.003)

    token = await _token(client)
    headers = {"Authorization": f"Bearer {token}"}

    first = await client.post(
        "/inference/jobs",
        json={"modality": "text", "payload": {"text": "cap test 1"}},
        headers=headers,
    )
    assert first.status_code == 202
    await run_inference_job_by_id(uuid.UUID(first.json()["id"]))

    blocked = await client.post(
        "/inference/jobs",
        json={"modality": "text", "payload": {"text": "cap test 2"}},
        headers=headers,
    )
    assert blocked.status_code == 402
