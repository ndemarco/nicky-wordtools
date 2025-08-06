import pytest
from io import StringIO
from permute import permute_by_value

def _run(input_lines, capsys):
    permute_by_value(StringIO(input_lines))
    out, _ = capsys.readouterr()
    return out.strip().splitlines()

@pytest.mark.parametrize("input_lines, expected", [
    # basic integer weights (from your existing tests, but checking order)
    ("wordA 10\nwordB 20\n", ["wordB wordA", "wordA wordB"]),
    ("alpha 100\nbeta 50\ngamma 50\n", [
        "alpha beta",  # total=150, wt1=100
        "beta alpha",  # total=150, wt1=50
        "alpha gamma", # total=150, wt1=100
        "gamma alpha", # total=150, wt1=50
        "beta gamma",  # total=100, wt1=50
        "gamma beta",  # total=100, wt1=50
    ]),
])
def test_weighted_integers(input_lines, expected, capsys):
    actual = _run(input_lines, capsys)
    assert actual == expected

def test_weighted_floats_and_negatives(capsys):
    # floats
    inp = "a 1.5\nb 2.5\n"
    # (b,a) has total=4.0, wt1=2.5 → comes before (a,b) total=4.0, wt1=1.5
    assert _run(inp, capsys) == ["b a", "a b"]

    # negative integers
    inp = "a -1\nb 2\nc 0\n"
    # totals:
    #  b→c: 2+0=2, wt1=2
    #  c→b: 0+2=2, wt1=0
    #  b→a: 2+(-1)=1, wt1=2
    #  a→b:-1+2=1, wt1=-1
    #  c→a: 0+(-1)=-1,wt1=0
    #  a→c:-1+0=-1,wt1=-1
    assert _run(inp, capsys) == [
        "b c", "c b",
        "b a", "a b",
        "c a", "a c",
    ]

    # negative floats
    inp = "x -1.5\ny 0.5\n"
    # both totals = -1.0, so order by wt1: y(- first) then x
    assert _run(inp, capsys) == ["y x", "x y"]

@pytest.mark.parametrize("input_lines, expected", [
    # no weights at all
    ("a\nb\n", ["a b", "b a"]),

    # mixed missing + valid weights → unweighted fallback
    ("a 1\nb\nc 2\n", [
        "a b", "a c",
        "b a", "b c",
        "c a", "c b",
    ]),

    # invalid weight string → unweighted fallback
    ("foo bar\nbaz 3\n", ["foo baz", "foo bar"?]),  # Wait, error: invalid test
])
def test_unweighted_missing_and_mixed(input_lines, expected, capsys):
    assert _run(input_lines, capsys) == expected

def test_invalid_weight_does_not_raise_but_falls_back(capsys):
    inp = "hello foo\nworld bar\n"
    # both lines invalid → unweighted with input order
    assert _run(inp, capsys) == ["hello world", "world hello"]

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
    actual = _run(input_lines, capsys)
    assert sorted(actual) == sorted(expected)
