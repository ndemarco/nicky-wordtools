#!/usr/bin/env python3
"""
Script to read weighted words from stdin and output all ordered permutations
sorted by combined weight and first-word weight.

Usage:
    cat wordlist.txt | python3 permute.py > permutations.txt

Each line of input should be:
    <word> <weight>

The script reads all entries, generates every ordered pair of distinct words,
calculates the total weight (weight1 + weight2), sorts by total weight
(descending) then by first-word weight (descending), and prints each pair
as "word1 word2" to stdout.
"""
import sys

def permute_by_value(lines):
    """
    Generate and print ordered word pairs based on weights.

    Reads lines of 'word weight' from the iterable `lines`, computes every
    ordered pair (word1, word2) where word1 != word2, sorts pairs descending
    by (weight1 + weight2) and then by weight1, and prints each pair as
    "word1 word2" to stdout.

    Args:
        lines: Iterable of strings, each containing a word and an integer weight.
    """
    entries = []
    for lineno, line in enumerate(lines, 1):
        line = line.strip()
        if not line:
            continue
        parts = line.split()
        try:
            wt = int(parts[-1])
        except ValueError:
            raise ValueError(f"Line {lineno}: invalid weight {parts[-1]!r}")
        word = " ".join(parts[:-1])
        entries.append((word, wt))

    pairs = []
    for word1, wt1 in entries:
        for word2, wt2 in entries:
            if word1 == word2:
                continue
            total = wt1 + wt2
            pairs.append((total, wt1, word1, word2))

    # Sort by combined weight, then by first-word weight, both descending
    pairs.sort(key=lambda x: (x[0], x[1]), reverse=True)

    for _, _, w1, w2 in pairs:
        print(f"{w1} {w2}")

if __name__ == "__main__":
    permute_by_value(sys.stdin)
