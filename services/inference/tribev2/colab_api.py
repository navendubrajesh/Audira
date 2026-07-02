"""Colab temporary TRIBE v2 API for demos.

Run this in Google Colab (GPU runtime) and expose it with a temporary tunnel
such as Cloudflare Tunnel. Render can then point INFERENCE_BASE_URL at that
tunnel URL during development/demo.

This intentionally mirrors services/inference/tribev2/main.py:
  GET  /health
  POST /v1/inference
"""

from __future__ import annotations

import os
import tempfile
import time
from typing import Any

from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel, Field

app = FastAPI(
    title="Audira.run TRIBE v2 Colab API",
    description="Temporary Colab-hosted API for development and demos only.",
    version="0.1.0",
)

API_KEY = os.environ.get("INFERENCE_API_KEY", "")
TRIBE_CACHE_DIR = os.environ.get("TRIBE_CACHE_DIR", "/content/tribev2-cache")
ALLOW_STUB = os.environ.get("TRIBE_ALLOW_STUB", "0") == "1"

_model = None


class InferenceBody(BaseModel):
    modality: str = "text"
    payload: dict[str, Any] = Field(default_factory=dict)
    model_id: str = "facebook/tribev2"


def _get_model():
    global _model
    if _model is None:
        try:
            from audira_core.huggingface import ensure_hf_login

            ensure_hf_login()
        except ImportError:
            token = os.environ.get("HF_TOKEN", "").strip()
            if not token and not ALLOW_STUB:
                raise RuntimeError(
                    "HF_TOKEN is not set. Add a Hugging Face Read token (free tier works)."
                ) from None
            if token:
                os.environ["HF_TOKEN"] = token
                os.environ["HUGGINGFACE_HUB_TOKEN"] = token

        try:
            from tribev2 import TribeModel
        except ImportError as exc:
            if ALLOW_STUB:
                return None
            raise RuntimeError(
                "tribev2 is not installed. Install it in Colab or set "
                "TRIBE_ALLOW_STUB=1 to test the HTTP tunnel without real TRIBE v2."
            ) from exc

        _model = TribeModel.from_pretrained("facebook/tribev2", cache_folder=TRIBE_CACHE_DIR)
    return _model


def _write_temp_text(text: str) -> str:
    fd, path = tempfile.mkstemp(suffix=".txt", prefix="audira_tribe_")
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        f.write(text)
    return path


def _stub_result(modality: str, started: float) -> dict[str, Any]:
    latency_ms = int((time.perf_counter() - started) * 1000)
    return {
        "output": {
            "status": "ok",
            "model": "facebook/tribev2",
            "license": "CC-BY-NC-4.0 (stub mode)",
            "modality": modality,
            "raw_fmri_shape": [8, 10242],
            "n_vertices": 10242,
            "n_timesteps": 8,
            "segments_count": 1,
            "mesh": "fsaverage5",
            "metrics_stub": {"attention": 72, "clarity": 68},
        },
        "latency_ms": max(latency_ms, 50),
        "cost_usd": 0.0,
        "provider": "colab-tribev2-stub",
        "model_id": "facebook/tribev2",
    }


def run_tribe_inference(modality: str, payload: dict[str, Any]) -> dict[str, Any]:
    started = time.perf_counter()
    model = _get_model()
    if model is None:
        return _stub_result(modality, started)

    text_path = payload.get("text_path")
    video_path = payload.get("video_path")
    audio_path = payload.get("audio_path")
    text = payload.get("text")

    temp_path: str | None = None
    if text and not text_path:
        temp_path = _write_temp_text(text)
        text_path = temp_path

    try:
        if video_path:
            events = model.get_events_dataframe(video_path=video_path)
        elif audio_path:
            events = model.get_events_dataframe(audio_path=audio_path)
        elif text_path:
            events = model.get_events_dataframe(text_path=text_path)
        else:
            raise ValueError("TRIBE v2 requires text, video_path, audio_path, or text_path")

        preds, segments = model.predict(events=events)
        latency_ms = int((time.perf_counter() - started) * 1000)
        return {
            "output": {
                "model": "facebook/tribev2",
                "license": "CC-BY-NC-4.0",
                "modality": modality,
                "raw_fmri_shape": list(preds.shape),
                "n_vertices": int(preds.shape[1]) if len(preds.shape) > 1 else 0,
                "n_timesteps": int(preds.shape[0]) if len(preds.shape) > 0 else 0,
                "segments_count": len(segments) if segments is not None else 0,
                "mesh": "fsaverage5",
            },
            "latency_ms": latency_ms,
            "cost_usd": float(os.environ.get("TRIBE_COST_USD_ESTIMATE", "0.08")),
            "provider": "colab-tribev2-gpu",
            "model_id": "facebook/tribev2",
        }
    finally:
        if temp_path and os.path.exists(temp_path):
            os.unlink(temp_path)


@app.get("/health")
async def health():
    return {
        "status": "ok",
        "model": "facebook/tribev2",
        "tier": "colab-gpu",
        "stub": ALLOW_STUB,
    }


@app.post("/v1/inference")
async def inference(
    body: InferenceBody,
    authorization: str | None = Header(default=None),
):
    if API_KEY:
        token = (authorization or "").removeprefix("Bearer ").strip()
        if token != API_KEY:
            raise HTTPException(status_code=401, detail="Unauthorized")

    try:
        result = run_tribe_inference(body.modality, body.payload)
        return {
            "output": result["output"],
            "cost_usd": result["cost_usd"],
            "provider": result["provider"],
            "model_id": result["model_id"],
            "latency_ms": result["latency_ms"],
        }
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)[:500]) from exc


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", "8001")))
