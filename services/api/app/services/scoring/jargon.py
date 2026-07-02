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


def score_jargon_density(
    text: str,
    *,
    banned_terms: list[str] | None = None,
    replacements: dict[str, str] | None = None,
) -> dict:
    words = re.findall(r"\b\w+\b", text.lower())
    total = max(len(words), 1)
    jargon_set = _DEFAULT_JARGON | {t.lower() for t in (banned_terms or [])}
    repl = replacements or {}

    hits: list[dict] = []
    for term in jargon_set:
        if term in text.lower():
            hits.append(
                {
                    "term": term,
                    "alternative": repl.get(term) or repl.get(term.lower()) or "Use plain language.",
                }
            )

    acronyms = _ACRONYM.findall(text)
    defined = set(re.findall(r"\b([A-Z]{2,})\s*\(", text))
    for acr in acronyms:
        if acr not in defined:
            hits.append(
                {
                    "term": acr,
                    "alternative": "Define acronym on first use.",
                    "undefined_acronym": True,
                }
            )

    for long_w in _LONG.findall(text):
        hits.append({"term": long_w, "alternative": "Consider a simpler word."})

    unique = {h["term"]: h for h in hits}
    hit_list = list(unique.values())[:20]

    density = min(100.0, (len(hit_list) / total) * 400)
    score = max(0.0, 100.0 - density * 2)

    return {
        "score": round(score, 1),
        "density_pct": round((len(hit_list) / total) * 100, 2),
        "flagged_terms": hit_list,
        "metric": "jargon_density",
    }
