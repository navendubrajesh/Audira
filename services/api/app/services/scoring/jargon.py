"""Jargon density scoring (TCA-029)."""

import re

_ACRONYM = re.compile(r"\b[A-Z]{2,}\b")
_LONG = re.compile(r"\b[a-zA-Z]{12,}\b")
_DEFAULT_JARGON = {
    "synergize",
    "leverage",
    "paradigm",
    "bandwidth",
    "circle back",
    "move the needle",
    "low-hanging fruit",
}


def score_jargon_density(text: str, extra_terms: list[str] | None = None) -> dict:
    words = re.findall(r"\b\w+\b", text.lower())
    total = max(len(words), 1)
    jargon_set = _DEFAULT_JARGON | {t.lower() for t in (extra_terms or [])}

    hits: list[str] = []
    for term in jargon_set:
        if term in text.lower():
            hits.append(term)
    hits.extend(_ACRONYM.findall(text))
    hits.extend(_LONG.findall(text))
    unique_hits = sorted(set(hits))

    density = min(100.0, (len(unique_hits) / total) * 400)
    score = max(0.0, 100.0 - density * 2)

    return {
        "score": round(score, 1),
        "density_pct": round((len(unique_hits) / total) * 100, 2),
        "flagged_terms": unique_hits[:20],
        "metric": "jargon_density",
    }
