"""Structure & scannability scoring (TCA-031)."""

import re

_HEADING = re.compile(r"^#{1,6}\s+|^[A-Z][^.!?]{0,80}:$", re.MULTILINE)
_LONG_BLOCK = re.compile(r"(?:[^\n]{200,})")


def score_structure(text: str, channel: str | None = None) -> dict:
    paragraphs = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]
    headings = _HEADING.findall(text)
    long_blocks = _LONG_BLOCK.findall(text)
    bullet_lines = len(re.findall(r"^\s*[-*•]\s+", text, re.MULTILINE))

    score = 65.0
    score += min(15, len(headings) * 5)
    score += min(10, bullet_lines * 2)
    score -= min(25, len(long_blocks) * 8)
    if channel == "email" and len(paragraphs) > 8:
        score -= 10
    if channel == "intranet" and len(headings) < 1 and len(text) > 500:
        score -= 12

    suggestions: list[str] = []
    if long_blocks:
        suggestions.append("Break up long paragraphs for better scannability.")
    if not headings and len(text) > 400:
        suggestions.append("Add headings or subheadings to guide readers.")
    if bullet_lines == 0 and len(paragraphs) > 4:
        suggestions.append("Consider bullet points for key takeaways.")

    return {
        "score": round(max(0.0, min(100.0, score)), 1),
        "headings_count": len(headings),
        "long_blocks": len(long_blocks),
        "bullet_lines": bullet_lines,
        "paragraph_count": len(paragraphs),
        "suggestions": suggestions,
        "metric": "structure_scannability",
    }
