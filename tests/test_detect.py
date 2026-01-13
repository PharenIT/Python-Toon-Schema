from detect import detect_format


def test_detect_json():
    assert detect_format('{"a":1}') == "json"


def test_detect_toon():
    assert detect_format("{a,b|1|2}") == "toon"


def test_detect_yaml():
    assert detect_format("a: 1\nb: 2") == "yaml"


def test_detect_csv():
    assert detect_format("id,name\n1,A\n2,B") == "csv"
