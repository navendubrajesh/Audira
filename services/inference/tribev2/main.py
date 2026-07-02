"""TRIBE v2 GPU inference HTTP service — decoupled tier for Audira.run."""

import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from engine import TRIBE_MODEL_ID

API_KEY = os.environ.get("INFERENCE_API_KEY", "")


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        from audira_core.huggingface import ensure_hf_login

        ensure_hf_login()
    except Exception as exc:
        # Model load is lazy; startup only primes HF auth when token is present.
        if os.environ.get("TRIBE_ALLOW_STUB", "0") != "1":
            print(f"[startup] Hugging Face auth not ready: {exc}")
    yield


app = FastAPI(
    title="Audira.run TRIBE v2 Inference",
    description=f"GPU service wrapping {TRIBE_MODEL_ID} — https://huggingface.co/{TRIBE_MODEL_ID}",
    version="0.1.0",
    lifespan=lifespan,
)


class InferenceBody(BaseModel):
    modality: str = "text"
    payload: dict = Field(default_factory=dict)
    model_id: str = TRIBE_MODEL_ID


@app.get("/health")
async def health():
    from audira_core.huggingface import resolve_hf_token

    return {
        "status": "ok",
        "model": TRIBE_MODEL_ID,
        "tier": "gpu",
        "huggingface_token_configured": bool(resolve_hf_token()),
    }


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
