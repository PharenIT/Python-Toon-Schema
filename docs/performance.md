# Performance Notes

- Encoder minimizes whitespace for arrays and uses compact JSON separators
  during comparison to reduce token count.
- Decoder uses a single pass parser with minimal allocations.
- Token counting uses `tiktoken` when installed; otherwise it falls back to
  character length for deterministic behavior.

## Benchmarks

TOON performance depends on structure. Use your real datasets and compare against
JSON compact, JSON pretty, YAML, and CSV. CSV will often win on flat tables, while
TOON tends to win on mixed or nested data.

Example workflow:

1. Choose a representative dataset.
2. Run `compare_formats` and `estimate_savings`.
3. Record tokens, chars, and total time for encode/decode.

For repeatable runs, keep the dataset fixed and always measure with the same
tokenizer/model. If you need to publish benchmark results, include dataset
descriptions and the exact commands used.
