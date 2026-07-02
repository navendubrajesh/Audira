"""Auth integration tests (TCA-067)."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_dev_login_and_me(client: AsyncClient) -> None:
    login = await client.post("/auth/dev-login", params={"email": "admin@test.com", "role": "admin"})
    assert login.status_code == 200
    token = login.json()["token"]

    me = await client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me.status_code == 200
    body = me.json()
    assert body["email"] == "admin@test.com"
    assert "admin" in body["roles"]
    assert "Administrator" in body["role_labels"]


@pytest.mark.asyncio
async def test_unauthenticated_me_rejected(client: AsyncClient) -> None:
    response = await client.get("/auth/me")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_audit_requires_permission(client: AsyncClient) -> None:
    login = await client.post(
        "/auth/dev-login", params={"email": "user@test.com", "role": "comms_manager"}
    )
    token = login.json()["token"]

    audit = await client.get("/admin/audit", headers={"Authorization": f"Bearer {token}"})
    assert audit.status_code == 403


@pytest.mark.asyncio
async def test_security_role_can_view_audit(client: AsyncClient) -> None:
    login = await client.post(
        "/auth/dev-login", params={"email": "sec@test.com", "role": "security"}
    )
    token = login.json()["token"]

    audit = await client.get("/admin/audit", headers={"Authorization": f"Bearer {token}"})
    assert audit.status_code == 200
    assert "entries" in audit.json()


@pytest.mark.asyncio
async def test_scim_webhook_provisions_user(client: AsyncClient) -> None:
    payload = {
        "event": "dsync.user.created",
        "data": {
            "id": "directory_user_01",
            "email": "scim@test.com",
            "state": "active",
            "groups": [{"name": "audira-admin"}],
        },
    }
    response = await client.post("/webhooks/workos/directory", json=payload)
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_logout_audited(client: AsyncClient) -> None:
    login = await client.post(
        "/auth/dev-login", params={"email": "sec@test.com", "role": "security"}
    )
    token = login.json()["token"]

    logout = await client.post("/auth/logout", headers={"Authorization": f"Bearer {token}"})
    assert logout.status_code == 200

    audit = await client.get("/admin/audit", headers={"Authorization": f"Bearer {token}"})
    actions = [e["action"] for e in audit.json()["entries"]]
    assert "auth.logout" in actions
