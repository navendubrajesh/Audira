"""Tests for audience library and analysis (TCA-001, TCA-008)."""

import pytest

DEV_HEADERS = {"Authorization": "Bearer dev:comms@example.com:comms_manager"}


@pytest.mark.asyncio
async def test_list_audiences_seeded(client):
    response = await client.get("/audiences", headers=DEV_HEADERS)
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 5
    assert any(a["name"] == "All employees" for a in data)


@pytest.mark.asyncio
async def test_analyze_text(client):
    response = await client.post(
        "/analyze",
        headers=DEV_HEADERS,
        json={
            "text": "Thank you for your commitment. We appreciate your support as we drive action together.",
            "objective": "engage",
            "channel": "email",
            "artifact_type_code": "email",
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert body["composite_score"] is not None
    assert body["composite_score"] > 0
    assert "metrics" in body["result"]
    assert "readability" in body["result"]["metrics"]
    assert "rewrite_suggestions" in body["result"]


@pytest.mark.asyncio
async def test_engineering_artifact_blocked(client):
    response = await client.post(
        "/analyze",
        headers=DEV_HEADERS,
        json={
            "text": "API spec section 3.1",
            "artifact_type_code": "engineering_spec",
        },
    )
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_governance_models(client):
    response = await client.get("/governance/models", headers=DEV_HEADERS)
    assert response.status_code == 200
    models = response.json()
    assert any(m["model_id"] == "facebook/tribev2" for m in models)


@pytest.mark.asyncio
async def test_mapping_module():
    import sys
    from pathlib import Path

    shared = Path(__file__).resolve().parents[2] / "shared"
    if str(shared) not in sys.path:
        sys.path.insert(0, str(shared))
    from audira_core.mapping.metrics import map_tribe_output

    out = map_tribe_output(
        {"metrics_stub": {"attention": 80, "clarity": 75}, "model_id": "tribe-v2-stub"},
        audience_attributes={"seniority": "executive"},
        objective="drive_action",
        channel="email",
    )
    assert out["engagement"] > 0
    assert out["mapping_version"] == "1.0.0"
