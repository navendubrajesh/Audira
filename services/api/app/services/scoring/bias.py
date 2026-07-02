"""Bias & fairness checks (TCA-064)."""

_STEREOTYPE_TERMS = {
    "young and energetic": "Age-biased phrasing — focus on skills instead.",
    "digital native": "Generational stereotype — avoid.",
    "man hours": "Gendered term — use person-hours or work hours.",
    "chairman": "Use chair or chairperson.",
}


def score_fairness(text: str) -> dict:
    lower = text.lower()
    flags = [
        {"phrase": phrase, "suggestion": suggestion}
        for phrase, suggestion in _STEREOTYPE_TERMS.items()
        if phrase in lower
    ]
    score = max(0.0, 100.0 - len(flags) * 15)
    return {
        "score": round(score, 1),
        "flags": flags,
        "metric": "fairness",
        "status": "pass" if score >= 70 else "review",
    }
