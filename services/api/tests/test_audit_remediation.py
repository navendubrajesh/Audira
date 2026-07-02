"""Tests for audit remediation (2026-06-24)."""

import pytest

DEV_HEADERS = {"Authorization": "Bearer dev:comms@example.com:comms_manager"}
ADMIN_HEADERS = {"Authorization": "Bearer dev:admin@example.com:admin"}


@pytest.mark.asyncio
async def test_guardrail_check_endpoints(client):
    resp = await client.post(
        "/guardrails/check/generative",
        headers=DEV_HEADERS,
        json={"text": "As an AI language model I cannot verify this 99% growth guarantee."},
    )
    assert resp.status_code == 200
    assert resp.json()["action"] in ("warn", "block", "pass")


@pytest.mark.asyncio
async def test_guardrail_settings(client):
    resp = await client.get("/guardrails/settings", headers=DEV_HEADERS)
    assert resp.status_code == 200
    assert resp.json()["generative_governance"] is False


@pytest.mark.asyncio
async def test_extended_metrics_in_analysis(client):
    resp = await client.post(
        "/analyze",
        headers=DEV_HEADERS,
        json={"text": "Team update: we support you through this change.", "fast_lane": True},
    )
    assert resp.status_code == 200
    metrics = resp.json()["result"]["metrics"]
    assert "emotion" in metrics
    assert "cognitive_load" in metrics
    assert "explainability" in resp.json()["result"]


@pytest.mark.asyncio
async def test_consistency_check(client):
    resp = await client.post(
        "/features/consistency/check",
        headers=DEV_HEADERS,
        json={
            "documents": [
                "All employees must complete training.",
                "All employees must complete training by Friday.",
            ]
        },
    )
    assert resp.status_code == 200
    assert resp.json()["document_count"] == 2


@pytest.mark.asyncio
async def test_seeded_standards(client):
    resp = await client.get("/context/standards", headers=DEV_HEADERS)
    assert resp.status_code == 200
    assert len(resp.json()) >= 1


@pytest.mark.asyncio
async def test_compare_metric_diffs(client):
    resp = await client.post(
        "/analyze/compare",
        headers=DEV_HEADERS,
        json={
            "variant_a": "Clear update for team members.",
            "variant_b": "We synergize paradigms across stakeholders.",
        },
    )
    assert resp.status_code == 200
    assert "metric_diffs" in resp.json()


@pytest.mark.asyncio
async def test_api_key_creation(client):
    resp = await client.post(
        "/features/api-keys",
        headers=ADMIN_HEADERS,
        json={"name": "test-integration"},
    )
    assert resp.status_code == 200
    assert resp.json()["api_key"].startswith("aud_")
