"""Map TRIBE v2 raw outputs to communications effectiveness metrics (TCA-015)."""

from __future__ import annotations

MAPPING_VERSION = "1.0.0"


def map_tribe_output(
    raw: dict,
    *,
    audience_attributes: dict | None = None,
    objective: str | None = None,
    channel: str | None = None,
) -> dict:
    """
    Translate neuro-model outputs into comms-facing scores (0–100).

    Accepts either pre-computed metrics_stub or vertex-level summaries from GPU tier.
    """
    attrs = audience_attributes or {}
    stub = raw.get("metrics_stub") or {}
    attention = float(stub.get("attention") or raw.get("attention_mean") or 65)
    clarity = float(stub.get("clarity") or raw.get("clarity_mean") or 62)
    trust = float(stub.get("trust") or attention * 0.92)
    action = float(stub.get("action_intent") or clarity * 0.88)

    # Audience / objective / channel calibration weights
    seniority = (attrs.get("seniority") or "").lower()
    if seniority in {"executive", "leadership", "c-suite"}:
        clarity *= 1.05
        action *= 0.95
    region = (attrs.get("region") or "").upper()
    if region in {"EU", "UK"}:
        trust *= 1.03
    if objective == "inform":
        action *= 0.9
    elif objective == "drive_action":
        action *= 1.08
    if channel in {"email", "intranet"}:
        clarity *= 1.02
    elif channel == "town_hall":
        attention *= 1.05

    def clamp(v: float) -> float:
        return round(max(0.0, min(100.0, v)), 1)

    engagement = clamp((attention * 0.55 + action * 0.45))
    clarity_score = clamp(clarity)
    trust_score = clamp(trust)
    action_intent = clamp(action)

    return {
        "mapping_version": MAPPING_VERSION,
        "engagement": engagement,
        "clarity": clarity_score,
        "trust": trust_score,
        "action_intent": action_intent,
        "attention_proxy": clamp(attention),
        "calibration": {
            "audience": attrs,
            "objective": objective,
            "channel": channel,
        },
        "source": {
            "model_id": raw.get("model_id") or raw.get("model"),
            "raw_vertices": raw.get("raw_fmri_vertices"),
        },
    }
