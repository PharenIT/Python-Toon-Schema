from toon_format import decode, encode


def test_decode_primitive_array():
    assert decode("[1|2|3]") == [1, 2, 3]


def test_decode_tabular_array():
    encoded = "^csv[id,name|1,A|2,B]"
    assert decode(encoded) == [{"id": 1, "name": "A"}, {"id": 2, "name": "B"}]
    legacy = "^{id,name}[1,A|2,B]"
    assert decode(legacy) == [{"id": 1, "name": "A"}, {"id": 2, "name": "B"}]


def test_decode_mixed_array():
    encoded = "[{x|1}|42|hi]"
    assert decode(encoded) == [{"x": 1}, 42, "hi"]


def test_decode_nested_object_roundtrip():
    data = {"users": [{"id": 1, "name": "Alice"}, {"id": 2, "name": "Bob"}]}
    assert decode(encode(data)) == data


def test_decode_json_yaml_csv():
    json_input = '{"a":1,"b":[2,3]}'
    yaml_input = "a: 1\nb: 2"
    csv_input = "id,name\n1,A\n2,B"
    assert decode(json_input) == {"a": 1, "b": [2, 3]}
    assert decode(yaml_input) == {"a": 1, "b": 2}
    assert decode(csv_input) == [{"id": 1, "name": "A"}, {"id": 2, "name": "B"}]
