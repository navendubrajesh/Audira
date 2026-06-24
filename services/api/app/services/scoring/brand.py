"""Brand alignment scoring (TCA-002)."""

import re


def score_brand_alignment(
    text: str,
    *,
    terminology_do: list[str] | None = None,
    terminology_dont: list[str] | None = None,
    messaging_pillars: list[str] | None = None,
) -> dict:
    lower = text.lower()
    do_terms = terminology_do or []
    dont_terms = terminology_dont or []
    pillars = messaging_pillars or []

    do_hits = [t for t in do_terms if t.lower() in lower]
    dont_hits = [t for t in dont_terms if t.lower() in lower]
    pillar_hits = [p for p in pillars if p.lower() in lower]

    score = 70.0
    score += min(20, len(do_hits) * 5)
    score += min(10, len(pillar_hits) * 5)
    score -= min(40, len(dont_hits) * 12)
    score = max(0.0, min(100.0, score))

    return {
        "score": round(score, 1),
        "preferred_terms_used": do_hits,
        "prohibited_terms": dont_hits,
        "pillars_reflected": pillar_hits,
        "metric": "brand_alignment",
    }
