"""Inference job types."""

from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class Modality(str, Enum):
    TEXT = "text"
    MULTIMODAL = "multimodal"


class JobStatus(str, Enum):
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CACHED = "cached"


class InferenceRequest(BaseModel):
    modality: Modality
    payload: dict[str, Any] = Field(default_factory=dict)
    model_id: str = "tribe-v2-stub"


class InferenceResult(BaseModel):
    output: dict[str, Any]
    latency_ms: int
    cost_usd: float
    provider: str
    model_id: str
