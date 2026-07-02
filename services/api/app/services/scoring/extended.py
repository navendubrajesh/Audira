"""Extended scorers for Phase 2/3 stories (TCA-006, TCA-022–032, TCA-047, TCA-062)."""

from __future__ import annotations

import re

# --- TCA-006 language detection (heuristic) ---
_INDIC_HINTS = {
    "hi": {"है", "और", "के", "में", "हम", "आप"},
    "fr": {"le", "la", "les", "des", "nous", "vous"},
    "de": {"der", "die", "das", "und", "wir", "Sie"},
}


def detect_language(text: str) -> dict:
    lower = text.lower()
    words = set(re.findall(r"\b\w+\b", lower))
    scores = {lang: len(words & hints) for lang, hints in _INDIC_HINTS.items()}
    best = max(scores, key=scores.get) if scores else "en"
    if scores.get(best, 0) >= 2:
        detected = best
    elif re.search(r"[\u0900-\u097F]", text):
        detected = "hi"
    else:
        detected = "en"
    return {
        "detected": detected,
        "confidence": "heuristic",
        "supported_analysis": detected == "en",
        "metric": "language_detection",
    }


# --- TCA-022 visual clutter proxy (text density) ---
def score_clutter(text: str) -> dict:
    lines = [ln for ln in text.splitlines() if ln.strip()]
    bullets = sum(1 for ln in lines if ln.strip().startswith(("-", "•", "*")))
    long_lines = sum(1 for ln in lines if len(ln) > 120)
    competing = long_lines + max(0, bullets - 8)
    score = max(0.0, 100.0 - competing * 8)
    return {
        "score": round(score, 1),
        "long_line_count": long_lines,
        "bullet_count": bullets,
        "competing_focal_points": min(competing, 10),
        "metric": "clutter",
    }


# --- TCA-023 emotion spectrum ---
_EMOTION_LEXICON: dict[str, set[str]] = {
    "trust": {"trust", "confident", "secure", "reliable", "commitment"},
    "reassurance": {"support", "together", "care", "help", "stable"},
    "anxiety": {"uncertain", "risk", "concern", "worry", "fear", "anxious"},
    "urgency": {"immediately", "urgent", "deadline", "critical", "now"},
    "celebration": {"congratulations", "celebrate", "proud", "achievement"},
}


def score_emotion(text: str) -> dict:
    words = set(re.findall(r"\b[a-z]+\b", text.lower()))
    intensities = {name: len(words & lex) for name, lex in _EMOTION_LEXICON.items()}
    dominant = max(intensities, key=intensities.get) if intensities else "neutral"
    negative = intensities.get("anxiety", 0)
    positive = intensities.get("trust", 0) + intensities.get("reassurance", 0)
    valence = "positive" if positive >= negative else "negative" if negative > positive else "neutral"
    flags = []
    if negative >= 2 and positive < negative:
        flags.append({"emotion": "anxiety", "note": "Message may trigger concern — consider reassuring framing."})
    score = min(100.0, 50 + positive * 8 - negative * 10)
    return {
        "score": round(max(0.0, score), 1),
        "spectrum": intensities,
        "dominant": dominant,
        "valence": valence,
        "flags": flags,
        "metric": "emotion",
    }


# --- TCA-025 crisis / sensitive framing ---
_ALARM_PHRASES = {
    "layoff": "Use transparent, compassionate language about workforce changes.",
    "termination": "Clarify facts and support resources; avoid alarming tone.",
    "crisis": "Provide clear actions and reassurance; avoid ambiguous statements.",
    "urgent action required": "Explain why and what happens next.",
    "failure": "Reframe constructively; focus on path forward.",
}


def score_crisis_framing(text: str) -> dict:
    lower = text.lower()
    flags = [{"phrase": p, "suggestion": s} for p, s in _ALARM_PHRASES.items() if p in lower]
    ambiguous = bool(re.search(r"\bmay\b.*\bor\b|\beither\b.*\bor\b", lower))
    if ambiguous:
        flags.append({"phrase": "ambiguous choice", "suggestion": "Clarify decision and timeline."})
    penalty = min(50, len(flags) * 12 + (10 if ambiguous else 0))
    return {
        "score": round(max(0.0, 100.0 - penalty), 1),
        "flags": flags,
        "ambiguous_framing": ambiguous,
        "metric": "crisis_framing",
    }


# --- TCA-028 cognitive load ---
def score_cognitive_load(text: str) -> dict:
    paragraphs = [p for p in re.split(r"\n\s*\n", text) if p.strip()]
    sentences = re.split(r"[.!?]+", text)
    avg_sent_len = sum(len(s.split()) for s in sentences if s.strip()) / max(
        1, len([s for s in sentences if s.strip()])
    )
    overload = avg_sent_len > 22 or len(paragraphs) > 0 and any(len(p) > 600 for p in paragraphs)
    score = max(0.0, 100.0 - max(0, avg_sent_len - 15) * 4 - (20 if overload else 0))
    suggestions = []
    if overload:
        suggestions.append("Break long paragraphs into shorter chunks.")
    if avg_sent_len > 20:
        suggestions.append("Shorten sentences for easier scanning.")
    return {
        "score": round(score, 1),
        "avg_sentence_words": round(avg_sent_len, 1),
        "overload": overload,
        "chunking_suggestions": suggestions,
        "metric": "cognitive_load",
    }


# --- TCA-030 key message findability ---
def score_key_message(text: str, key_message: str | None = None) -> dict:
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    lead = lines[0] if lines else text[:200]
    stated = key_message or _extract_key_message(text)
    in_lead = stated.lower() in lead.lower() if stated else False
    buried = stated and stated.lower() in text.lower() and not in_lead
    score = 85.0 if in_lead else (55.0 if buried else 40.0)
    return {
        "score": round(score, 1),
        "stated_key_message": stated,
        "in_lead": in_lead,
        "buried": buried,
        "suggestion": None if in_lead else "Move the core message to the opening sentence.",
        "metric": "key_message",
    }


def _extract_key_message(text: str) -> str | None:
    m = re.search(r"(?:key message|main point|bottom line)[:\s]+(.+?)(?:\.|$)", text, re.I)
    return m.group(1).strip() if m else None


# --- TCA-032 memorability ---
def score_memorability(text: str) -> dict:
    words = re.findall(r"\b\w+\b", text.lower())
    unique_ratio = len(set(words)) / max(len(words), 1)
    has_concrete = bool(re.search(r"\b\d+%|\b\d+\b|\b(monday|tuesday|q[1-4])\b", text, re.I))
    repetition = len(words) - len(set(words))
    score = 50 + unique_ratio * 30 + (15 if has_concrete else 0) - min(20, repetition)
    return {
        "score": round(max(0.0, min(100.0, score)), 1),
        "has_concrete_facts": has_concrete,
        "weak_retention": score < 55,
        "metric": "memorability",
    }


# --- TCA-047 subject line / hook ---
def score_subject_line(text: str, channel: str | None = None) -> dict:
    first_line = text.strip().split("\n")[0][:120]
    length = len(first_line)
    has_hook = bool(re.search(r"\b(how|why|what|new|important|update)\b", first_line, re.I))
    too_long = length > 60 and (channel or "") in ("email", "slack", "")
    score = 70 + (10 if has_hook else 0) - (15 if too_long else 0) - (10 if length < 10 else 0)
    variants = [
        first_line,
        f"Update: {first_line[:50]}",
        f"Important — {first_line[:45]}",
    ]
    return {
        "score": round(max(0.0, min(100.0, score)), 1),
        "subject_line": first_line,
        "variants": variants[:3],
        "predicted_open": "medium" if score >= 65 else "low",
        "metric": "subject_line",
    }


# --- TCA-021 early attention (above-the-fold proxy) ---
def score_early_attention(text: str) -> dict:
    fold = text[:280]
    words = fold.split()
    key_terms = {"update", "important", "announce", "team", "change", "launch"}
    hits = sum(1 for w in words if w.lower() in key_terms)
    score = min(100.0, 45 + hits * 12 + min(20, len(words)))
    outside = not any(t in fold.lower() for t in ("trust", "commit", "support", "thank"))
    return {
        "score": round(score, 1),
        "above_fold_chars": len(fold),
        "key_message_in_fold": hits > 0,
        "reposition_recommended": outside and score < 60,
        "metric": "early_attention",
    }


# --- TCA-062 explainability drivers ---
def explain_drivers(metrics: dict, composite: float) -> dict:
    drivers: list[dict] = []
    for name, block in metrics.items():
        if not isinstance(block, dict) or "score" not in block:
            continue
        score = float(block["score"])
        impact = "positive" if score >= 70 else "negative" if score < 55 else "neutral"
        drivers.append({"metric": name, "score": score, "impact": impact})
    drivers.sort(key=lambda d: d["score"])
    weaknesses = [d for d in drivers if d["impact"] == "negative"][:3]
    strengths = [d for d in drivers if d["impact"] == "positive"][-3:]
    return {
        "composite_score": composite,
        "top_strengths": strengths,
        "top_weaknesses": weaknesses,
        "summary": _plain_summary(strengths, weaknesses, composite),
    }


def _plain_summary(strengths: list, weaknesses: list, composite: float) -> str:
    parts = [f"Overall effectiveness is {composite}/100."]
    if strengths:
        parts.append(f"Strongest areas: {', '.join(s['metric'] for s in strengths)}.")
    if weaknesses:
        parts.append(f"Focus improvements on: {', '.join(w['metric'] for w in weaknesses)}.")
    return " ".join(parts)
