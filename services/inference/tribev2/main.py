"""TRIBE v2 GPU inference HTTP service — decoupled tier for Audira.run."""

import os

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

app = FastAPI(
    title="Audira.run TRIBE v2 Inference",
    description="GPU service wrapping facebook/tribev2 — https://huggingface.co/facebook/tribev2",
    version="0.1.0",
)

API_KEY = os.environ.get("INFERENCE_API_KEY", "")


class InferenceBody(BaseModel):
    modality: str = "text"
    payload: dict = Field(default_factory=dict)
    model_id: str = "facebook/tribev2"


@app.get("/health")
async def health():
    return {"status": "ok", "model": "facebook/tribev2", "tier": "gpu"}


@app.post("/v1/inference")
async def inference(body: InferenceBody, authorization: str | None = None):
    if API_KEY:
        token = (authorization or "").removeprefix("Bearer ").strip()
        if token != API_KEY:
            raise HTTPException(status_code=401, detail="Unauthorized")

    try:
        from engine import run_tribe_inference

        result = run_tribe_inference(body.modality, body.payload)
        return {
            "output": result["output"],
            "cost_usd": result["cost_usd"],
            "provider": result["provider"],
            "model_id": result["model_id"],
            "latency_ms": result["latency_ms"],
        }
    except ImportError as exc:
        raise HTTPException(
            status_code=503,
            detail="tribev2 package not installed on this GPU image",
        ) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)[:500]) from exc
