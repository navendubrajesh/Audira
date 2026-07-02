"""Brand alignment scoring (TCA-002, TCA-034)."""

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

    sections = score_brand_sections(
        text,
        terminology_do=do_terms,
        terminology_dont=dont_terms,
        messaging_pillars=pillars,
    )

    return {
        "score": round(score, 1),
        "preferred_terms_used": do_hits,
        "prohibited_terms": dont_hits,
        "pillars_reflected": pillar_hits,
        "sections": sections,
        "metric": "brand_alignment",
    }


def score_brand_sections(
    text: str,
    *,
    terminology_do: list[str],
    terminology_dont: list[str],
    messaging_pillars: list[str],
) -> list[dict]:
    blocks = [b.strip() for b in re.split(r"\n\s*\n", text) if b.strip()]
    if not blocks:
        blocks = [text]
    out: list[dict] = []
    for i, block in enumerate(blocks[:10]):
        block_lower = block.lower()
        dont = [t for t in terminology_dont if t.lower() in block_lower]
        do = [t for t in terminology_do if t.lower() in block_lower]
        s = 75.0 + min(15, len(do) * 5) - min(30, len(dont) * 10)
        out.append(
            {
                "section": i + 1,
                "preview": block[:80],
                "score": round(max(0, min(100, s)), 1),
                "deviations": dont,
            }
        )
    return out
