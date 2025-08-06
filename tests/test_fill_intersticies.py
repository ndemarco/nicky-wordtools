import pytest
from fill_interstices import generate_separators

# Shift mapping for reference in tests
SHIFT_MAP = {'1':'!', '2':'@', '3':'#', '4':'$', '5':'%', '6':'^', '7':'&', '8':'*', '9':'(', '0':')'}
DIGITS_IN_ORDER = list('0123456789')

@ pytest.mark.parametrize("mask, expected", [
    ('?d', [str(i) for i in range(10)]),
    ('?^', []),
])
def test_basic_placeholders(mask, expected):
    result = generate_separators(mask)
    assert result == expected

@ pytest.mark.parametrize("mask, count, first, last", [
    ('?d?d', 100, '00', '99'),
    ('?d?d?^', 100, '00)', '99('),
])
def test_digit_combinations(mask, count, first, last):
    result = generate_separators(mask)
    assert len(result) == count
    assert result[0] == first
    assert result[-1] == last

@ pytest.mark.parametrize("mask, expected", [
    ('?d?^', [f"{d}{SHIFT_MAP[d]}" for d in DIGITS_IN_ORDER]),
    ('{?d?^}', [f"{d}{SHIFT_MAP[d]}" for d in DIGITS_IN_ORDER]),
])
def test_digit_caret(mask, expected):
    result = generate_separators(mask)
    assert result == expected

@ pytest.mark.parametrize("mask, expected", [
    ('{?d?^}-', [ (f"{d}{SHIFT_MAP[d]}")[::-1] for d in DIGITS_IN_ORDER]),
])
def test_group_reverse(mask, expected):
    result = generate_separators(mask)
    assert result == expected

@ pytest.mark.parametrize("mask, count, first, last", [
    ('?d?d{?^?^}', 100, '00))', '99(('),
    ('?d?d{?^?^}-', 100, '00))', '99(('),
])
def test_group_extended(mask, count, first, last):
    result = generate_separators(mask)
    assert len(result) == count
    assert result[0] == first
    assert result[-1] == last

@ pytest.mark.parametrize("mask, count", [
    ('?d?d?d?d', 10**4),
    ('?d?d?^?^', 100),
])
def test_max_insertion_length(mask, count):
    # Max tokens = 4 produces correct count
    result = generate_separators(mask)
    assert len(result) == count

@ pytest.mark.parametrize("mask, expected", [
    ('abc', ['abc']),
    ('A?dB', [f"A{i}B" for i in range(10)]),
    ('{AB}-', ['BA']),
])
def test_literal_and_group(mask, expected):
    result = generate_separators(mask)
    assert result == expected

@ pytest.mark.parametrize("mask", [
    '?d{?^?^}-',  # insufficient caret refs -> no outputs
    '?^?d',       # caret before any digit -> no outputs
])
def test_invalid_sequences(mask):
    result = generate_separators(mask)
    assert result == []
