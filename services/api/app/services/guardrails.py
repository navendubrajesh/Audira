"""Guardrail enforcement (TCA-037, TCA-044, TCA-060) — disabled by default until enabled."""

from __future__ import annotations

import re
from typing import Any

# TCA-037 — generative AI / unverified claims
_AI_MARKERS = {
    "as an ai",
    "language model",
    "i cannot",
    "hallucination",
    "generated content",
}
_UNVERIFIED_PATTERNS = [
    (r"\b\d{1,3}%\s+(?:increase|decrease|growth)\b", "Verify statistic before publishing."),
    (r"\bguaranteed\b", "Avoid absolute guarantees in enterprise comms."),
]

# TCA-060 — regulated / risk language
_REGULATED_PHRASES = {
    "investment advice": "Requires financial compliance review.",
    "medical advice": "Requires clinical/legal review.",
    "legally binding": "Requires legal sign-off.",
    "hipaa": "Ensure PHI handling compliance.",
    "gdpr": "Ensure data-processing compliance statement is accurate.",
}


def check_generative_governance(text: str) -> dict[str, Any]:
    """TCA-037 — score LLM-style or unverified content."""
    lower = text.lower()
    ai_hits = [m for m in _AI_MARKERS if m in lower]
    unverified = []
    for pattern, note in _UNVERIFIED_PATTERNS:
        if re.search(pattern, text, re.I):
            unverified.append({"pattern": pattern, "note": note})
    penalty = len(ai_hits) * 15 + len(unverified) * 10
    score = max(0.0, 100.0 - penalty)
    action = "block" if score < 40 else "warn" if score < 70 else "pass"
    return {
        "score": round(score, 1),
        "ai_markers": ai_hits,
        "unverified_claims": unverified,
        "action": action,
        "metric": "generative_governance",
    }


def check_regulated_claims(text: str) -> dict[str, Any]:
    """TCA-060 — regulated-claim and risk-language detection."""
    lower = text.lower()
    flags = [{"phrase": p, "requirement": r} for p, r in _REGULATED_PHRASES.items() if p in lower]
    high_risk = [f for f in flags if "compliance" in f["requirement"].lower() or "legal" in f["requirement"].lower()]
    action = "review_required" if flags else "pass"
    return {
        "score": round(max(0.0, 100.0 - len(flags) * 20), 1),
        "flags": flags,
        "high_risk_count": len(high_risk),
        "action": action,
        "metric": "regulated_claims",
    }


def guardrailed_rewrite(text: str, suggestion: str) -> dict[str, Any]:
    """TCA-044 — propose rewrite; human must approve before apply."""
    proposed = text
    if suggestion.startswith("replace:") and "->" in suggestion:
        src, dst = suggestion.removeprefix("replace:").split("->", 1)
        proposed = text.replace(src.strip(), dst.strip())
    return {
        "original": text,
        "proposed": proposed,
        "status": "pending_human_approval",
        "message": "Rewrite requires explicit human approval before use (TCA-044).",
    }
