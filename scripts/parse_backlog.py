#!/usr/bin/env python3
"""Parse Resonode competitive backlog Excel and compute build order."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_XLSX = ROOT / "Enterprise_Comms_NeuroAnalyzer_Competitive_Backlog_1.xlsx"
OUTPUT_JSON = ROOT / "data" / "backlog.json"
OUTPUT_ORDER = ROOT / "docs" / "BUILD_ORDER.md"

# Logical dependencies: story cannot start until all deps are Done.
DEPENDENCIES: dict[str, list[str]] = {
    "TCA-013": ["TCA-014", "TCA-016"],
    "TCA-015": ["TCA-013", "TCA-014"],
    "TCA-020": ["TCA-007", "TCA-013", "TCA-015"],
    "TCA-024": ["TCA-002"],
    "TCA-027": ["TCA-008"],
    "TCA-029": ["TCA-005"],
    "TCA-034": ["TCA-002", "TCA-005"],
    "TCA-038": ["TCA-015", "TCA-027", "TCA-034"],
    "TCA-048": ["TCA-038", "TCA-067"],
    "TCA-059": ["TCA-005"],
    "TCA-061": ["TCA-067", "TCA-068"],
    "TCA-063": ["TCA-015"],
    "TCA-070": ["TCA-068"],
    "TCA-072": ["TCA-067"],
    "TCA-075": ["TCA-072"],
}

# Epic sequencing within the same sort bucket (lower = earlier).
EPIC_ORDER: dict[str, int] = {
    "E18": 0,
    "E17": 1,
    "E01": 2,
    "E02": 3,
    "E03": 4,
    "E04": 5,
    "E05": 6,
    "E06": 7,
    "E07": 8,
    "E08": 9,
    "E09": 10,
    "E15": 11,
    "E16": 12,
    "E12": 13,
    "E13": 14,
    "E14": 15,
    "E10": 16,
    "E11": 17,
}

GUARDRAIL_STORY_IDS = {"TCA-037", "TCA-044", "TCA-060"}

PHASE_ORDER = {"Phase 1 (Pilot/MVP)": 1, "Phase 2 (Scale)": 2, "Phase 3 (Advanced)": 3}
TYPE_ORDER = {"Foundation": 0, "Parity": 1, "Differentiator": 2}
PRIORITY_ORDER = {"Must": 0, "Should": 1, "Could": 2}


def norm_epic(epic: str) -> str:
    match = re.match(r"(E\d+)", str(epic))
    return match.group(1) if match else "E99"


def story_record(row: pd.Series) -> dict[str, Any]:
    return {
        "id": row["ID"],
        "prd_ref": row["PRD Ref"],
        "platform": row["Platform"],
        "epic": row["Epic"],
        "epic_code": norm_epic(row["Epic"]),
        "functionality": row["Functionality"],
        "user_story": row["User Story"],
        "role": row["Role"],
        "type": row["Type"],
        "priority": row["Priority"],
        "benchmark_source": row["Benchmark Source"],
        "acceptance_criteria": row["Acceptance Criteria"],
        "phase": row["Phase"],
        "phase_num": PHASE_ORDER.get(str(row["Phase"]), 99),
        "market_coverage": row["Market Coverage"],
        "is_guardrail": row["ID"] in GUARDRAIL_STORY_IDS,
        "dependencies": DEPENDENCIES.get(row["ID"], []),
        "status": "pending",
    }


def sort_key(story: dict[str, Any]) -> tuple:
    return (
        story["phase_num"],
        TYPE_ORDER.get(story["type"], 9),
        PRIORITY_ORDER.get(story["priority"], 9),
        EPIC_ORDER.get(story["epic_code"], 99),
        story["id"],
    )


def topological_sort(stories: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_id = {s["id"]: s for s in stories}
    remaining = {s["id"] for s in stories}
    done: set[str] = set()
    ordered: list[dict[str, Any]] = []

    base_sorted = sorted(stories, key=sort_key)

    while remaining:
        candidates = [
            sid
            for sid in remaining
            if all(dep in done for dep in by_id[sid]["dependencies"])
        ]
        if not candidates:
            # Cycle or missing dep — fall back to base order for leftovers.
            candidates = sorted(remaining, key=lambda sid: sort_key(by_id[sid]))

        next_id = min(candidates, key=lambda sid: sort_key(by_id[sid]))
        ordered.append(by_id[next_id])
        done.add(next_id)
        remaining.remove(next_id)

    return ordered


def render_build_order_md(stories: list[dict[str, Any]], source: Path) -> str:
    lines = [
        "# Resonode — Computed Build Order",
        "",
        f"**Source:** `{source.name}`  ",
        f"**Stories:** {len(stories)}  ",
        "**Ordering:** phase → type (Foundation → Parity → Differentiator) → priority (Must → Should → Could) → epic sequence → dependencies",
        "",
        "## Phase 0 bootstrap (pre-backlog)",
        "",
        "Scaffold monorepo, design system, Docker/CI, docs ledger — **no TCA story started yet.**",
        "",
        "## Story queue",
        "",
        "| # | ID | Phase | Type | Priority | Epic | Platform | Guardrail | Status |",
        "|---:|---|---|---|---|---|---|---|---|",
    ]
    for idx, s in enumerate(stories, start=1):
        phase_short = f"P{s['phase_num']}"
        guard = "yes" if s["is_guardrail"] else ""
        epic_short = s["epic_code"]
        lines.append(
            f"| {idx} | {s['id']} | {phase_short} | {s['type']} | {s['priority']} "
            f"| {epic_short} | {s['platform'][:30]} | {guard} | {s['status']} |"
        )

    phase1 = [s for s in stories if s["phase_num"] == 1]
    lines.extend(
        [
            "",
            "## Phase 1 MVP summary",
            "",
            f"- **Count:** {len(phase1)} stories",
            f"- **First story after bootstrap:** `{phase1[0]['id']}` — {phase1[0]['functionality']}",
            f"- **Guardrail stories (stop & review before implementing):** {', '.join(sorted(GUARDRAIL_STORY_IDS))}",
            "",
            "## Guardrail rule",
            "",
            "When the queue reaches a guardrail story (TCA-037, TCA-044, TCA-060), **pause the loop**, "
            "complete prior stories, and obtain explicit go-ahead before implementation.",
        ]
    )
    return "\n".join(lines) + "\n"


def parse_backlog(xlsx_path: Path) -> list[dict[str, Any]]:
    df = pd.read_excel(xlsx_path, sheet_name="Backlog")
    stories = [story_record(row) for _, row in df.iterrows()]
    return topological_sort(stories)


def main() -> None:
    parser = argparse.ArgumentParser(description="Parse Resonode backlog Excel")
    parser.add_argument("--input", type=Path, default=DEFAULT_XLSX)
    parser.add_argument("--json", type=Path, default=OUTPUT_JSON)
    parser.add_argument("--order-md", type=Path, default=OUTPUT_ORDER)
    args = parser.parse_args()

    if not args.input.exists():
        raise SystemExit(f"Backlog file not found: {args.input}")

    stories = parse_backlog(args.input)
    args.json.parent.mkdir(parents=True, exist_ok=True)
    args.order_md.parent.mkdir(parents=True, exist_ok=True)

    payload = {
        "source_file": args.input.name,
        "story_count": len(stories),
        "guardrail_ids": sorted(GUARDRAIL_STORY_IDS),
        "stories": stories,
    }
    args.json.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    args.order_md.write_text(render_build_order_md(stories, args.input), encoding="utf-8")

    print(f"Wrote {len(stories)} stories -> {args.json}")
    print(f"Wrote build order -> {args.order_md}")
    print(f"First story: {stories[0]['id']}")


if __name__ == "__main__":
    main()
