"""
TRIBE v2 inference engine — wraps facebook/tribev2 from Hugging Face.

Requires GPU, HuggingFace token (LLaMA 3.2 is gated), and:
  pip install git+https://github.com/facebookresearch/tribev2.git  # or tribev2 package

Model card: https://huggingface.co/facebook/tribev2
License: CC-BY-NC-4.0 (non-commercial — see PRD Section 13)
"""

from __future__ import annotations

import os
import tempfile
import time
from typing import Any

_model = None
TRIBE_MODEL_ID = "facebook/tribev2"


def _ensure_hf_auth() -> None:
    try:
        from audira_core.huggingface import ensure_hf_login

        ensure_hf_login()
    except ImportError:
        token = (
            os.environ.get("HF_TOKEN")
            or os.environ.get("HUGGINGFACE_HUB_TOKEN")
            or os.environ.get("HUGGING_FACE_HUB_TOKEN")
            or ""
        ).strip()
        if not token:
            raise RuntimeError(
                "HF_TOKEN is not set. Add a Hugging Face Read token to download "
                f"{TRIBE_MODEL_ID} and its gated LLaMA 3.2 dependency."
            ) from None
        os.environ["HF_TOKEN"] = token
        os.environ["HUGGINGFACE_HUB_TOKEN"] = token


def _get_model():
    global _model
    if _model is None:
        from tribev2 import TribeModel

        _ensure_hf_auth()
        cache = os.environ.get("TRIBE_CACHE_DIR", "/cache/tribev2")
        _model = TribeModel.from_pretrained(TRIBE_MODEL_ID, cache_folder=cache)
    return _model


def _write_temp_text(text: str) -> str:
    fd, path = tempfile.mkstemp(suffix=".txt", prefix="audira_tribe_")
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        f.write(text)
    return path


def run_tribe_inference(modality: str, payload: dict[str, Any]) -> dict[str, Any]:
    """Run TRIBE v2 and return raw output + metadata for the mapping layer (TCA-015)."""
    model = _get_model()
    started = time.perf_counter()

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
            df = model.get_events_dataframe(video_path=video_path)
        elif audio_path:
            df = model.get_events_dataframe(audio_path=audio_path)
        elif text_path:
            df = model.get_events_dataframe(text_path=text_path)
        else:
            raise ValueError("TRIBE v2 requires text, video_path, audio_path, or text_path in payload")

        preds, segments = model.predict(events=df)
        latency_ms = int((time.perf_counter() - started) * 1000)

        return {
            "output": {
                "model": TRIBE_MODEL_ID,
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
            "provider": "tribe-v2-gpu",
            "model_id": TRIBE_MODEL_ID,
        }
    finally:
        if temp_path and os.path.exists(temp_path):
            os.unlink(temp_path)
