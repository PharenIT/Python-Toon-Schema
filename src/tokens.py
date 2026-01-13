"""Token counting utilities."""

from __future__ import annotations

from typing import Any

from encoder import encode


def _get_encoder():
    try:
        import tiktoken
    except Exception:
        return None
    for model in ("gpt-4o-mini", "gpt-4o", "gpt-4-turbo"):
        try:
            return tiktoken.encoding_for_model(model)
        except Exception:
            continue
    try:
        return tiktoken.get_encoding("cl100k_base")
    except Exception:
        return None


def count_tokens(value: Any) -> int:
    """Count tokens using tiktoken when available.

    Args:
        value: Either a raw string or a Python value to encode as TOON.

    Returns:
        Token count (character count fallback if tiktoken is unavailable).
    """
    text = value if isinstance(value, str) else encode(value)
    encoder = _get_encoder()
    if encoder is None:
        return len(text)
    return len(encoder.encode(text))
