# TOON Format (Python)

TOON is a compact, reversible encoding of JSON designed to reduce LLM prompt tokens.
This implementation focuses on a minimal, deterministic syntax and fast encode/decode.

## Core Syntax

1. Objects use a key list and a value list: `{k1,k2|v1|v2}`
2. Arrays use pipe separators: `[v1|v2|v3]`
3. Tables (uniform dict arrays) use CSV blocks: `^csv[k1,k2|r1c1,r1c2|r2c1,r2c2]`

TOON is best for mixed or nested data. Pure tabular data is still smaller in raw CSV.

## Quick Start

```python
from toon_format import encode, decode, encode_best, encode_as, convert_format

data = {"users": [{"id": 1, "name": "Alice"}, {"id": 2, "name": "Bob"}]}

print(encode(data))
print(decode(encode(data)))
print(encode_best(data))
print(encode_as(data, "json"))
print(convert_format(encode(data), "yaml"))
```

## Installation

1. Install the package from PyPI:

```
pip install p-toon
```

2. Optional dev tools for build and upload:

```
pip install -e .[dev]
```

## Auto Mode

1. Pick the smallest format automatically (tokens by default):

```python
best = encode_best(data, candidates=("toon", "json", "yaml", "csv"))
print(best["format"], best["text"])
```

2. Or use auto mode inside `encode()`:

```python
print(encode(data, options={"mode": "auto", "candidates": ("toon", "json", "csv")}))
```

## Benchmarks

This repository provides tooling to measure token savings locally so you can benchmark your own data.
Run the demo or use `compare_formats` for a quick comparison, then expand to your real datasets.

Example workflow:

1. Start with a representative dataset that matches your production structure.
2. Compare TOON vs JSON compact, JSON pretty, YAML, and CSV.
3. Measure both tokens and chars, and pick the best format for your use case.

```python
from toon_format import compare_formats, estimate_savings

print(compare_formats(data))
print(estimate_savings(data))
```

If you want to publish benchmark results in this README, add your measured numbers and dataset description.

## Format Examples

Example object:

```
{name,age|Alice|30}
```

Example array:

```
[1|2|3]
```

Example table:

```
^csv[id,name|1,Alice|2,Bob]
```

## Layout

```
src/
  encoder.py
  decoder.py
  detect.py
  tokens.py
  compare.py
  formats.py
  convert.py
  toon_format.py
```

## Docs

1. `docs/index.md`
2. `docs/format.md`
3. `docs/api.md`
4. `docs/performance.md`
5. `docs/prompt_header.md`

## Tests

```
python -m pytest
```

## Demo

```
python examples/demo.py
```
