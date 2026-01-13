"""Format detection utilities."""

from __future__ import annotations

import json


def detect_format(text: str) -> str:
    """Detect input format among json, csv, yaml, toon, or unknown."""
    stripped = text.strip()
    if stripped == "":
        return "unknown"
    try:
        json.loads(text)
        return "json"
    except Exception:
        pass
    lines = [line for line in text.splitlines() if line.strip() != ""]
    if not lines:
        return "unknown"
    first = stripped[0]
    if first == "^" or "|" in stripped:
        return "toon"
    if first in {"{", "["}:
        return "toon"
    if any(":" in line for line in lines):
        return "yaml"
    comma_lines = [line for line in lines if "," in line]
    if len(comma_lines) >= 2 and not any(":" in line for line in lines):
        return "csv"
    return "unknown"
