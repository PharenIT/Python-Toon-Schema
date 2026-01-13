# TOON Format for Python

> **⚠️ Early Release (v0.1.x):** The API is stable enough for use, but may evolve before 1.0.0.

Compact, human-readable serialization format for LLM contexts with strong token savings on mixed and nested data. Uses a minimal syntax and deterministic round-trips. Designed for fast encode/decode and practical prompt efficiency.

## Key Features

Minimal syntax • Tabular arrays for uniform data • Optional auto format selection • Python 3.9+

## Installation

```bash
pip install p-toon-llm
```

## Quick Start

```python
from toon_format import encode, decode

# Simple object
encode({"name": "Alice", "age": 30})
# {name,age|Alice|30}

# Tabular array (uniform objects)
encode([{"id": 1, "name": "Alice"}, {"id": 2, "name": "Bob"}])
# ^csv[id,name|1,Alice|2,Bob]

# Decode back to Python
decode("{items|[apple|banana]}")
# {'items': ['apple', 'banana']}
```

## API Reference

### `encode(value, options=None)` → `str`

```python
encode({"id": 123})
encode({"id": 123}, {"mode": "auto", "candidates": ("toon", "json", "csv")})
```

Options:
1. `mode`: `toon` (default), `hybrid`, or `auto`
2. `candidates`: iterable of formats for auto mode
3. `metric`: `tokens` or `chars` for auto mode

### `decode(input_str, options=None)` → `Any`

```python
decode("{id|123}")
```

### Token Counting & Comparison

```python
from toon_format import estimate_savings, compare_formats, count_tokens

data = {"users": [{"id": 1, "name": "Alice"}, {"id": 2, "name": "Bob"}]}
result = estimate_savings(data)
print(f"Saves {result['savings_percent']:.1f}% tokens")

print(compare_formats(data))

toon_str = encode(data)
print(count_tokens(toon_str))
```

Requires `tiktoken` for accurate token counts. Without it, `count_tokens` falls back to character length.

## Format Specification

| Type | Example Input | TOON Output |
|------|---------------|-------------|
| **Object** | `{"name": "Alice", "age": 30}` | `{name,age|Alice|30}` |
| **Primitive Array** | `[1, 2, 3]` | `[1|2|3]` |
| **Tabular Array** | `[{"id": 1, "name": "A"}, {"id": 2, "name": "B"}]` | `^csv[id,name|1,A|2,B]` |
| **Mixed Array** | `[{"x": 1}, 42, "hi"]` | `[{x|1}|42|hi]` |

Quoting: only when necessary (empty, reserved tokens, numeric ambiguity, whitespace, delimiters)

Type Normalization: datetime/date -> ISO 8601 • Decimal -> float • NaN/Inf -> null • -0 -> 0

## Auto Mode

```python
from toon_format import encode_best, encode

best = encode_best(data, candidates=("toon", "json", "yaml", "csv"))
print(best["format"], best["text"])

print(encode(data, options={"mode": "auto", "candidates": ("toon", "json", "csv")}))
```

## Benchmarks

TOON tends to win on mixed and nested data. CSV will usually win on flat tables. Use your own datasets for reliable results.

```python
from toon_format import compare_formats, estimate_savings

print(compare_formats(data))
print(estimate_savings(data))
```

## Development

```bash
python -m pytest
```

## Documentation

1. `docs/index.md`
2. `docs/format.md`
3. `docs/api.md`
4. `docs/performance.md`
5. `docs/prompt_header.md`

## License

MIT License – see `LICENSE`
