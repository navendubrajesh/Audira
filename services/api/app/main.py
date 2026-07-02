"""FastAPI application factory."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.db.base import Base
from app.db.session import engine, async_session_factory
from app.models import (  # noqa: F401 — register models
    analysis,
    audience,
    audit_log,
    context,
    governance,
    inference_job,
    studio,
    tenant,
    user,
)
from app.routers import (
    admin,
    analyze,
    audiences,
    auth,
    context,
    features,
    governance,
    guardrails,
    health,
    inference,
    observability,
    privacy,
    studio,
    tenant,
    webhooks,
)
from app.services.seed_defaults import seed_global_governance, seed_tenant_defaults
from app.services.tenant_service import ensure_default_tenant


@asynccontextmanager
async def lifespan(app: FastAPI):
    if settings.hf_token:
        from audira_core.huggingface import apply_hf_token_env

        apply_hf_token_env(settings.hf_token)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    async with async_session_factory() as session:
        tenant = await ensure_default_tenant(session)
        await seed_tenant_defaults(session, tenant.id)
        await seed_global_governance(session)
    yield
    await engine.dispose()


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description=(
            "Audira.run orchestration API — ingestion, model routing, mapping/calibration, "
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
    app.include_router(audiences.router)
    app.include_router(context.router)
    app.include_router(analyze.router)
    app.include_router(governance.router)
    app.include_router(guardrails.router)
    app.include_router(privacy.router)
    app.include_router(observability.router)
    app.include_router(features.router)
    app.include_router(studio.router)
    app.include_router(webhooks.router)
    app.include_router(admin.router)

    return app
