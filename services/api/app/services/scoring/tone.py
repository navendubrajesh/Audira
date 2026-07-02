"""Tone alignment scoring (TCA-024, TCA-034)."""

import re

_TONE_LEXICON: dict[str, set[str]] = {
    "professional": {"please", "thank", "regarding", "ensure", "commitment", "support"},
    "empathetic": {"understand", "together", "care", "support", "listen", "appreciate"},
    "urgent": {"immediately", "deadline", "critical", "now", "required", "action"},
    "celebratory": {"congratulations", "celebrate", "achievement", "proud", "success"},
    "formal": {"hereby", "pursuant", "accordingly", "respectfully", "shall"},
}


def score_tone(text: str, target_tone: str = "professional") -> dict:
    sentences = [s.strip() for s in re.split(r"[.!?]+", text) if s.strip()]
    words = set(re.findall(r"\b[a-z]+\b", text.lower()))
    target = _TONE_LEXICON.get(target_tone, _TONE_LEXICON["professional"])

    overlap = words & target
    other_tones = {
        name: len(words & lex)
        for name, lex in _TONE_LEXICON.items()
        if name != target_tone
    }
    dominant_other = max(other_tones.items(), key=lambda x: x[1]) if other_tones else ("", 0)

    score = 60.0 + min(30, len(overlap) * 6) - min(25, dominant_other[1] * 5)
    score = max(0.0, min(100.0, score))

    sentence_flags: list[dict] = []
    for sent in sentences:
        sw = set(re.findall(r"\b[a-z]+\b", sent.lower()))
        if sw & _TONE_LEXICON.get(dominant_other[0], set()) and not (sw & target):
            sentence_flags.append(
                {
                    "sentence": sent[:120],
                    "detected_tone": dominant_other[0],
                    "gap": f"Expected {target_tone}, detected {dominant_other[0]} markers.",
                }
            )

    return {
        "score": round(score, 1),
        "target_tone": target_tone,
        "tone_markers": sorted(overlap),
        "dominant_mismatch": dominant_other[0] if dominant_other[1] > 0 else None,
        "sentence_flags": sentence_flags[:8],
        "metric": "tone_alignment",
    }
