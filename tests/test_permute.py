import pytest
from io import StringIO
from permute import permute_by_value

@pytest.mark.parametrize("input_lines, expected_output", [
    ("wordA 10\nwordB 20\n", [
        "wordB wordA",
        "wordA wordB",
    ]),
    ("alpha 100\nbeta 50\ngamma 50\n", [
        "alpha beta",
        "beta alpha",
        "alpha gamma",
        "gamma alpha",
        "beta gamma",
        "gamma beta",
    ]),
])
def test_permute_basic(input_lines, expected_output, capsys):
    input_stream = StringIO(input_lines)
    permute_by_value(input_stream)
    out, err = capsys.readouterr()
    actual_lines = out.strip().split("\n")
    assert sorted(actual_lines) == sorted(expected_output)


def test_permute_ignores_blank_lines(capsys):
    input_lines = """
word1 5

word2 10
    
word3 7
"""
    expected = [
        "word2 word3", "word3 word2",
        "word2 word1", "word1 word2",
        "word3 word1", "word1 word3"
    ]
    permute_by_value(StringIO(input_lines))
    out, _ = capsys.readouterr()
    assert sorted(out.strip().splitlines()) == sorted(expected)


def test_invalid_weight_raises():
    with pytest.raises(ValueError):
        permute_by_value(StringIO("word 5x\n"))
