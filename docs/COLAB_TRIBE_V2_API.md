# Colab temporary TRIBE v2 API

Use this only for development/demo. Google Colab is not a stable production API host: runtimes sleep, URLs change, and GPU access is not guaranteed.

## Flow

```text
Audira Web -> Render API/worker -> INFERENCE_BASE_URL -> Colab FastAPI tunnel -> TRIBE v2
```

The Colab service implements the same contract as the normal GPU service:

- `GET /health`
- `POST /v1/inference`
- Optional `Authorization: Bearer <INFERENCE_API_KEY>`

## 1. Open Colab with GPU

In Colab:

1. Runtime -> Change runtime type
2. Hardware accelerator -> GPU
3. Open `notebooks/tribev2_colab_api.py` in Colab, or copy/paste its cells into a new Colab notebook

## 2. Required secrets in Colab

Set these in the Colab notebook (sidebar key icon → Secrets):

| Secret name | Required | Value |
|---|---|---|
| `HF_TOKEN` | Yes | Hugging Face **Read** token from [huggingface.co/settings/tokens](https://huggingface.co/settings/tokens) |
| `INFERENCE_API_KEY` | Optional | Any strong random string; use the **same** value on Render |

Enable **Notebook access** for each secret. The notebook loads them automatically — do not hardcode tokens in the file.

Accept gated licenses on [facebook/tribev2](https://huggingface.co/facebook/tribev2) before running real inference.

## 3. Render variables during demo

After the notebook starts Cloudflare Tunnel, copy the public `https://...trycloudflare.com` URL and set:

| Render API variable | Demo value |
|---|---|
| `INFERENCE_BASE_URL` | `https://<your-cloudflare-tunnel>.trycloudflare.com` |
| `INFERENCE_API_KEY` | same value as the Colab notebook |

Redeploy or restart the Render API/worker so it picks up the new values.

## 4. Test from your laptop

Replace the URL and key:

```bash
curl -X POST "https://<your-cloudflare-tunnel>.trycloudflare.com/v1/inference" \
  -H "Authorization: Bearer <INFERENCE_API_KEY>" \
  -H "Content-Type: application/json" \
  -d '{"modality":"text","model_id":"facebook/tribev2","payload":{"text":"Hello from Audira demo."}}'
```

Expected response shape:

```json
{
  "output": {
    "model": "facebook/tribev2",
    "mesh": "fsaverage5"
  },
  "cost_usd": 0.08,
  "provider": "colab-tribev2-gpu",
  "model_id": "facebook/tribev2",
  "latency_ms": 12345
}
```

## Operational notes

- The tunnel URL changes every Colab session. Update `INFERENCE_BASE_URL` each time.
- Keep the notebook tab open while demoing.
- Use `TRIBE_ALLOW_STUB=1` first to prove the tunnel works.
- Use `TRIBE_ALLOW_STUB=0` only after TRIBE v2 installs and model download succeeds.
- TRIBE v2 is licensed `CC-BY-NC-4.0`; use it only for non-commercial research/demo unless you have commercial rights.
