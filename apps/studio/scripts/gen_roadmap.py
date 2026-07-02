#!/usr/bin/env python3
"""Generate traceability JSON and ROADMAP.md from backlog-data.json."""

import json
import re
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
data = json.loads((ROOT / "src/mock/backlog-data.json").read_text(encoding="utf-8"))


def epic_code(epic: str) -> str:
    match = re.match(r"(E\d+)", str(epic))
    return match.group(1) if match else "E99"


def infer_verticals(story: dict) -> list[str]:
    text = " ".join(
        str(story.get(k, ""))
        for k in ("Epic", "Functionality", "User Story", "Platform")
    ).lower()
    code = epic_code(story["Epic"])
    verts: set[str] = set()
    if code in ("E19", "E20", "E21", "E22"):
        verts.add("linkedin")
    elif code in ("E14", "E09"):
        verts.add("analytics")
    elif code in ("E13", "E15", "E16", "E17", "E08"):
        verts.add("governance")
    elif code == "E02":
        verts.add("assets")
    elif code in ("E04", "E11"):
        verts.add("social")
    elif code in ("E06", "E07"):
        verts.update(["linkedin", "blog", "placement", "social"])
    elif code == "E05":
        verts.update(["social", "linkedin"])
    else:
        verts.add("home")
    if "linkedin" in text:
        verts.add("linkedin")
    if any(k in text for k in ("job", "recruit", "placement", "naukri")):
        verts.add("placement")
    if any(k in text for k in ("blog", "seo", "wordpress", "medium")):
        verts.add("blog")
    return sorted(verts)


def infer_screen(story: dict) -> str:
    code = epic_code(story["Epic"])
    func = story["Functionality"].lower()
    plat = story["Platform"]
    if code.startswith("E19") or code.startswith("E20") or code.startswith("E21"):
        if "workspace" in func or "split" in func:
            return "linkedin/AnalyzerWorkspace"
        if "persona" in func:
            return "linkedin/PersonaPicker"
        if "prompter" in func or "anti-generic" in func:
            return "linkedin/AntiGenericWizard"
        if "ingestion" in func or "multimodal" in func:
            return "linkedin/MultimodalDropZone"
        if "toolbar" in func or "markdown" in func:
            return "linkedin/DraftEditor"
        return "linkedin/AnalyzeTab"
    if code == "E22":
        return "linkedin/EngagementHelper"
    if "Admin" in plat or code in ("E13", "E15", "E16", "E17"):
        return "governance/GovernanceModule"
    if code == "E14":
        return "analytics/InsightsConsole"
    if code == "E02":
        return "assets/AssetLibrary"
    if code in ("E04", "E11"):
        return "social/VerticalWorkspace"
    if code == "E10":
        return "shared/RewriteAssist"
    return "home/CommandCenter"


def impl_type(story: dict) -> str:
    phase = story.get("Phase", "")
    pri = story.get("Priority", "")
    sig = story["ID"] in (
        "TCA-083",
        "TCA-091",
        "TCA-077",
        "TCA-078",
        "TCA-079",
        "TCA-087",
    )
    if sig:
        return "Real (placeholder logic)"
    if "Phase 1" in phase and pri == "Must":
        return "Placeholder (MVP screen)"
    if "Phase 3" in phase:
        return "Stub (coming soon)"
    return "Placeholder"


rows = []
for s in data["backlog"]:
    rows.append(
        {
            "id": s["ID"],
            "epic": epic_code(s["Epic"]),
            "epic_name": s["Epic"],
            "verticals": infer_verticals(s),
            "screen": infer_screen(s),
            "impl": impl_type(s),
            "status": s.get("Status", "To Do"),
            "phase": s.get("Phase", ""),
            "priority": s.get("Priority", ""),
            "functionality": s["Functionality"],
        }
    )

(ROOT / "src/mock/traceability.json").write_text(
    json.dumps(rows, indent=2), encoding="utf-8"
)

counts = Counter(r["status"] for r in rows)
lines = [
    "# Audira Studio — Product Roadmap",
    "",
    "Generated from backlog traceability (`TCA-001`…`TCA-092`).",
    "",
    "## Summary",
    "",
    f"- **Done:** {counts.get('Done', 0)} | **Partial:** {counts.get('Partial', 0)} | **To Do:** {counts.get('To Do', 0)}",
    "",
    "## Traceability",
    "",
    "| Story ID | Epic | Vertical(s) | Screen / Component | Implementation | Status |",
    "|---|---|---|---|---|---|",
]
for r in rows:
    verts = ", ".join(r["verticals"])
    lines.append(
        f"| {r['id']} | {r['epic']} | {verts} | `{r['screen']}` | {r['impl']} | {r['status']} |"
    )

(ROOT / "ROADMAP.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
print(f"Generated traceability + ROADMAP for {len(rows)} stories")
