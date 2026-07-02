"""Inclusive language checks (TCA-059)."""

_DEFAULT_FLAGS = {
    "guys": "Consider gender-neutral alternatives (e.g. team, everyone).",
    "manpower": "Use workforce or staffing.",
    "sanity check": "Use review or validation.",
    "blacklist": "Use blocklist or deny list.",
    "whitelist": "Use allowlist or approved list.",
    "master": "Avoid master/slave terminology in technical comms.",
    "slave": "Avoid master/slave terminology in technical comms.",
}


def score_inclusive_language(
    text: str,
    custom_rules: list[dict] | None = None,
    region: str | None = None,
) -> dict:
    lower = text.lower()
    flags: list[dict] = []

    for term, suggestion in _DEFAULT_FLAGS.items():
        if term in lower:
            flags.append({"term": term, "suggestion": suggestion})

    for rule in custom_rules or []:
        pattern = (rule.get("pattern") or "").lower()
        if pattern and pattern in lower:
            flags.append(
                {
                    "term": pattern,
                    "suggestion": rule.get("replacement") or rule.get("metadata", {}).get("note", ""),
                }
            )

    if region and region.upper() in {"EU", "UK"}:
        extra = {"chairman": "Use chair or chairperson."}
        for term, suggestion in extra.items():
            if term in lower and not any(f["term"] == term for f in flags):
                flags.append({"term": term, "suggestion": suggestion, "region": region})

    penalty = min(40, len(flags) * 8)
    score = max(0.0, 100.0 - penalty)

    return {
        "score": round(score, 1),
        "flags": flags,
        "flag_count": len(flags),
        "metric": "inclusive_language",
    }
