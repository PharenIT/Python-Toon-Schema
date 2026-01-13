"""TOON encoder implementation.

Encodes Python values into a compact, deterministic format intended for LLM prompts.
"""

from __future__ import annotations

import math
import re
from datetime import date, datetime
from decimal import Decimal
from typing import Any

_RESERVED_TOKENS = {"null", "true", "false"}

_NUMERIC_RE = re.compile(r"^[+-]?(?:\d+\.?\d*|\d*\.\d+)(?:[eE][+-]?\d+)?$")

_DELIMITERS = {"{", "}", "[", "]", "|", ",", "^", "="}


def normalize_value(value: Any) -> Any:
    """Normalize values for deterministic encoding.

    - datetime/date -> ISO 8601 strings
    - Decimal -> float
    - NaN/Inf -> None
    - -0.0 -> 0.0
    """
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    if isinstance(value, Decimal):
        return float(value)
    if isinstance(value, float):
        if math.isnan(value) or math.isinf(value):
            return None
        if value == 0.0:
            return 0.0
        return value
    if isinstance(value, dict):
        return {k: normalize_value(v) for k, v in value.items()}
    if isinstance(value, list):
        return [normalize_value(v) for v in value]
    return value


def _needs_quotes(text: str) -> bool:
    if text == "":
        return True
    lowered = text.lower()
    if lowered in _RESERVED_TOKENS:
        return True
    if _NUMERIC_RE.match(text):
        return True
    for ch in text:
        if ch.isspace() or ch in _DELIMITERS:
            return True
    return False


def _escape_string(text: str) -> str:
    return (
        text.replace("\\", "\\\\")
        .replace("\"", "\\\"")
        .replace("\n", "\\n")
        .replace("\r", "\\r")
        .replace("\t", "\\t")
    )


def _encode_string(text: str) -> str:
    if _needs_quotes(text):
        return f"\"{_escape_string(text)}\""
    return text


def _encode_primitive(value: Any) -> str:
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, int):
        return str(value)
    if isinstance(value, float):
        if value == 0.0:
            return "0"
        return format(value, "g")
    if isinstance(value, str):
        return _encode_string(value)
    return _encode_string(str(value))


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


def _encode_table(values: list[dict[Any, Any]]) -> str:
    keys = list(values[0].keys())
    header = ",".join(_encode_string(str(k)) for k in keys)
    rows = []
    for row in values:
        row_part = ",".join(_encode_primitive(row[k]) for k in keys)
        rows.append(row_part)
    return f"^csv[{header}|{'|'.join(rows)}]"


def _encode_list(values: list[Any]) -> str:
    if _is_tabular(values):
        return _encode_table(values)
    if not values:
        return "[]"
    return f"[{'|'.join(_encode(v) for v in values)}]"


def _encode_dict(values: dict[Any, Any]) -> str:
    if not values:
        return "{}"
    keys = list(values.keys())
    key_part = ",".join(_encode_string(str(k)) for k in keys)
    value_part = "|".join(_encode(values[k]) for k in keys)
    return f"{{{key_part}|{value_part}}}"


def _encode(value: Any) -> str:
    if isinstance(value, dict):
        return _encode_dict(value)
    if isinstance(value, list):
        return _encode_list(value)
    return _encode_primitive(value)


def encode(value: Any, options: dict | None = None) -> str:
    """Encode a Python value into TOON.

    Args:
        value: Python value to encode.
        options: Reserved for future compatibility.

    Returns:
        TOON string.
    """
    if options:
        mode = options.get("mode", "toon")
        if mode == "auto":
            # Local import to avoid circular dependency on formats -> encoder.
            from formats import encode_best

            candidates = options.get("candidates")
            metric = options.get("metric", "tokens")
            best = encode_best(value, candidates=candidates, metric=metric)
            return best["text"]
        if mode not in {"toon", "hybrid"}:
            raise ValueError(f"Unknown encode mode: {mode}")
    normalized = normalize_value(value)
    return _encode(normalized)
