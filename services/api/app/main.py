"""FastAPI application factory."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.db.base import Base
from app.db.session import engine, async_session_factory
from app.models import audit_log, inference_job, tenant, user  # noqa: F401 — register models
from app.routers import admin, auth, health, inference, tenant, webhooks
from app.services.tenant_service import ensure_default_tenant


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    async with async_session_factory() as session:
        await ensure_default_tenant(session)
    yield
    await engine.dispose()


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description=(
            "Resonode orchestration API — ingestion, model routing, mapping/calibration, "
            "and governance. GPU inference runs on a decoupled tier."
        ),
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(health.router)
    app.include_router(auth.router)
    app.include_router(inference.router)
    app.include_router(tenant.router)
    app.include_router(webhooks.router)
    app.include_router(admin.router)

    return app
