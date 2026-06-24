"""Inference cost estimation and cap checks."""

from resonode_core.inference.types import Modality

# Pilot pricing estimates (USD) — replaced by provider-reported cost in production
ESTIMATED_COST_USD: dict[Modality, float] = {
    Modality.TEXT: 0.002,
    Modality.MULTIMODAL: 0.05,
}


def estimate_cost(modality: Modality) -> float:
    return ESTIMATED_COST_USD[modality]


def would_exceed_cap(current_spend: float, additional: float, cap: float) -> bool:
    if cap <= 0:
        return False
    return (current_spend + additional) > cap
