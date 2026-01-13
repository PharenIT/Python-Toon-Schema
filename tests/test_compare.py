from toon_format import compare_formats, estimate_savings, encode_best


def test_estimate_savings_keys():
    data = {"a": 1, "b": [2, 3]}
    result = estimate_savings(data)
    assert set(result.keys()) == {"json_tokens", "toon_tokens", "savings_percent"}


def test_compare_formats_output():
    data = {"a": 1}
    text = compare_formats(data)
    assert "Format Comparison" in text
    assert "JSON" in text
    assert "TOON" in text


def test_encode_best_selects_csv_for_table():
    data = [{"id": 1, "name": "A"}, {"id": 2, "name": "B"}]
    best = encode_best(data, candidates=("toon", "json", "csv"))
    assert best["format"] == "csv"
