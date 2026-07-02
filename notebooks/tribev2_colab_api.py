# %% [markdown]
# # Audira TRIBE v2 Temporary Colab API
#
# Development/demo only. Starts a FastAPI service compatible with Audira's
# `/v1/inference` contract and exposes it through a temporary Cloudflare Tunnel.
#
# **Before you run:** Colab sidebar (key icon) → Secrets → add `HF_TOKEN` (Read
# token from Hugging Face) and optionally `INFERENCE_API_KEY` (shared with Render).
# Enable notebook access for each secret.

# %% [markdown]
# ## 1. Configure secrets (Colab Secrets)
#
# | Secret name | Required | Purpose |
# |---|---|---|
# | `HF_TOKEN` | Yes | Hugging Face Read token — accept [facebook/tribev2](https://huggingface.co/facebook/tribev2) licenses first |
# | `INFERENCE_API_KEY` | Optional | Shared secret for Render; defaults to demo value below if unset |

# %%
import os

TRIBE_ALLOW_STUB = "0"  # "0" = real TRIBE v2; "1" = stub (tunnel test only, no HF token)


def _colab_secret(name: str) -> str | None:
    """Read a Colab Secret, printing why it failed if it isn't available."""
    try:
        from google.colab import userdata  # type: ignore
    except Exception:
        return None  # not running in Colab

    try:
        value = userdata.get(name)
        return value.strip() if value else None
    except userdata.SecretNotFoundError:
        print(f"[secret] '{name}' not found. Add it via the key icon in the sidebar.")
    except userdata.NotebookAccessError:
        print(f"[secret] '{name}' exists but notebook access is off. Toggle it on for this notebook.")
    except Exception as exc:
        print(f"[secret] could not read '{name}': {exc}")
    return None


def _resolve_hf_token() -> str:
    token = _colab_secret("HF_TOKEN")
    if token:
        return token
    if TRIBE_ALLOW_STUB == "1":
        return ""
    # Fallback: prompt securely so a missing/blocked secret doesn't hard-block you.
    import getpass

    print(
        "HF_TOKEN Colab Secret not available. Recommended: add it via the key icon "
        "(name it HF_TOKEN, enable notebook access). For now you can paste it below."
    )
    return getpass.getpass("Paste Hugging Face token (hidden, blank to abort): ").strip()


HF_TOKEN = _resolve_hf_token()
INFERENCE_API_KEY = _colab_secret("INFERENCE_API_KEY") or "audira-colab-demo-secret"

if TRIBE_ALLOW_STUB != "1" and not HF_TOKEN:
    raise RuntimeError(
        "No Hugging Face token provided. Add a Colab Secret named HF_TOKEN "
        "(key icon in the sidebar) with notebook access enabled, or paste it when "
        "prompted. Accept gated licenses on huggingface.co/facebook/tribev2 first. "
        "To skip TRIBE v2 entirely and just test the tunnel, set TRIBE_ALLOW_STUB = \"1\"."
    )

if HF_TOKEN:
    os.environ["HF_TOKEN"] = HF_TOKEN
else:
    os.environ.pop("HF_TOKEN", None)

os.environ["INFERENCE_API_KEY"] = INFERENCE_API_KEY
os.environ["TRIBE_ALLOW_STUB"] = TRIBE_ALLOW_STUB
os.environ["TRIBE_CACHE_DIR"] = "/content/tribev2-cache"

print("HF_TOKEN loaded:", "yes" if HF_TOKEN else "no (stub mode)")
print("INFERENCE_API_KEY set:", INFERENCE_API_KEY[:4] + "…" if len(INFERENCE_API_KEY) > 4 else INFERENCE_API_KEY)
print("TRIBE_ALLOW_STUB:", TRIBE_ALLOW_STUB)

# %% [markdown]
# ## 2. Install dependencies

# %%
!pip -q install fastapi "uvicorn[standard]" httpx pydantic requests huggingface_hub

# Real TRIBE v2 (GPU runtime required). First run downloads large weights.
!pip -q install git+https://github.com/facebookresearch/tribev2.git

# %% [markdown]
# ## 3. Write the Audira-compatible FastAPI app

# %%
from pathlib import Path

_APP_SOURCE = r'''from __future__ import annotations

import os
import tempfile
import time
from typing import Any

from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel, Field

app = FastAPI(title="Audira.run TRIBE v2 Colab API", version="0.1.0")

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
            from tribev2 import TribeModel
        except ImportError as exc:
            if ALLOW_STUB:
                return None
            raise RuntimeError(
                "tribev2 is not installed. Install it or set TRIBE_ALLOW_STUB=1."
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

    temp_path = None
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
    return {"status": "ok", "model": "facebook/tribev2", "tier": "colab-gpu", "stub": ALLOW_STUB}


@app.post("/v1/inference")
async def inference(body: InferenceBody, authorization: str | None = Header(default=None)):
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
'''

Path("/content/colab_api.py").write_text(_APP_SOURCE)
print("Wrote /content/colab_api.py")

# %% [markdown]
# ## 4. Start the API server

# %%
import subprocess
import time

# Stop any previous demo processes from earlier runs.
subprocess.run(["pkill", "-f", "uvicorn colab_api"], check=False)
time.sleep(1)

_server_env = os.environ.copy()
server = subprocess.Popen(
    ["python", "-m", "uvicorn", "colab_api:app", "--host", "0.0.0.0", "--port", "8001"],
    cwd="/content",
    env=_server_env,
)
time.sleep(3)
print("API running on http://127.0.0.1:8001")

# %% [markdown]
# ## 5. Start Cloudflare Tunnel
#
# Copy `AUDIRA INFERENCE_BASE_URL`. On Render API set:
#
# - `INFERENCE_BASE_URL=<tunnel URL>`
# - `INFERENCE_API_KEY=<same as Colab secret or default above>`

# %%
!wget -q https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64 -O /content/cloudflared
!chmod +x /content/cloudflared

import re
import threading

subprocess.run(["pkill", "cloudflared"], check=False)
time.sleep(1)

tunnel = subprocess.Popen(
    ["/content/cloudflared", "tunnel", "--url", "http://127.0.0.1:8001", "--no-autoupdate"],
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
    text=True,
)

public_url = None
_URL_RE = re.compile(r"https://[-a-z0-9]+\.trycloudflare\.com")


def watch_tunnel():
    global public_url
    for line in tunnel.stdout:
        print(line, end="")
        match = _URL_RE.search(line)
        if match and not public_url:
            public_url = match.group(0)
            print("\nAUDIRA INFERENCE_BASE_URL =", public_url)
            print("Render INFERENCE_API_KEY =", INFERENCE_API_KEY)


threading.Thread(target=watch_tunnel, daemon=True).start()

for _ in range(60):
    if public_url:
        break
    time.sleep(1)

if public_url:
    print("\nCurrent tunnel URL:", public_url)
else:
    print("\nTunnel URL not ready yet. Wait a few seconds and re-run this cell.")

# %% [markdown]
# ## 6. Test the temporary API

# %%
import requests

for _ in range(30):
    if public_url:
        break
    time.sleep(1)

assert public_url, "Tunnel URL still not ready. Re-run the Cloudflare Tunnel cell above."

# 1) Confirm the local server is up (isolates server vs tunnel problems).
local = requests.get("http://127.0.0.1:8001/health", timeout=10)
print("Local health:", local.status_code, local.json())

# 2) Wait for the public tunnel hostname to resolve. A brand-new
#    *.trycloudflare.com name can take 10-40s to become resolvable, which shows
#    up as "Name or service not known" / ConnectionError if you call it too soon.
def wait_for_tunnel(url: str, attempts: int = 30, delay: int = 3) -> bool:
    for i in range(1, attempts + 1):
        try:
            r = requests.get(f"{url}/health", timeout=10)
            if r.ok:
                print(f"Tunnel reachable after {i} attempt(s):", r.json())
                return True
            print(f"[{i}] tunnel returned HTTP {r.status_code}, retrying…")
        except requests.exceptions.RequestException:
            print(f"[{i}] tunnel not resolvable yet, waiting {delay}s…")
        time.sleep(delay)
    return False


if not wait_for_tunnel(public_url):
    raise RuntimeError(
        "Tunnel URL is not reachable yet. The local server works, so this is DNS "
        "propagation or a dropped tunnel. Re-run the Cloudflare Tunnel cell to get "
        "a fresh URL, then re-run this cell."
    )

# 3) Real inference (first call is slow while TRIBE v2 loads into GPU memory).
response = requests.post(
    f"{public_url}/v1/inference",
    headers={"Authorization": f"Bearer {INFERENCE_API_KEY}"},
    json={
        "modality": "text",
        "model_id": "facebook/tribev2",
        "payload": {"text": "Hello from Audira Colab demo."},
    },
    timeout=600,
)
print("Inference:", response.status_code)
print(response.json())
