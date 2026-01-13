"""Helpers for alternate output formats and auto selection."""

from __future__ import annotations

import json
from typing import Any, Iterable

from encoder import encode as encode_toon
from tokens import count_tokens


def _is_primitive(value: Any) -> bool:
    return isinstance(value, (str, int, float, bool)) or value is None


def _is_tabular(values: list[Any]) -> bool:
    if not values or not all(isinstance(v, dict) for v in values):
        return False
    keys = list(values[0].keys())
    if not keys:
        return False
    for row in values:
        if list(row.keys()) != keys:
            return False
        if not all(_is_primitive(v) for v in row.values()):
            return False
    return True


def _scalar_to_yaml(value: Any) -> str:
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (int, float)):
        return str(value)
    text = str(value)
    if text == "" or any(ch.isspace() or ch in {":", "-", "#", "\""} for ch in text):
        return f"\"{text.replace('\\', '\\\\').replace('"', '\\"')}\""
    return text


def to_yaml_simple(value: Any, indent: int = 0) -> str:
    pad = " " * indent
    if isinstance(value, dict):
        lines = []
        for k, v in value.items():
            if isinstance(v, (dict, list)):
                lines.append(f"{pad}{k}:")
                lines.append(to_yaml_simple(v, indent + 2))
            else:
                lines.append(f"{pad}{k}: {_scalar_to_yaml(v)}")
        return "\n".join(lines)
    if isinstance(value, list):
        lines = []
        for item in value:
            if isinstance(item, (dict, list)):
                lines.append(f"{pad}-")
                lines.append(to_yaml_simple(item, indent + 2))
            else:
                lines.append(f"{pad}- {_scalar_to_yaml(item)}")
        return "\n".join(lines)
    return f"{pad}{_scalar_to_yaml(value)}"


def to_csv(value: Any) -> str | None:
    if not isinstance(value, list) or not _is_tabular(value):
        return None
    keys = list(value[0].keys())
    lines = [",".join(str(k) for k in keys)]
    for row in value:
        lines.append(",".join(str(row.get(k, "")) for k in keys))
    return "\n".join(lines)


def to_json_compact(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"))


def to_json_pretty(value: Any, indent: int = 2) -> str:
    return json.dumps(value, ensure_ascii=False, indent=indent)


def encode_as(value: Any, fmt: str) -> str:
    fmt = fmt.lower()
    if fmt == "toon":
        return encode_toon(value)
    if fmt == "json":
        return to_json_compact(value)
    if fmt == "json_pretty":
        return to_json_pretty(value)
    if fmt == "yaml":
        return to_yaml_simple(value)
    if fmt == "csv":
        csv_text = to_csv(value)
        if csv_text is None:
            raise ValueError("CSV requires a list of uniform dict rows")
        return csv_text
    raise ValueError(f"Unknown format: {fmt}")


def _candidate_formats(value: Any, candidates: Iterable[str] | None) -> list[str]:
    if candidates is None:
        candidates = ("toon", "json", "yaml")
    formats = [fmt.lower() for fmt in candidates]
    if "csv" not in formats:
        return formats
    if to_csv(value) is None:
        return [fmt for fmt in formats if fmt != "csv"]
    return formats


def encode_best(value: Any, candidates: Iterable[str] | None = None, metric: str = "tokens") -> dict:
    formats = _candidate_formats(value, candidates)
    best = None
    for fmt in formats:
        text = encode_as(value, fmt)
        score = count_tokens(text) if metric == "tokens" else len(text)
        if best is None or score < best["score"]:
            best = {"format": fmt, "text": text, "score": score, "chars": len(text)}
    if best is None:
        raise ValueError("No valid formats available")
    return {
        "format": best["format"],
        "text": best["text"],
        "tokens": best["score"],
        "chars": best["chars"],
    }
