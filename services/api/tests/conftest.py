"""Pytest configuration — in-memory SQLite for tests."""

import os
import sys
from collections.abc import AsyncGenerator
from pathlib import Path

import pytest
from httpx import ASGITransport, AsyncClient

os.environ.setdefault(
    "DATABASE_URL",
    "sqlite+aiosqlite:///file:audira_test?mode=memory&cache=shared&uri=true",
)
os.environ.setdefault("AUTH_MODE", "development")
os.environ.setdefault(
    "JWT_SECRET",
    "test-jwt-secret-at-least-32-characters-long",
)

API_ROOT = Path(__file__).resolve().parents[1]
SHARED_ROOT = API_ROOT.parent / "shared"
WORKER_ROOT = API_ROOT.parent / "worker"
if str(API_ROOT) not in sys.path:
    sys.path.insert(0, str(API_ROOT))
if str(SHARED_ROOT) not in sys.path:
    sys.path.insert(0, str(SHARED_ROOT))
if str(WORKER_ROOT) not in sys.path:
    sys.path.insert(0, str(WORKER_ROOT))


@pytest.fixture
async def client() -> AsyncGenerator[AsyncClient, None]:
    from app.main import create_app

    app = create_app()
    async with app.router.lifespan_context(app):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            yield ac


@pytest.fixture(autouse=True)
def mock_redis_enqueue(monkeypatch):
    async def noop(*_args, **_kwargs):
        return None

    monkeypatch.setattr("app.routers.inference.enqueue_inference_job", noop)
    monkeypatch.setattr("app.routers.inference.enqueue_batch_jobs", noop)


@pytest.fixture
async def db_session():
    from app.db.session import async_session_factory

    async with async_session_factory() as session:
        yield session
