"""TOON decoder implementation."""

from __future__ import annotations

import csv
import json
import re
from typing import Any

from detect import detect_format

_INT_RE = re.compile(r"^[+-]?\d+$")
_FLOAT_RE = re.compile(r"^[+-]?(?:\d+\.?\d*|\d*\.\d+)(?:[eE][+-]?\d+)?$")

_STOP_CHARS = {"{", "}", "[", "]", "|", ",", "^"}


def _unescape_string(text: str) -> str:
    result = []
    i = 0
    while i < len(text):
        ch = text[i]
        if ch != "\\":
            result.append(ch)
            i += 1
            continue
        i += 1
        if i >= len(text):
            break
        esc = text[i]
        if esc == "n":
            result.append("\n")
        elif esc == "r":
            result.append("\r")
        elif esc == "t":
            result.append("\t")
        else:
            result.append(esc)
        i += 1
    return "".join(result)


def _parse_primitive(token: str) -> Any:
    token = token.strip()
    if token == "":
        return ""
    if token.startswith("\"") and token.endswith("\""):
        return _unescape_string(token[1:-1])
    lowered = token.lower()
    if lowered == "null":
        return None
    if lowered == "true":
        return True
    if lowered == "false":
        return False
    if _INT_RE.match(token):
        try:
            return int(token)
        except ValueError:
            return token
    if _FLOAT_RE.match(token):
        try:
            return float(token)
        except ValueError:
            return token
    return token


def _skip_ws(text: str, idx: int) -> int:
    while idx < len(text) and text[idx].isspace():
        idx += 1
    return idx


def _parse_quoted(text: str, idx: int) -> tuple[str, int]:
    idx += 1
    start = idx
    buf = []
    while idx < len(text):
        ch = text[idx]
        if ch == "\\" and idx + 1 < len(text):
            buf.append(text[idx])
            buf.append(text[idx + 1])
            idx += 2
            continue
        if ch == "\"":
            raw = "".join(buf) if buf else text[start:idx]
            return _unescape_string(raw), idx + 1
        buf.append(ch)
        idx += 1
    return _unescape_string(text[start:idx]), idx


def _parse_token(text: str, idx: int, stop_chars: set[str]) -> tuple[str, int]:
    idx = _skip_ws(text, idx)
    if idx >= len(text):
        return "", idx
    if text[idx] == "\"":
        value, idx = _parse_quoted(text, idx)
        return value, idx
    start = idx
    while idx < len(text):
        ch = text[idx]
        if ch.isspace() or ch in stop_chars:
            break
        idx += 1
    return text[start:idx], idx


def _split_csv_segment(segment: str) -> list[str]:
    tokens = []
    buf = []
    in_quotes = False
    i = 0
    while i < len(segment):
        ch = segment[i]
        if ch == "\\" and i + 1 < len(segment):
            buf.append(segment[i])
            buf.append(segment[i + 1])
            i += 2
            continue
        if ch == "\"":
            in_quotes = not in_quotes
            buf.append(ch)
            i += 1
            continue
        if ch == "," and not in_quotes:
            tokens.append("".join(buf))
            buf = []
            i += 1
            continue
        buf.append(ch)
        i += 1
    tokens.append("".join(buf))
    return tokens


def _read_segment(text: str, idx: int) -> tuple[str, int]:
    buf = []
    in_quotes = False
    while idx < len(text):
        ch = text[idx]
        if ch == "\\" and idx + 1 < len(text):
            buf.append(text[idx])
            buf.append(text[idx + 1])
            idx += 2
            continue
        if ch == "\"":
            in_quotes = not in_quotes
            buf.append(ch)
            idx += 1
            continue
        if not in_quotes and ch in {"|", "]"}:
            break
        buf.append(ch)
        idx += 1
    return "".join(buf), idx


def _parse_value(text: str, idx: int) -> tuple[Any, int]:
    idx = _skip_ws(text, idx)
    if idx >= len(text):
        return None, idx
    ch = text[idx]
    if ch == "{":
        return _parse_object(text, idx)
    if ch == "[":
        return _parse_array(text, idx)
    if ch == "^":
        return _parse_table(text, idx)
    if ch == "\"":
        value, idx = _parse_quoted(text, idx)
        return value, idx
    token, idx = _parse_token(text, idx, _STOP_CHARS)
    return _parse_primitive(token), idx


def _parse_object(text: str, idx: int) -> tuple[dict[str, Any], int]:
    obj: dict[str, Any] = {}
    idx += 1
    idx = _skip_ws(text, idx)
    if idx < len(text) and text[idx] == "}":
        return obj, idx + 1
    keys = []
    while idx < len(text):
        key, idx = _parse_token(text, idx, {",", "|", "}"})
        keys.append(str(key))
        idx = _skip_ws(text, idx)
        if idx >= len(text):
            break
        if text[idx] == ",":
            idx += 1
            continue
        if text[idx] == "|":
            idx += 1
            break
        if text[idx] == "}":
            return obj, idx + 1
    for key in keys:
        value, idx = _parse_value(text, idx)
        obj[key] = value
        idx = _skip_ws(text, idx)
        if idx >= len(text):
            break
        if text[idx] == "|":
            idx += 1
            continue
        if text[idx] == "}":
            return obj, idx + 1
    return obj, idx


def _parse_array(text: str, idx: int) -> tuple[list[Any], int]:
    items: list[Any] = []
    idx += 1
    idx = _skip_ws(text, idx)
    if idx < len(text) and text[idx] == "]":
        return items, idx + 1
    while idx < len(text):
        value, idx = _parse_value(text, idx)
        items.append(value)
        idx = _skip_ws(text, idx)
        if idx >= len(text):
            break
        if text[idx] == "|":
            idx += 1
            continue
        if text[idx] == "]":
            return items, idx + 1
    return items, idx


def _parse_table(text: str, idx: int) -> tuple[list[dict[str, Any]], int]:
    idx += 1
    idx = _skip_ws(text, idx)
    if text[idx : idx + 3].lower() == "csv":
        idx += 3
        idx = _skip_ws(text, idx)
        if idx >= len(text) or text[idx] != "[":
            raise ValueError("Invalid csv table rows")
        idx += 1
        idx = _skip_ws(text, idx)
        rows: list[dict[str, Any]] = []
        if idx < len(text) and text[idx] == "]":
            return rows, idx + 1
        header_segment, idx = _read_segment(text, idx)
        keys = [str(_parse_primitive(tok)) for tok in _split_csv_segment(header_segment)]
        if idx < len(text) and text[idx] == "|":
            idx += 1
        while idx < len(text):
            row_segment, idx = _read_segment(text, idx)
            if row_segment == "" and idx < len(text) and text[idx] == "]":
                return rows, idx + 1
            row_tokens = _split_csv_segment(row_segment)
            row_values = [_parse_primitive(tok) for tok in row_tokens]
            rows.append({k: v for k, v in zip(keys, row_values)})
            if idx >= len(text):
                break
            if text[idx] == "|":
                idx += 1
                continue
            if text[idx] == "]":
                return rows, idx + 1
        return rows, idx
    if idx >= len(text) or text[idx] != "{":
        raise ValueError("Invalid table header")
    keys, idx = _parse_keys(text, idx)
    idx = _skip_ws(text, idx)
    if idx >= len(text) or text[idx] != "[":
        raise ValueError("Invalid table rows")
    idx += 1
    idx = _skip_ws(text, idx)
    rows = []
    if idx < len(text) and text[idx] == "]":
        return rows, idx + 1
    while idx < len(text):
        row = []
        while idx < len(text):
            token, idx = _parse_token(text, idx, {",", "|", "]"})
            row.append(_parse_primitive(token))
            idx = _skip_ws(text, idx)
            if idx >= len(text) or text[idx] in {"|", "]"}:
                break
            if text[idx] == ",":
                idx += 1
                continue
        rows.append({k: v for k, v in zip(keys, row)})
        if idx >= len(text):
            break
        if text[idx] == "|":
            idx += 1
            continue
        if text[idx] == "]":
            return rows, idx + 1
    return rows, idx


def _parse_keys(text: str, idx: int) -> tuple[list[str], int]:
    keys = []
    idx += 1
    idx = _skip_ws(text, idx)
    if idx < len(text) and text[idx] == "}":
        return keys, idx + 1
    while idx < len(text):
        key, idx = _parse_token(text, idx, {",", "}"})
        keys.append(str(key))
        idx = _skip_ws(text, idx)
        if idx >= len(text):
            break
        if text[idx] == ",":
            idx += 1
            continue
        if text[idx] == "}":
            return keys, idx + 1
    return keys, idx


def _parse_toon(text: str) -> Any:
    value, _ = _parse_value(text, 0)
    return value


def _parse_csv(text: str) -> Any:
    reader = csv.reader(text.splitlines())
    rows = list(reader)
    if not rows:
        return []
    header = rows[0]
    data = []
    for row in rows[1:]:
        item = {}
        for key, value in zip(header, row):
            item[key] = _parse_primitive(value)
        data.append(item)
    return data


def _yaml_indent(line: str) -> int:
    return len(line) - len(line.lstrip(" "))


def _yaml_parse_inline(token: str) -> Any:
    token = token.strip()
    if token == "":
        return ""
    if token.startswith("\"") and token.endswith("\""):
        return _unescape_string(token[1:-1])
    return _parse_primitive(token)


def _yaml_parse_node(lines: list[str], idx: int, indent: int) -> tuple[Any, int]:
    if idx >= len(lines):
        return None, idx
    line = lines[idx]
    if _yaml_indent(line) < indent:
        return None, idx
    stripped = line.strip()
    if stripped.startswith("-"):
        items: list[Any] = []
        while idx < len(lines) and _yaml_indent(lines[idx]) == indent:
            item_line = lines[idx].strip()[1:].lstrip()
            if item_line == "":
                idx += 1
                item, idx = _yaml_parse_node(lines, idx, indent + 2)
                items.append(item)
            else:
                items.append(_yaml_parse_inline(item_line))
                idx += 1
        return items, idx
    if ":" in stripped:
        obj: dict[str, Any] = {}
        while idx < len(lines):
            line = lines[idx]
            if _yaml_indent(line) < indent:
                break
            if _yaml_indent(line) > indent:
                break
            content = line[indent:]
            if ":" not in content:
                break
            key, rest = content.split(":", 1)
            key_str = str(_parse_primitive(key.strip()))
            if rest.strip() == "":
                idx += 1
                value, idx = _yaml_parse_node(lines, idx, indent + 2)
                obj[key_str] = value
            else:
                obj[key_str] = _yaml_parse_inline(rest.strip())
                idx += 1
        return obj, idx
    return _yaml_parse_inline(stripped), idx + 1


def decode(input_str: str, options: dict | None = None) -> Any:
    """Decode TOON/JSON/YAML/CSV to Python values.

    Args:
        input_str: Input text.
        options: Reserved for future compatibility.

    Returns:
        Decoded Python value.
    """
    del options
    fmt = detect_format(input_str)
    if fmt == "json":
        return json.loads(input_str)
    if fmt == "csv":
        return _parse_csv(input_str)
    if fmt == "yaml":
        lines = [line.rstrip("\n") for line in input_str.splitlines() if line.strip() != ""]
        if not lines:
            return None
        value, _ = _yaml_parse_node(lines, 0, 0)
        return value
    if fmt == "toon":
        return _parse_toon(input_str)
    return _parse_toon(input_str)
