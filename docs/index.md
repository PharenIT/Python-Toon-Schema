# TOON Format

TOON is a token-optimized, reversible serialization format intended for LLM prompts.
It preserves structure while reducing noise compared to JSON.

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
