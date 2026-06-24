"""Residency and tenant isolation tests (TCA-068)."""

import uuid

import pytest
from httpx import AsyncClient

from app.auth.roles import Role
from app.auth.session import create_session_token
from app.models.tenant import Tenant
from app.models.user import User
from app.residency.regions import DataRegion
from app.services.inference_runner import run_inference_job_by_id
from app.tenants import SECOND_TENANT_ID


async def _token(client: AsyncClient, email: str, role: str = "comms_manager") -> str:
    login = await client.post("/auth/dev-login", params={"email": email, "role": role})
    return login.json()["token"]


@pytest.mark.asyncio
async def test_get_residency(client: AsyncClient) -> None:
    token = await _token(client, "residency@test.com", "security")
    response = await client.get(
        "/tenant/residency", headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    body = response.json()
    assert body["storage_region"] in ("IN", "EU")
    assert body["encryption_at_rest"] == "AES-256"
    assert body["tls_min_version"] == "1.2"
    assert body["tenant_isolation"] is True


@pytest.mark.asyncio
async def test_patch_residency(client: AsyncClient) -> None:
    token = await _token(client, "admin-res@test.com", "admin")
    response = await client.patch(
        "/tenant/residency",
        json={"storage_region": "EU", "processing_region": "EU"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    assert response.json()["storage_region"] == "EU"


@pytest.mark.asyncio
async def test_isolation_verify(client: AsyncClient) -> None:
    token = await _token(client, "sec-verify@test.com", "security")
    response = await client.get(
        "/tenant/residency/verify", headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert response.json()["cross_tenant_access_blocked"] is True


@pytest.mark.asyncio
async def test_cross_tenant_job_access_denied(client: AsyncClient, db_session) -> None:
    tenant_b = Tenant(
        id=SECOND_TENANT_ID,
        name="Other Org",
        storage_region=DataRegion.EU.value,
        processing_region=DataRegion.EU.value,
    )
    db_session.add(tenant_b)
    user_b = User(
        email="tenant-b@test.com",
        workos_user_id="dev-tenant-b@test.com",
        tenant_id=SECOND_TENANT_ID,
        roles=[Role.COMMS_MANAGER.value],
    )
    db_session.add(user_b)
    await db_session.commit()
    await db_session.refresh(user_b)

    token_a = await _token(client, "tenant-a@test.com", "comms_manager")
    submit = await client.post(
        "/inference/jobs",
        json={"modality": "text", "payload": {"text": "tenant a only"}},
        headers={"Authorization": f"Bearer {token_a}"},
    )
    job_id = submit.json()["id"]
    await run_inference_job_by_id(uuid.UUID(job_id))

    token_b = create_session_token(
        user_id=user_b.id,
        email=user_b.email,
        tenant_id=user_b.tenant_id,
        roles=[Role.COMMS_MANAGER],
    )
    poll = await client.get(
        f"/inference/jobs/{job_id}",
        headers={"Authorization": f"Bearer {token_b}"},
    )
    assert poll.status_code == 404
