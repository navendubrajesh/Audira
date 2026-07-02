"""Predicted attention heatmap from text layout (TCA-020)."""

from __future__ import annotations

import re


def generate_attention_heatmap(text: str, *, width: int = 12, height: int = 8) -> dict:
    """
    Produce a saliency grid and reading-order focus points from text structure.
    Full image/TRI BE saliency requires GPU image modality — this is the text-layout proxy.
    """
    words = re.findall(r"\b\w+\b", text)
    if not words:
        return {"grid": [], "focus_order": [], "format": "grid", "export_svg": ""}

    importance = _word_weights(words)
    cells = width * height
    chunk = max(1, len(importance) // cells)
    grid: list[list[float]] = []
    idx = 0
    for _row in range(height):
        row: list[float] = []
        for _col in range(width):
            slice_ = importance[idx : idx + chunk] or [0.3]
            row.append(round(sum(slice_) / len(slice_), 3))
            idx += chunk
        grid.append(row)

    sentences = [s.strip() for s in re.split(r"[.!?]+", text) if s.strip()]
    focus_order = [
        {"rank": i + 1, "text": s[:120], "weight": round(1.0 - (i * 0.08), 2)}
        for i, s in enumerate(sentences[:8])
    ]

    return {
        "grid": grid,
        "width": width,
        "height": height,
        "focus_order": focus_order,
        "format": "grid",
        "export_svg": _grid_to_svg(grid),
        "note": "Text-layout proxy; connect TRIBE image modality for pixel saliency.",
    }


def _word_weights(words: list[str]) -> list[float]:
    stop = {"the", "a", "an", "and", "or", "to", "of", "in", "for", "is", "are", "we", "you"}
    weights: list[float] = []
    for i, w in enumerate(words):
        base = 0.35
        if w.lower() not in stop:
            base += 0.25
        if w.isupper() and len(w) > 2:
            base += 0.2
        if i < 20:
            base += 0.15
        weights.append(min(1.0, base))
    return weights


def _grid_to_svg(grid: list[list[float]]) -> str:
    if not grid:
        return ""
    cell = 24
    h = len(grid)
    w = len(grid[0])
    rects: list[str] = []
    for y, row in enumerate(grid):
        for x, val in enumerate(row):
            shade = int(255 - val * 180)
            rects.append(
                f'<rect x="{x * cell}" y="{y * cell}" width="{cell}" height="{cell}" '
                f'fill="rgb(255,{shade},{shade})"/>'
            )
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w * cell}" height="{h * cell}">'
        + "".join(rects)
        + "</svg>"
    )
