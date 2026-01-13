# Performance Notes

- Encoder minimizes whitespace for arrays and uses compact JSON separators
  during comparison to reduce token count.
- Decoder uses a single pass parser with minimal allocations.
- Token counting uses `tiktoken` when installed; otherwise it falls back to
  character length for deterministic behavior.
