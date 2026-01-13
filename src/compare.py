"""Savings estimation and format comparison."""

from __future__ import annotations

import json
from typing import Any

from encoder import encode
from tokens import count_tokens


def estimate_savings(value: Any) -> dict:
    """Estimate token savings comparing JSON vs TOON."""
    json_str = json.dumps(value, ensure_ascii=False, separators=(",", ":"))
    toon_str = encode(value)
    json_tokens = count_tokens(json_str)
    toon_tokens = count_tokens(toon_str)
    savings = 0.0
    if json_tokens:
        savings = (json_tokens - toon_tokens) / json_tokens * 100
    return {
        "json_tokens": json_tokens,
        "toon_tokens": toon_tokens,
        "savings_percent": round(savings, 2),
    }


def compare_formats(value: Any) -> str:
    """Return a formatted comparison table for JSON and TOON."""
    json_str = json.dumps(value, ensure_ascii=False, separators=(",", ":"))
    toon_str = encode(value)
    json_tokens = count_tokens(json_str)
    toon_tokens = count_tokens(toon_str)
    json_size = len(json_str)
    toon_size = len(toon_str)
    savings_tokens = json_tokens - toon_tokens
    savings_pct = 0.0
    if json_tokens:
        savings_pct = savings_tokens / json_tokens * 100
    lines = [
        "Format Comparison",
        "────────────────────────────────────────────",
        f"{'Format':<10}{'Tokens':>8}{'Size (chars)':>14}",
        f"{'JSON':<10}{json_tokens:>8}{json_size:>14}",
        f"{'TOON':<10}{toon_tokens:>8}{toon_size:>14}",
        "────────────────────────────────────────────",
        f"Savings: {savings_tokens} tokens ({savings_pct:.1f}%)",
    ]
    return "\n".join(lines)
