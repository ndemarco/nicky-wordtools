import pytest
from morph_caps import parse_spec, Spec

# Main cases - tested via parameterization decorator
@ pytest.mark.parametrize("spec_str,line,expected", [
    ("w1^2{1-1}", "capital word", ["cApital word"]),
    ("w1^2{1-2}", "capital word", [
        "cApital word",  # span=1, offset=0
        "caPital word",  # span=1, offset=1
        "cAPital word",  # span=2, offset=0
    ]),
    ("w1$3{1-1}", "capital", ["capiTal"]),
    ("w2^1{1-1}", "foo bar baz", ["foo Bar baz"]),
    ("w1-2^1{1-1}", "foo bar", ["Foo bar", "foo Bar"]),
])
def test_main_cases(spec_str, line, expected):
    spec = parse_spec(spec_str)
    result = spec.apply_to_line(line)
    assert result == expected

# Test for out-of-range word index
def test_word_index_out_of_range():
    spec = parse_spec("w3^1{1-1}")
    with pytest.raises(ValueError):
        spec.apply_to_line("one two")

# test for position out of range for word RTL and LTR
def test_position_out_of_range_ltr():
    spec = parse_spec("w1^12{1-1}")
    with pytest.raises(ValueError):
        spec.apply_to_line("abcdefghij")  # 10 letters, pos=12

def test_position_out_of_range_rtl():
    spec = parse_spec("w1$12{1-1}")
    with pytest.raises(ValueError):
        spec.apply_to_line("abcdefghij")

# Test spans sliding and combination
def test_span_and_sliding():
    spec = parse_spec("w1^1{2-3}")
    result = spec.apply_to_line("word")
    # span=2 on positions 1-2 -> WOrd, wORd; span=3 at pos1 -> WORd
    assert sorted(result) == sorted(["WOrd", "wORd", "WORd"])

# Test for Invalid spec format
def test_parse_invalid_spec():
    with pytest.raises(ValueError):
        parse_spec("invalid")

# Composite test: multiple specs on same line
def test_multiple_specs():
    specs = [parse_spec("w1^1{1-1}"), parse_spec("w2$1{1-1}")]
    line = "hello world"
    all_out = []
    for spec in specs:
        all_out.extend(spec.apply_to_line(line))
    assert sorted(all_out) == sorted(["Hello world", "hello worlD"])

# Edge: single-letter word
def test_single_letter_word():
    spec = parse_spec("w1^1{1-1}")
    assert spec.apply_to_line("a") == ["A"]

# Edge: word length equal to span
def test_entire_word_span():
    spec = parse_spec("w1^1{10-10}")
    # 10 letters
    assert spec.apply_to_line("abcdefghij") == ["ABCDEFGHIJ"]
