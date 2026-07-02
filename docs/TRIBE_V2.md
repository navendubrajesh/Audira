# TRIBE v2 integration

**Model:** [facebook/tribev2](https://huggingface.co/facebook/tribev2) on Hugging Face  
**Backlog:** TCA-013, TCA-014, TCA-015 (mapping layer separate)  
**License:** [CC-BY-NC-4.0](https://huggingface.co/facebook/tribev2) — non-commercial. Production use in a sold product requires Meta commercial licence or routing production to a commercially-licensed model (PRD §13, TCA-016).

## What TRIBE v2 is

Meta FAIR's multimodal brain encoding model. It predicts fMRI-style cortical responses from **video, audio, or text** using LLaMA 3.2, V-JEPA2, and Wav2Vec-BERT encoders. Output lives on the **fsaverage5** mesh (~20k vertices).

Quick start from the model card:

```python
from tribev2 import TribeModel

model = TribeModel.from_pretrained("facebook/tribev2", cache_folder="./cache")
df = model.get_events_dataframe(video_path="path/to/video.mp4")
preds, segments = model.predict(events=df)
```

## Where it runs in Audira.run

TRIBE v2 **never** runs inside Vercel or Render API containers. It runs in:

```
services/inference/tribev2/   ← GPU Docker service
         ▲
         │ POST /v1/inference
         │
services/worker  →  HttpGpuProvider  →  INFERENCE_BASE_URL
```

Code path:

1. Web/API submits job with `model_id: "facebook/tribev2"`
2. Worker calls GPU service
3. GPU service loads `TribeModel` and returns raw fMRI-shaped output
4. Mapping layer (TCA-015, future) converts raw output → comms metrics

## Setup checklist

1. **Hugging Face account** — create token at [huggingface.co/settings/tokens](https://huggingface.co/settings/tokens)
2. **Accept LLaMA 3.2 licence** — gated dependency; accept on HF model page
3. **GPU host** — Modal, RunPod, AWS g5, Azure NC-series, or local CUDA
4. **Deploy** `services/inference/tribev2/Dockerfile` to GPU host
5. **Set secrets:**
   - `HF_TOKEN` on GPU service
   - `INFERENCE_API_KEY` on GPU service and Render API (same value)
   - `INFERENCE_BASE_URL` on Render API → GPU service URL

## API contract (GPU service)

**POST /v1/inference**

```json
{
  "modality": "text",
  "model_id": "facebook/tribev2",
  "payload": {
    "text": "Your communication artifact text here..."
  }
}
```

Or provide `video_path`, `audio_path`, or `text_path` (paths on the GPU container filesystem / mounted object storage).

**Response:**

```json
{
  "output": {
    "model": "facebook/tribev2",
    "raw_fmri_shape": [120, 10242],
    "n_vertices": 10242,
    "mesh": "fsaverage5"
  },
  "latency_ms": 45000,
  "cost_usd": 0.08,
  "provider": "tribe-v2-gpu"
}
```

## Dev without GPU

Leave `INFERENCE_BASE_URL` empty. Jobs with `model_id: tribe-v2-stub` use `MockGpuProvider` and return stub metrics — enough for UI/API/workflow development.

## Next backlog items

| Story | Purpose |
|---|---|
| TCA-014 | Model abstraction routing (partially done via `factory.py`) |
| TCA-013 | Mark done once GPU tier deployed + end-to-end test |
| TCA-015 | Map raw fMRI output → attention/clarity/etc. scores |
| TCA-016 | Licence register + legal sign-off |
