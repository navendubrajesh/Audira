"""Smoke tests for Phase 0 bootstrap."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_health_ok(client: AsyncClient) -> None:
    response = await client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


@pytest.mark.asyncio
async def test_inference_health_reports_hf_config(client: AsyncClient, monkeypatch) -> None:
    monkeypatch.setattr("app.config.settings.hf_token", "test-token")
    monkeypatch.setattr(
        "app.routers.health.verify_hf_token",
        lambda token: {"ok": True, "name": "demo"},
    )
    response = await client.get("/health/inference")
    assert response.status_code == 200
    body = response.json()
    assert body["model_id"] == "facebook/tribev2"
    assert body["huggingface_token_configured"] is True
    assert body["huggingface_token_valid"] is True
    assert body["huggingface_user"] == "demo"
