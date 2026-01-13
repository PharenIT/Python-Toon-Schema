from datetime import datetime
from decimal import Decimal

import pytest

from toon_format import encode
from formats import encode_as


def test_encode_object_compact():
    data = {"name": "Alice", "age": 30}
    assert encode(data) == "{name,age|Alice|30}"


def test_encode_primitive_array_compact():
    data = [1, 2, 3]
    assert encode(data) == "[1|2|3]"


def test_encode_tabular_array():
    data = [{"id": 1, "name": "A"}, {"id": 2, "name": "B"}]
    assert encode(data) == "^csv[id,name|1,A|2,B]"


def test_encode_mixed_array():
    data = [{"x": 1}, 42, "hi"]
    assert encode(data) == "[{x|1}|42|hi]"


def test_normalization_rules():
    dt = datetime(2024, 1, 1, 12, 30, 0)
    data = {"time": dt, "amount": Decimal("1.25")}
    encoded = encode(data)
    assert "2024-01-01T12:30:00" in encoded
    assert "1.25" in encoded


def test_encode_as_json():
    data = {"a": 1}
    assert encode_as(data, "json") == "{\"a\":1}"


def test_encode_auto_selects_csv_for_table():
    data = [{"id": 1, "name": "A"}, {"id": 2, "name": "B"}]
    result = encode(data, options={"mode": "auto", "candidates": ("toon", "json", "csv")})
    assert result.startswith("id,name")


def test_encode_unknown_mode():
    with pytest.raises(ValueError):
        encode({"a": 1}, options={"mode": "nope"})
