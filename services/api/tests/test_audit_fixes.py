"""Extended analysis tests after audit fixes."""

import pytest

DEV_HEADERS = {"Authorization": "Bearer dev:comms@example.com:comms_manager"}


@pytest.mark.asyncio
async def test_fast_lane_analysis(client):
    response = await client.post(
        "/analyze",
        headers=DEV_HEADERS,
        json={
            "text": "Thank you team members for your support. We ensure clarity in every update.",
            "objective": "inform",
            "artifact_type_code": "email",
            "fast_lane": True,
            "full_analysis": False,
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert body["result"]["inference"]["skipped"] is True
    assert "verdict" in body["result"]
    assert "structure" in body["result"]["metrics"]


@pytest.mark.asyncio
async def test_compare_variants(client):
    response = await client.post(
        "/analyze/compare",
        headers=DEV_HEADERS,
        json={
            "variant_a": "Short clear update for all team members.",
            "variant_b": "We synergize paradigms to leverage bandwidth across stakeholders.",
            "objective": "inform",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["winner"] in ("a", "b")
    assert data["delta"] >= 0


@pytest.mark.asyncio
async def test_quality_gates(client):
    response = await client.get("/context/quality-gates", headers=DEV_HEADERS)
    assert response.status_code == 200
    assert "pass_threshold" in response.json()


@pytest.mark.asyncio
async def test_analytics_dashboard_real(client):
    await client.post(
        "/analyze",
        headers=DEV_HEADERS,
        json={"text": "Hello team.", "fast_lane": True},
    )
    dash = await client.get("/features/analytics/dashboard", headers=DEV_HEADERS)
    assert dash.status_code == 200
    assert dash.json()["analyses_count"] >= 1


@pytest.mark.asyncio
async def test_pii_detection():
    from app.services.scoring.pii import detect_pii, redact_pii

    text = "Contact us at user@example.com or 555-123-4567."
    findings = detect_pii(text)
    assert len(findings) >= 1
    redacted, _ = redact_pii(text)
    assert "example.com" not in redacted


@pytest.mark.asyncio
async def test_heatmap():
    from app.services.heatmap import generate_attention_heatmap

    hm = generate_attention_heatmap("First sentence matters. Second adds detail.")
    assert len(hm["grid"]) > 0
    assert hm["export_svg"].startswith("<svg")
