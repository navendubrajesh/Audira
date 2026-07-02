"""Health and bootstrap routes."""

from fastapi import APIRouter

from app.config import settings
from audira_core.huggingface import resolve_hf_token, verify_hf_token

router = APIRouter(tags=["health"])


@router.get("/health")
async def health() -> dict:
    return {"status": "ok", "service": "audira-api"}


@router.get("/health/inference")
async def inference_health() -> dict:
    """Check TRIBE v2 / Hugging Face configuration (no secrets returned)."""
    token = resolve_hf_token(settings.hf_token) or None
    hf_check = verify_hf_token(token) if token else None
    return {
        "model_id": "facebook/tribev2",
        "inference_tier_configured": bool(settings.inference_base_url),
        "huggingface_token_configured": bool(token),
        "huggingface_token_valid": hf_check.get("ok") if hf_check else None,
        "huggingface_user": hf_check.get("name") if hf_check and hf_check.get("ok") else None,
        "note": (
            "TRIBE v2 runs on the GPU tier (Colab/RunPod). Set HF_TOKEN on that host "
            "to download facebook/tribev2. A free Hugging Face Read token works."
        ),
    }
