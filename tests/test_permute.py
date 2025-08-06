import pytest
from io import StringIO
from permute import permute_by_value

def _run(input_lines, capsys):
    """
    Helper: run permute_by_value over the given lines and
    return stdout lines as a list.
    """
    permute_by_value(StringIO(input_lines))
    out, _ = capsys.readouterr()
    return out.strip().splitlines()


@pytest.mark.parametrize("input_lines, expected", [
    # (1) No weights at all → unweighted in input order
    ("a\nb\n", ["a b", "b a"]),

    # (2) Mixed missing + valid → unweighted fallback
    ("a 1\nb\nc 2\n", [
        "a b", "a c",
        "b a", "b c",
        "c a", "c b",
    ]),

    # (3) Invalid weight string → unweighted fallback
    ("foo bar\nbaz 3\n", ["foo baz", "baz foo"]),
])
def test_unweighted_missing_and_invalid(input_lines, expected, capsys):
    assert _run(input_lines, capsys) == expected


@pytest.mark.parametrize("input_lines, expected", [
    # Basic integer weights
    ("wordA 10\nwordB 20\n", ["wordB wordA", "wordA wordB"]),

    ("alpha 100\nbeta 50\ngamma 50\n", [
        "alpha beta", "beta alpha",
        "alpha gamma", "gamma alpha",
        "beta gamma", "gamma beta",
    ]),
])
def test_weighted_integers(input_lines, expected, capsys):
    assert _run(input_lines, capsys) == expected


def test_weighted_floats_and_negatives(capsys):
    # Floats
    inp = "a 1.5\nb 2.5\n"
    assert _run(inp, capsys) == ["b a", "a b"]

    # Negative integers
    inp2 = "a -1\nb 2\nc 0\n"
    assert _run(inp2, capsys) == [
        "b c", "c b",
        "b a", "a b",
        "c a", "a c",
    ]

    # Negative floats
    inp3 = "x -1.5\ny 0.5\n"
    assert _run(inp3, capsys) == ["y x", "x y"]


def test_ignores_blank_lines(capsys):
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
    assert sorted(_run(input_lines, capsys)) == sorted(expected)
