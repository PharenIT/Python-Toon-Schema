# API Reference

## encode(value, options=None) -> str

Encode a Python value into TOON.

Options:
- `mode`: `toon` (default), `hybrid`, or `auto`
- `candidates`: iterable of formats for auto mode
- `metric`: `tokens` or `chars` for auto mode

## decode(input_str, options=None) -> Any

Auto-detect and decode JSON, YAML, CSV, or TOON into Python values.

## count_tokens(value) -> int

Count tokens using `tiktoken` when available. Falls back to character count.

## estimate_savings(value) -> dict

Return JSON vs TOON token counts and percentage savings.

## compare_formats(value) -> str

Return a formatted comparison table for JSON and TOON.

## encode_as(value, fmt) -> str

Encode a Python value into a specific format: `toon`, `json`, `json_pretty`,
`yaml`, or `csv`.

## encode_best(value, candidates=None, metric="tokens") -> dict

Pick the smallest encoding among the candidates and return:
`{format, text, tokens, chars}`.

## convert_format(input_str, target_format) -> str

Auto-detect and decode input, then re-encode into a chosen format.
