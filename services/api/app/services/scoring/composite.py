"""Composite effectiveness score (TCA-038, TCA-003)."""

from typing import Any

DEFAULT_WEIGHTS = {
    "readability": 0.15,
    "jargon": 0.10,
    "inclusive": 0.10,
    "brand": 0.15,
    "tone": 0.10,
    "structure": 0.05,
    "engagement": 0.15,
    "clarity": 0.10,
    "trust": 0.05,
    "action_intent": 0.05,
}

OBJECTIVE_WEIGHTS: dict[str, dict[str, float]] = {
    "inform": {
        **DEFAULT_WEIGHTS,
        "readability": 0.20,
        "clarity": 0.15,
        "action_intent": 0.02,
        "engagement": 0.10,
    },
    "engage": {
        **DEFAULT_WEIGHTS,
        "engagement": 0.25,
        "tone": 0.15,
        "action_intent": 0.05,
    },
    "drive_action": {
        **DEFAULT_WEIGHTS,
        "action_intent": 0.20,
        "engagement": 0.20,
        "clarity": 0.12,
    },
    "reassure": {
        **DEFAULT_WEIGHTS,
        "trust": 0.18,
        "tone": 0.15,
        "inclusive": 0.12,
    },
    "celebrate": {
        **DEFAULT_WEIGHTS,
        "tone": 0.18,
        "engagement": 0.22,
        "brand": 0.12,
    },
}

PASS_THRESHOLD = 70.0
NEEDS_WORK_THRESHOLD = 55.0


def weights_for_objective(objective: str | None) -> dict[str, float]:
    if objective and objective in OBJECTIVE_WEIGHTS:
        return OBJECTIVE_WEIGHTS[objective]
    return DEFAULT_WEIGHTS


def composite_score(
    metrics: dict[str, Any],
    *,
    objective: str | None = None,
    weights: dict[str, float] | None = None,
) -> float:
    w = weights or weights_for_objective(objective)
    total_w = 0.0
    acc = 0.0
    for key, weight in w.items():
        block = metrics.get(key)
        if isinstance(block, dict) and "score" in block:
            val = float(block["score"])
        elif isinstance(block, (int, float)):
            val = float(block)
        else:
            continue
        acc += val * weight
        total_w += weight
    if total_w == 0:
        return 0.0
    return round(acc / total_w, 1)


def quality_verdict(score: float, *, pass_threshold: float = PASS_THRESHOLD) -> dict:
    if score >= pass_threshold:
        label = "pass"
    elif score >= NEEDS_WORK_THRESHOLD:
        label = "needs_work"
    else:
        label = "fail"
    return {
        "label": label,
        "pass_threshold": pass_threshold,
        "needs_work_threshold": NEEDS_WORK_THRESHOLD,
    }
