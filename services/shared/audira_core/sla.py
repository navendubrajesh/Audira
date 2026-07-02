"""SLA targets per NFR-01."""

from audira_core.inference.types import Modality

SLA_TARGETS_MS: dict[Modality, int] = {
    Modality.TEXT: 2_000,
    Modality.MULTIMODAL: 60_000,
}


def check_sla(modality: Modality, latency_ms: int) -> bool:
    return latency_ms <= SLA_TARGETS_MS[modality]


def sla_target_ms(modality: Modality) -> int:
    return SLA_TARGETS_MS[modality]
