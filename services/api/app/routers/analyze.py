"""Analysis API — run, history, uploads (TCA-007, TCA-008, TCA-020, TCA-038)."""

from typing import Annotated, Literal
from uuid import UUID

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import get_current_user, require_permission
from app.auth.principal import Principal
from app.db.session import get_db
from app.models.analysis import AnalysisRun, ArtifactUpload
from app.models.context import ArtifactType
from app.services.analysis_service import run_text_analysis
from app.services.tenant_service import assert_tenant_resource, TenantIsolationError

router = APIRouter(prefix="/analyze", tags=["analyze"])

OBJECTIVES = ["inform", "engage", "drive_action", "reassure", "celebrate"]
CHANNELS = ["email", "intranet", "town_hall", "slack", "press", "video"]


class AnalyzeRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=50000)
    audience_id: str | None = None
    artifact_type_code: str | None = None
    objective: Literal["inform", "engage", "drive_action", "reassure", "celebrate"] | None = None
    channel: str | None = None
    model_id: str = "tribe-v2-stub"


class AnalyzeResponse(BaseModel):
    id: str
    composite_score: float | None
    latency_ms: int | None
    model_id: str
    mapping_version: str
    result: dict


@router.get("/objectives")
async def list_objectives():
    return {"objectives": OBJECTIVES, "channels": CHANNELS}


@router.post("", response_model=AnalyzeResponse)
async def analyze_text(
    body: AnalyzeRequest,
    principal: Annotated[Principal, Depends(require_permission("analyses.run"))],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    if body.artifact_type_code:
        result = await db.execute(
            select(ArtifactType).where(
                ArtifactType.tenant_id == principal.tenant_id,
                ArtifactType.code == body.artifact_type_code,
            )
        )
        artifact = result.scalar_one_or_none()
        if artifact and artifact.block_engineering:
            raise HTTPException(
                status_code=400,
                detail="Engineering artifacts are excluded from comms analysis.",
            )

    audience_uuid = UUID(body.audience_id) if body.audience_id else None
    run = await run_text_analysis(
        db,
        tenant_id=principal.tenant_id,
        user_id=principal.user_id,
        text=body.text,
        audience_id=audience_uuid,
        artifact_type_code=body.artifact_type_code,
        objective=body.objective,
        channel=body.channel,
        model_id=body.model_id,
    )
    return AnalyzeResponse(
        id=str(run.id),
        composite_score=run.composite_score,
        latency_ms=run.latency_ms,
        model_id=run.model_id,
        mapping_version=run.mapping_version,
        result=run.result,
    )


@router.get("/runs")
async def list_runs(
    principal: Annotated[Principal, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    limit: int = 20,
):
    result = await db.execute(
        select(AnalysisRun)
        .where(AnalysisRun.tenant_id == principal.tenant_id)
        .order_by(AnalysisRun.created_at.desc())
        .limit(min(limit, 100))
    )
    runs = result.scalars().all()
    return [
        {
            "id": str(r.id),
            "composite_score": r.composite_score,
            "artifact_type_code": r.artifact_type_code,
            "objective": r.objective,
            "created_at": r.created_at.isoformat(),
        }
        for r in runs
    ]


@router.get("/runs/{run_id}")
async def get_run(
    run_id: UUID,
    principal: Annotated[Principal, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    run = await db.get(AnalysisRun, run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Analysis not found")
    try:
        assert_tenant_resource(run.tenant_id, principal.tenant_id)
    except TenantIsolationError:
        raise HTTPException(status_code=404, detail="Analysis not found") from None
    return {
        "id": str(run.id),
        "composite_score": run.composite_score,
        "latency_ms": run.latency_ms,
        "model_id": run.model_id,
        "mapping_version": run.mapping_version,
        "result": run.result,
        "input_text": run.input_text,
    }


@router.post("/upload")
async def upload_artifact(
    principal: Annotated[Principal, Depends(require_permission("analyses.run"))],
    db: Annotated[AsyncSession, Depends(get_db)],
    file: UploadFile = File(...),
):
    """TCA-007 — ingest text-bearing artifacts (txt/md/pdf stub)."""
    content = await file.read()
    text = content.decode("utf-8", errors="ignore")
    is_engineering = "engineering_spec" in (file.filename or "").lower() or "spec" in (
        file.content_type or ""
    )

    upload = ArtifactUpload(
        tenant_id=principal.tenant_id,
        filename=file.filename or "upload.txt",
        content_type=file.content_type or "text/plain",
        storage_key=None,
        parsed={"text": text[:50000], "char_count": len(text)},
        is_engineering=is_engineering,
    )
    db.add(upload)
    await db.commit()
    await db.refresh(upload)

    if is_engineering:
        return {
            "id": str(upload.id),
            "status": "excluded",
            "reason": "Engineering artifact — out of scope for comms scoring.",
        }

    run = await run_text_analysis(
        db,
        tenant_id=principal.tenant_id,
        user_id=principal.user_id,
        text=text[:50000],
        artifact_type_code="email",
    )
    return {
        "upload_id": str(upload.id),
        "analysis_id": str(run.id),
        "composite_score": run.composite_score,
        "result": run.result,
    }
