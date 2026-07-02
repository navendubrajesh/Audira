"""PII detection and redaction (TCA-061, TCA-071)."""

import re

_PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    ("email", re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")),
    ("phone", re.compile(r"\b(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b")),
    ("ssn", re.compile(r"\b\d{3}-\d{2}-\d{4}\b")),
    ("credit_card", re.compile(r"\b(?:\d[ -]*?){13,16}\b")),
]


def detect_pii(text: str) -> list[dict]:
    findings: list[dict] = []
    for kind, pattern in _PATTERNS:
        for match in pattern.finditer(text):
            findings.append(
                {
                    "type": kind,
                    "start": match.start(),
                    "end": match.end(),
                    "snippet": match.group()[:4] + "***",
                }
            )
    return findings


def redact_pii(text: str) -> tuple[str, list[dict]]:
    findings = detect_pii(text)
    redacted = text
    for item in sorted(findings, key=lambda x: x["start"], reverse=True):
        redacted = redacted[: item["start"]] + f"[REDACTED_{item['type'].upper()}]" + redacted[item["end"] :]
    return redacted, findings
