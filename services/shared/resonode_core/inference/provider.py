"""Inference provider abstraction — GPU tier is always external."""

from typing import Protocol

from resonode_core.inference.types import InferenceRequest, InferenceResult


class InferenceProvider(Protocol):
    name: str

    async def run(self, request: InferenceRequest) -> InferenceResult: ...


class MockGpuProvider:
    """Simulates decoupled GPU tier latency and cost (development / tests)."""

    name = "mock-gpu"

    def __init__(self, model_label: str = "mock-gpu") -> None:
        self.model_label = model_label

    async def run(self, request: InferenceRequest) -> InferenceResult:
        import asyncio
        import time

        from resonode_core.cost import estimate_cost
        from resonode_core.inference.types import Modality

        delay = 0.05 if request.modality == Modality.TEXT else 0.2
        await asyncio.sleep(delay)

        started = time.perf_counter()
        latency_ms = int((time.perf_counter() - started) * 1000) + int(delay * 1000)

        return InferenceResult(
            output={
                "status": "ok",
                "modality": request.modality.value,
                "model_id": request.model_id,
                "model": self.model_label,
                "license": "CC-BY-NC-4.0 (stub — connect GPU tier for real inference)",
                "metrics_stub": {"attention": 72, "clarity": 68},
                "raw_fmri_vertices": 10242,
            },
            latency_ms=max(latency_ms, int(delay * 1000)),
            cost_usd=estimate_cost(request.modality),
            provider=self.name,
            model_id=request.model_id,
        )


class HttpGpuProvider:
    """Calls Modal / Replicate / Baseten via HTTP."""

    name = "http-gpu"

    def __init__(self, base_url: str, api_key: str = "") -> None:
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key

    async def run(self, request: InferenceRequest) -> InferenceResult:
        import time

        import httpx

        from resonode_core.cost import estimate_cost

        headers = {"Authorization": f"Bearer {self.api_key}"} if self.api_key else {}
        started = time.perf_counter()
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(
                f"{self.base_url}/v1/inference",
                json=request.model_dump(),
                headers=headers,
            )
            response.raise_for_status()
            data = response.json()

        latency_ms = int((time.perf_counter() - started) * 1000)
        return InferenceResult(
            output=data.get("output", data),
            latency_ms=latency_ms,
            cost_usd=float(data.get("cost_usd", estimate_cost(request.modality))),
            provider=self.name,
            model_id=request.model_id,
        )
