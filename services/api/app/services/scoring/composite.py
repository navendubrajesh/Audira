"""Composite effectiveness score (TCA-038)."""

from typing import Any


DEFAULT_WEIGHTS = {
    "readability": 0.15,
    "jargon": 0.10,
    "inclusive": 0.10,
    "brand": 0.15,
    "tone": 0.10,
    "engagement": 0.20,
    "clarity": 0.10,
    "trust": 0.05,
    "action_intent": 0.05,
}


def composite_score(metrics: dict[str, Any], weights: dict[str, float] | None = None) -> float:
    w = weights or DEFAULT_WEIGHTS
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
