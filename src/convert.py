"""Format conversion helpers."""

from __future__ import annotations

from typing import Any

from decoder import decode
from formats import encode_as


def convert_format(input_str: str, target_format: str) -> str:
    """Decode input (auto-detect) and re-encode into target format."""
    value = decode(input_str)
    return encode_as(value, target_format)
