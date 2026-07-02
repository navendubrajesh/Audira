"""Readability scoring (TCA-027)."""

import re

_WORD = re.compile(r"[A-Za-z']+")
_PASSIVE = re.compile(
    r"\b(am|is|are|was|were|be|been|being)\s+\w+ed\b|\b(am|is|are|was|were)\s+\w+\s+by\b",
    re.IGNORECASE,
)


def score_readability(text: str, *, target_grade: float = 10.0) -> dict:
    words = _WORD.findall(text)
    sentences_raw = [s.strip() for s in re.split(r"[.!?]+", text) if s.strip()]
    sentences = max(1, len(sentences_raw))
    syllables = sum(max(1, _syllable_count(w)) for w in words) or 1
    word_count = max(len(words), 1)

    fre = 206.835 - 1.015 * (word_count / sentences) - 84.6 * (syllables / word_count)
    score = max(0.0, min(100.0, fre))
    grade = 0.39 * (word_count / sentences) + 11.8 * (syllables / word_count) - 15.59

    long_sentences = [s[:100] for s in sentences_raw if len(s.split()) > 25]
    passive = [s[:100] for s in sentences_raw if _PASSIVE.search(s)]
    ambiguous = [s[:100] for s in sentences_raw if re.search(r"\b(may|might|possibly|unclear)\b", s, re.I)]

    flags: list[dict] = []
    for s in long_sentences[:5]:
        flags.append({"type": "long_sentence", "text": s, "suggestion": "Split into shorter sentences."})
    for s in passive[:5]:
        flags.append({"type": "passive_voice", "text": s, "suggestion": "Prefer active voice."})

    meets_target = grade <= target_grade

    return {
        "score": round(score, 1),
        "grade_level": round(max(0, grade), 1),
        "target_grade": target_grade,
        "meets_target": meets_target,
        "word_count": word_count,
        "sentence_count": sentences,
        "flags": flags,
        "ambiguous_phrases": ambiguous[:5],
        "metric": "flesch_reading_ease",
    }


def _syllable_count(word: str) -> int:
    word = word.lower()
    if len(word) <= 3:
        return 1
    word = re.sub(r"e$", "", word)
    groups = re.findall(r"[aeiouy]+", word)
    return max(1, len(groups))
