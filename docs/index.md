# TOON Format

TOON is a token-optimized, reversible serialization format intended for LLM prompts.
It preserves structure while reducing noise compared to JSON.

## Origin

This project exists because multiple large customers wanted more efficient
representations to reduce token costs in their AI solutions.

## Highlights

- Compact object, array, and table encodings
- Automatic type detection on decode
- Optional token counting via `tiktoken`

## Quick Start

```python
from toon_format import encode, decode, compare_formats, estimate_savings, encode_best

data = {"users": [{"id": 1, "name": "Alice"}, {"id": 2, "name": "Bob"}]}

print(encode(data))
print(estimate_savings(data))
print(compare_formats(data))
print(decode(encode(data)))
print(encode_best(data))
```

See `docs/format.md` for the full encoding rules.

## Benchmarks

This repository includes tools to benchmark TOON locally on your own datasets.
Use `compare_formats` and `estimate_savings` with representative data to measure
token and character savings, then decide whether TOON or another format is best.
