import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from toon_format import (
    compare_formats,
    count_tokens,
    decode,
    encode,
    encode_as,
    encode_best,
    estimate_savings,
)


DATA = {
    "users": [
        {"id": 1, "name": "Alice", "role": "admin"},
        {"id": 2, "name": "Bob", "role": "member"},
        {"id": 3, "name": "Cara", "role": "member"},
    ],
    "meta": {"team": "Toon", "active": True, "region": "EU"},
    "events": [
        {"type": "login", "user_id": 1, "ok": True},
        {"type": "purchase", "user_id": 2, "amount": 19.99},
        "note: rollout 1",
    ],
}

MIXED_DATA = {
    "session": {
        "id": "s1",
        "user": {"id": 7, "name": "Mila"},
        "flags": [True, False, None],
    },
    "timeline": [
        {"t": "login", "ok": True},
        {"t": "view", "page": "/pricing"},
        ["nested", {"k": "v"}],
        42,
    ],
    "meta": {"tags": ["alpha", "beta"], "score": 9.5},
}


def _yaml_simple(obj, indent=0):
    pad = " " * indent
    if isinstance(obj, dict):
        lines = []
        for k, v in obj.items():
            if isinstance(v, (dict, list)):
                lines.append(f"{pad}{k}:")
                lines.append(_yaml_simple(v, indent + 2))
            else:
                lines.append(f"{pad}{k}: {v}")
        return "\n".join(lines)
    if isinstance(obj, list):
        lines = []
        for item in obj:
            if isinstance(item, (dict, list)):
                lines.append(f"{pad}-")
                lines.append(_yaml_simple(item, indent + 2))
            else:
                lines.append(f"{pad}- {item}")
        return "\n".join(lines)
    return f"{pad}{obj}"


def _csv_from_list(rows):
    if not rows:
        return ""
    keys = list(rows[0].keys())
    lines = [",".join(keys)]
    for row in rows:
        lines.append(",".join(str(row.get(k, "")) for k in keys))
    return "\n".join(lines)


def _section(title):
    print(title)
    print("-" * len(title))


def _print_block(title, content):
    _section(title)
    print(content)
    print()


def _print_tokens(title, items):
    _section(title)
    for key, value in items.items():
        print(f"{key:<12}{value}")
    print()


def main():
    toon_text = encode(DATA)
    json_compact = json.dumps(DATA, ensure_ascii=False, separators=(",", ":"))
    json_pretty = json.dumps(DATA, ensure_ascii=False, indent=2)
    yaml_text = _yaml_simple(DATA)
    csv_text = _csv_from_list(DATA["users"])

    _print_block("TOON", toon_text)
    _print_block("Savings", f"{estimate_savings(DATA)}\n{compare_formats(DATA)}")
    _print_block("JSON (compact)", json_compact)
    _print_block("JSON (pretty)", json_pretty)
    _print_block("YAML (simple)", yaml_text)
    _print_block("CSV (users)", csv_text)

    _print_tokens(
        "Token comparison (TOON vs JSON vs YAML vs CSV)",
        {
            "toon": count_tokens(toon_text),
            "json_compact": count_tokens(json_compact),
            "json_pretty": count_tokens(json_pretty),
            "yaml": count_tokens(yaml_text),
            "csv": count_tokens(csv_text),
        },
    )

    _print_block("Round-trip", decode(encode(DATA)))
    _print_block("Mixed nested example", encode(MIXED_DATA))

    best = encode_best(MIXED_DATA, candidates=("toon", "json", "yaml"))
    _print_block("Auto-best (mixed nested)", f"{best['format']}\n{best['text']}")

    best_table = encode_best(DATA["users"], candidates=("toon", "json", "yaml", "csv"))
    _print_block("Auto-best (users table)", f"{best_table['format']}\n{best_table['text']}")

    _print_block("Convert (TOON -> JSON)", encode_as(decode(toon_text), "json"))
    _print_block(
        "Encode mode=auto (users table)",
        encode(DATA["users"], options={"mode": "auto", "candidates": ("toon", "json", "csv")}),
    )


if __name__ == "__main__":
    main()
