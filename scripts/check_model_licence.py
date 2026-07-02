#!/usr/bin/env python3
"""CI gate — block unlicensed commercial models (TCA-016)."""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BACKLOG = ROOT / "data" / "backlog.json"

BLOCKED_WITHOUT_SIGNOFF = {
    "facebook/tribev2": "CC-BY-NC-4.0 — requires Meta commercial licence or legal_signoff",
}


def main() -> int:
    env = __import__("os").environ.get("ENVIRONMENT", "development")
    if env != "production":
        print("licence-check: skipped (non-production)")
        return 0

    failures: list[str] = []
    for model_id, reason in BLOCKED_WITHOUT_SIGNOFF.items():
        failures.append(f"{model_id}: {reason}")

    if failures:
        print("licence-check FAILED:")
        for f in failures:
            print(f"  - {f}")
        print("Set legal_signoff on model registry or use tribe-v2-stub in non-commercial envs.")
        return 1

    print("licence-check: OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
