"""Phase 2/3 feature endpoints — MVP stubs satisfying backlog routes."""

from typing import Annotated

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.auth.dependencies import get_current_user, require_permission
from app.auth.principal import Principal

router = APIRouter(prefix="/features", tags=["features"])


class AddInAnalyzeRequest(BaseModel):
    text: str
    source: str = "word"


@router.post("/addin/analyze")
async def addin_analyze(
    body: AddInAnalyzeRequest,
    principal: Annotated[Principal, Depends(require_permission("analyses.run"))],
):
    """TCA-048 / TCA-049 / TCA-050 — Office add-in analysis hook."""
    return {
        "status": "accepted",
        "source": body.source,
        "message": "Use POST /analyze for full scoring; add-in SDK routes here in production.",
        "tenant_id": str(principal.tenant_id),
    }


@router.get("/analytics/dashboard")
async def analytics_dashboard(
    principal: Annotated[Principal, Depends(get_current_user)],
):
    """TCA-039 / TCA-055 — org-level analytics stub."""
    return {
        "tenant_id": str(principal.tenant_id),
        "period": "30d",
        "avg_composite_score": 71.2,
        "analyses_count": 0,
        "top_audiences": [],
    }


@router.get("/campaigns")
async def list_campaigns(principal: Annotated[Principal, Depends(get_current_user)]):
    """TCA-051 / TCA-054 — campaign tracking stub."""
    return {"campaigns": [], "tenant_id": str(principal.tenant_id)}


@router.post("/simulations/what-if")
async def what_if_simulation(
    body: dict,
    principal: Annotated[Principal, Depends(require_permission("analyses.run"))],
):
    """TCA-009 / TCA-017 / TCA-018 — what-if simulation stub."""
    return {
        "baseline_score": body.get("baseline_score", 70),
        "projected_score": 74,
        "delta": 4,
        "changes_applied": body.get("changes", []),
    }


@router.get("/integrations")
async def list_integrations(principal: Annotated[Principal, Depends(get_current_user)]):
    """TCA-036 / TCA-073 — integration catalogue."""
    return {
        "integrations": [
            {"id": "workday", "status": "planned"},
            {"id": "sharepoint", "status": "planned"},
            {"id": "teams", "status": "planned"},
        ]
    }


@router.get("/guardrails/status")
async def guardrail_status(principal: Annotated[Principal, Depends(get_current_user)]):
    """TCA-037 / TCA-044 / TCA-060 — guardrail checkpoint (requires human review before enable)."""
    return {
        "stories": ["TCA-037", "TCA-044", "TCA-060"],
        "enabled": False,
        "message": "Guardrail stories require product/legal sign-off before activation.",
    }
