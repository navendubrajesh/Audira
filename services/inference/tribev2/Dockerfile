# TRIBE v2 GPU inference service
# Build on a CUDA base for production. CPU image is for structure validation only.
FROM python:3.12-slim

WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    TRIBE_CACHE_DIR=/cache/tribev2 \
    HF_HOME=/cache/huggingface

COPY services/inference/tribev2/requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt

COPY services/inference/tribev2/ /app/

EXPOSE 8080
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]

# Production: use nvidia/cuda:12.x runtime, install tribev2 + torch with CUDA,
# mount HF_TOKEN at runtime, and use a GPU-enabled host (Modal, RunPod, AWS g5, etc.)
