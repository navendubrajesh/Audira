"""Analysis API — run, history, uploads, compare, rerun."""

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
from app.services.analysis_service import rerun_analysis, run_text_analysis
from app.services.document_parser import parse_document
from app.services.storage import store_artifact
from app.services.tenant_service import TenantIsolationError, assert_tenant_resource

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
    fast_lane: bool = True
    full_analysis: bool = False


class CompareRequest(BaseModel):
    variant_a: str = Field(..., min_length=1, max_length=50000)
    variant_b: str = Field(..., min_length=1, max_length=50000)
    objective: Literal["inform", "engage", "drive_action", "reassure", "celebrate"] | None = "engage"
    artifact_type_code: str | None = "email"


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
        fast_lane=body.fast_lane,
        full_analysis=body.full_analysis,
    )
    return AnalyzeResponse(
        id=str(run.id),
        composite_score=run.composite_score,
        latency_ms=run.latency_ms,
        model_id=run.model_id,
        mapping_version=run.mapping_version,
        result=run.result,
    )


@router.post("/compare")
async def compare_variants(
    body: CompareRequest,
    principal: Annotated[Principal, Depends(require_permission("analyses.run"))],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """TCA-040 — A/B variant comparison."""
    run_a = await run_text_analysis(
        db,
        tenant_id=principal.tenant_id,
        user_id=principal.user_id,
        text=body.variant_a,
        artifact_type_code=body.artifact_type_code,
        objective=body.objective,
        fast_lane=True,
    )
    run_b = await run_text_analysis(
        db,
        tenant_id=principal.tenant_id,
        user_id=principal.user_id,
        text=body.variant_b,
        artifact_type_code=body.artifact_type_code,
        objective=body.objective,
        fast_lane=True,
    )
    score_a = run_a.composite_score or 0
    score_b = run_b.composite_score or 0
    return {
        "variant_a": {"id": str(run_a.id), "composite_score": score_a},
        "variant_b": {"id": str(run_b.id), "composite_score": score_b},
        "winner": "a" if score_a >= score_b else "b",
        "delta": round(abs(score_a - score_b), 1),
    }


@router.post("/runs/{run_id}/rerun", response_model=AnalyzeResponse)
async def rerun(
    run_id: UUID,
    principal: Annotated[Principal, Depends(require_permission("analyses.run"))],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    run = await rerun_analysis(db, run_id, principal.tenant_id, principal.user_id)
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
            "verdict": (r.result or {}).get("verdict", {}).get("label"),
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
        "input_hash": run.input_hash,
        "result": run.result,
        "input_text": run.input_text,
    }


@router.post("/upload")
async def upload_artifact(
    principal: Annotated[Principal, Depends(require_permission("analyses.run"))],
    db: Annotated[AsyncSession, Depends(get_db)],
    file: UploadFile = File(...),
    artifact_type_code: str = "email",
):
    """TCA-007 — parse docx/pdf/pptx/txt and store blob."""
    content = await file.read()
    storage_key = store_artifact(principal.tenant_id, file.filename or "upload.txt", content)
    parsed = parse_document(file.filename or "", content, file.content_type)

    is_engineering = (
        "engineering_spec" in (file.filename or "").lower()
        or parsed.format == "unknown"
        and not parsed.text.strip()
        and "spec" in (file.filename or "").lower()
    )

    upload = ArtifactUpload(
        tenant_id=principal.tenant_id,
        filename=file.filename or "upload.txt",
        content_type=file.content_type or "text/plain",
        storage_key=storage_key,
        parsed={
            "text": parsed.text[:50000],
            "format": parsed.format,
            "page_count": parsed.page_count,
            "slide_count": parsed.slide_count,
            "warnings": parsed.warnings,
        },
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

    if not parsed.text.strip():
        raise HTTPException(
            status_code=400,
            detail={"message": "Could not extract text.", "warnings": parsed.warnings},
        )

    run = await run_text_analysis(
        db,
        tenant_id=principal.tenant_id,
        user_id=principal.user_id,
        text=parsed.text[:50000],
        artifact_type_code=artifact_type_code,
        fast_lane=True,
    )
    return {
        "upload_id": str(upload.id),
        "storage_key": storage_key,
        "analysis_id": str(run.id),
        "composite_score": run.composite_score,
        "parsed": upload.parsed,
        "result": run.result,
    }
