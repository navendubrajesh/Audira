"""E01 context — artifact types, standards, brand (TCA-004, TCA-005, TCA-002)."""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import get_current_user, require_permission
from app.auth.principal import Principal
from app.db.session import get_db
from app.models.context import ArtifactType, BrandProfile, StandardsRule
from app.models.governance import TenantQualityGates
from app.services.seed_defaults import seed_tenant_defaults
from app.services.tenant_service import assert_tenant_resource, TenantIsolationError

router = APIRouter(prefix="/context", tags=["context"])


class ArtifactTypeResponse(BaseModel):
    id: str
    code: str
    label: str
    checks: list
    block_engineering: bool
    is_active: bool


class StandardsRuleBody(BaseModel):
    artifact_type_code: str | None = None
    rule_type: str = "inclusive"
    pattern: str
    replacement: str | None = None
    metadata: dict = Field(default_factory=dict)
    status: str = "draft"


class BrandProfileBody(BaseModel):
    voice_attributes: dict = Field(default_factory=dict)
    terminology_do: list[str] = Field(default_factory=list)
    terminology_dont: list[str] = Field(default_factory=list)
    messaging_pillars: list[str] = Field(default_factory=list)
    target_tone: str = "professional"


@router.get("/artifact-types", response_model=list[ArtifactTypeResponse])
async def list_artifact_types(
    principal: Annotated[Principal, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    await seed_tenant_defaults(db, principal.tenant_id)
    result = await db.execute(
        select(ArtifactType).where(
            ArtifactType.tenant_id == principal.tenant_id, ArtifactType.is_active.is_(True)
        )
    )
    return [
        ArtifactTypeResponse(
            id=str(a.id),
            code=a.code,
            label=a.label,
            checks=a.checks,
            block_engineering=a.block_engineering,
            is_active=a.is_active,
        )
        for a in result.scalars().all()
    ]


@router.post("/artifact-types", response_model=ArtifactTypeResponse, status_code=201)
async def create_artifact_type(
    body: ArtifactTypeResponse,
    principal: Annotated[Principal, Depends(require_permission("standards.manage"))],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    row = ArtifactType(
        tenant_id=principal.tenant_id,
        code=body.code,
        label=body.label,
        checks=body.checks,
        block_engineering=body.block_engineering,
        is_active=body.is_active,
    )
    db.add(row)
    await db.commit()
    await db.refresh(row)
    return ArtifactTypeResponse(
        id=str(row.id),
        code=row.code,
        label=row.label,
        checks=row.checks,
        block_engineering=row.block_engineering,
        is_active=row.is_active,
    )


@router.get("/standards")
async def list_standards(
    principal: Annotated[Principal, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    result = await db.execute(
        select(StandardsRule).where(StandardsRule.tenant_id == principal.tenant_id)
    )
    rules = result.scalars().all()
    return [
        {
            "id": str(r.id),
            "version": r.version,
            "status": r.status,
            "artifact_type_code": r.artifact_type_code,
            "rule_type": r.rule_type,
            "pattern": r.pattern,
            "replacement": r.replacement,
            "metadata": r.metadata_,
        }
        for r in rules
    ]


@router.post("/standards", status_code=201)
async def create_standard(
    body: StandardsRuleBody,
    principal: Annotated[Principal, Depends(require_permission("standards.manage"))],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    rule = StandardsRule(
        tenant_id=principal.tenant_id,
        artifact_type_code=body.artifact_type_code,
        rule_type=body.rule_type,
        pattern=body.pattern,
        replacement=body.replacement,
        metadata_=body.metadata,
        status=body.status,
    )
    db.add(rule)
    await db.commit()
    await db.refresh(rule)
    return {"id": str(rule.id), "status": rule.status}


@router.post("/standards/{rule_id}/publish")
async def publish_standard(
    rule_id: UUID,
    principal: Annotated[Principal, Depends(require_permission("standards.manage"))],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    rule = await db.get(StandardsRule, rule_id)
    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")
    try:
        assert_tenant_resource(rule.tenant_id, principal.tenant_id)
    except TenantIsolationError:
        raise HTTPException(status_code=404, detail="Rule not found") from None
    rule.status = "published"
    rule.version += 1
    await db.commit()
    return {"id": str(rule.id), "status": rule.status, "version": rule.version}


@router.post("/standards/{rule_id}/rollback")
async def rollback_standard(
    rule_id: UUID,
    principal: Annotated[Principal, Depends(require_permission("standards.manage"))],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """TCA-005 — revert published rule to draft."""
    rule = await db.get(StandardsRule, rule_id)
    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")
    try:
        assert_tenant_resource(rule.tenant_id, principal.tenant_id)
    except TenantIsolationError:
        raise HTTPException(status_code=404, detail="Rule not found") from None
    rule.status = "draft"
    await db.commit()
    return {"id": str(rule.id), "status": rule.status}


@router.get("/quality-gates")
async def get_quality_gates(
    principal: Annotated[Principal, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """TCA-052 — org quality thresholds."""
    await seed_tenant_defaults(db, principal.tenant_id)
    gates = await db.get(TenantQualityGates, principal.tenant_id)
    if not gates:
        from app.services.scoring.composite import NEEDS_WORK_THRESHOLD, PASS_THRESHOLD

        return {
            "pass_threshold": PASS_THRESHOLD,
            "needs_work_threshold": NEEDS_WORK_THRESHOLD,
            "block_publish_on_fail": False,
            "tenant_id": str(principal.tenant_id),
        }
    return {
        "pass_threshold": gates.pass_threshold,
        "needs_work_threshold": gates.needs_work_threshold,
        "block_publish_on_fail": gates.block_publish_on_fail,
        "tenant_id": str(principal.tenant_id),
    }


@router.patch("/quality-gates")
async def update_quality_gates(
    body: dict,
    principal: Annotated[Principal, Depends(require_permission("standards.manage"))],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    gates = await db.get(TenantQualityGates, principal.tenant_id)
    if not gates:
        gates = TenantQualityGates(tenant_id=principal.tenant_id)
        db.add(gates)
    for key in ("pass_threshold", "needs_work_threshold", "block_publish_on_fail"):
        if key in body:
            setattr(gates, key, body[key])
    await db.commit()
    return await get_quality_gates(principal, db)


@router.get("/brand")
async def get_brand(
    principal: Annotated[Principal, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    await seed_tenant_defaults(db, principal.tenant_id)
    result = await db.execute(
        select(BrandProfile)
        .where(BrandProfile.tenant_id == principal.tenant_id)
        .order_by(BrandProfile.version.desc())
        .limit(1)
    )
    brand = result.scalar_one_or_none()
    if not brand:
        raise HTTPException(status_code=404, detail="Brand profile not found")
    return {
        "id": str(brand.id),
        "version": brand.version,
        "status": brand.status,
        "voice_attributes": brand.voice_attributes,
        "terminology_do": brand.terminology_do,
        "terminology_dont": brand.terminology_dont,
        "messaging_pillars": brand.messaging_pillars,
        "target_tone": brand.target_tone,
    }


@router.put("/brand")
async def upsert_brand(
    body: BrandProfileBody,
    principal: Annotated[Principal, Depends(require_permission("brand.manage"))],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    result = await db.execute(
        select(BrandProfile)
        .where(BrandProfile.tenant_id == principal.tenant_id)
        .order_by(BrandProfile.version.desc())
        .limit(1)
    )
    current = result.scalar_one_or_none()
    version = (current.version + 1) if current else 1
    brand = BrandProfile(
        tenant_id=principal.tenant_id,
        version=version,
        status="published",
        **body.model_dump(),
    )
    db.add(brand)
    await db.commit()
    await db.refresh(brand)
    return {"id": str(brand.id), "version": brand.version, "status": brand.status}
