"""Hugging Face token helpers — works with free-tier Read tokens and paid plans."""

from __future__ import annotations

import os
from typing import Any

HF_TOKEN_ENV_NAMES = ("HF_TOKEN", "HUGGINGFACE_HUB_TOKEN", "HUGGING_FACE_HUB_TOKEN")


def resolve_hf_token(explicit: str | None = None) -> str | None:
    """Return the first available HF token (explicit arg, then env vars)."""
    if explicit and explicit.strip():
        return explicit.strip()
    for name in HF_TOKEN_ENV_NAMES:
        value = os.environ.get(name, "").strip()
        if value:
            return value
    return None


def apply_hf_token_env(token: str) -> None:
    """Mirror the token into env vars used by huggingface_hub and tribev2."""
    for name in HF_TOKEN_ENV_NAMES:
        os.environ[name] = token


def ensure_hf_login(explicit: str | None = None) -> str:
    """Configure Hugging Face auth for gated models (e.g. LLaMA 3.2 for TRIBE v2).

    Returns the token used. Raises RuntimeError when no token is available.
    """
    token = resolve_hf_token(explicit)
    if not token:
        raise RuntimeError(
            "HF_TOKEN is not set. Add a Hugging Face Read token to your environment "
            "(free tier works). Accept gated licenses at "
            "https://huggingface.co/facebook/tribev2 first."
        )

    apply_hf_token_env(token)

    try:
        from huggingface_hub import login

        login(token=token, add_to_git_credential=False)
    except ImportError:
        pass

    return token


def verify_hf_token(token: str) -> dict[str, Any]:
    """Validate a token against the Hugging Face API (no token echoed back)."""
    import httpx

    try:
        response = httpx.get(
            "https://huggingface.co/api/whoami-v2",
            headers={"Authorization": f"Bearer {token}"},
            timeout=15.0,
        )
        if response.status_code == 200:
            data = response.json()
            return {
                "ok": True,
                "name": data.get("name") or data.get("fullname"),
                "type": data.get("type"),
            }
        return {"ok": False, "error": f"HTTP {response.status_code}"}
    except Exception as exc:
        return {"ok": False, "error": str(exc)[:200]}
