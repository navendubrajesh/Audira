"""Object storage for artifact uploads (TCA-007)."""

from __future__ import annotations

import hashlib
from pathlib import Path
from uuid import UUID

from app.config import settings

LOCAL_UPLOAD_ROOT = Path(__file__).resolve().parents[2] / "uploads"


def store_artifact(tenant_id: UUID, filename: str, content: bytes) -> str:
    """Persist blob locally in dev; returns storage key."""
    if settings.object_storage_endpoint and settings.object_storage_bucket:
        return _store_s3_compatible(tenant_id, filename, content)

    LOCAL_UPLOAD_ROOT.mkdir(parents=True, exist_ok=True)
    digest = hashlib.sha256(content).hexdigest()[:16]
    safe_name = filename.replace("/", "_").replace("\\", "_")[:200]
    key = f"{tenant_id}/{digest}_{safe_name}"
    path = LOCAL_UPLOAD_ROOT / key.replace("/", "_")
    path.write_bytes(content)
    return key


def _store_s3_compatible(tenant_id: UUID, filename: str, content: bytes) -> str:
    try:
        import boto3
        from botocore.client import Config

        client = boto3.client(
            "s3",
            endpoint_url=settings.object_storage_endpoint or None,
            aws_access_key_id=settings.object_storage_access_key or None,
            aws_secret_access_key=settings.object_storage_secret_key or None,
            config=Config(signature_version="s3v4"),
        )
        digest = hashlib.sha256(content).hexdigest()[:16]
        key = f"{tenant_id}/{digest}/{filename}"
        client.put_object(Bucket=settings.object_storage_bucket, Key=key, Body=content)
        return key
    except Exception:
        LOCAL_UPLOAD_ROOT.mkdir(parents=True, exist_ok=True)
        digest = hashlib.sha256(content).hexdigest()[:16]
        key = f"{tenant_id}/{digest}_{filename}"
        (LOCAL_UPLOAD_ROOT / key.replace("/", "_")).write_bytes(content)
        return key
