"""Readability scoring (TCA-027)."""

import re

_WORD = re.compile(r"[A-Za-z']+")


def score_readability(text: str) -> dict:
    words = _WORD.findall(text)
    sentences = max(1, len(re.split(r"[.!?]+", text)) - 1)
    syllables = sum(max(1, _syllable_count(w)) for w in words) or 1
    word_count = max(len(words), 1)

    # Flesch Reading Ease
    fre = 206.835 - 1.015 * (word_count / sentences) - 84.6 * (syllables / word_count)
    score = max(0.0, min(100.0, fre))

    grade = 0.39 * (word_count / sentences) + 11.8 * (syllables / word_count) - 15.59

    return {
        "score": round(score, 1),
        "grade_level": round(max(0, grade), 1),
        "word_count": word_count,
        "sentence_count": sentences,
        "metric": "flesch_reading_ease",
    }


def _syllable_count(word: str) -> int:
    word = word.lower()
    if len(word) <= 3:
        return 1
    word = re.sub(r"e$", "", word)
    groups = re.findall(r"[aeiouy]+", word)
    return max(1, len(groups))
