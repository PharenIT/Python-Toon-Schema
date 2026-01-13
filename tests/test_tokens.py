from toon_format import count_tokens


def test_count_tokens_string():
    assert isinstance(count_tokens("hello"), int)


def test_count_tokens_value():
    assert isinstance(count_tokens({"a": 1}), int)
