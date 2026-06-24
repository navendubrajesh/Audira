"""Model governance & validation (TCA-016, TCA-019, TCA-063, TCA-070)."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import get_current_user, require_roles
from app.auth.principal import Principal
from app.auth.roles import Role
from app.db.session import get_db
from app.models.governance import ModelRegistryEntry, ValidationMetric
from app.services.seed_defaults import seed_global_governance

router = APIRouter(prefix="/governance", tags=["governance"])


class ModelChangelogEntry(BaseModel):
    version: str
    note: str


@router.get("/models")
async def list_models(
    principal: Annotated[Principal, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    await seed_global_governance(db)
    result = await db.execute(select(ModelRegistryEntry).order_by(ModelRegistryEntry.model_id))
    return [
        {
            "model_id": m.model_id,
            "version": m.version,
            "licence": m.licence,
            "commercial_ok": m.commercial_ok,
            "status": m.status,
            "modalities": m.modalities,
            "legal_signoff": m.legal_signoff,
            "changelog": m.changelog,
        }
        for m in result.scalars().all()
    ]


@router.get("/validation-metrics")
async def validation_metrics(
    principal: Annotated[Principal, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    await seed_global_governance(db)
    result = await db.execute(select(ValidationMetric))
    return [
        {
            "metric_name": v.metric_name,
            "accuracy": v.accuracy,
            "sample_size": v.sample_size,
            "methodology": v.methodology,
        }
        for v in result.scalars().all()
    ]


@router.post("/models/{model_id}/changelog")
async def append_changelog(
    model_id: str,
    entry: ModelChangelogEntry,
    principal: Annotated[Principal, Depends(require_roles(Role.ML_PLATFORM_ENG, Role.ADMIN))],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    result = await db.execute(
        select(ModelRegistryEntry).where(ModelRegistryEntry.model_id == model_id)
    )
    model = result.scalar_one_or_none()
    if not model:
        raise HTTPException(status_code=404, detail="Model not found")
    log = list(model.changelog or [])
    log.append(entry.model_dump())
    model.changelog = log
    model.version = entry.version
    await db.commit()
    return {"model_id": model_id, "changelog": model.changelog}
