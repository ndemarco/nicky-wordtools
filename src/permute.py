#!/usr/bin/env python3
"""
Read words with optional weights from stdin and output all ordered permutations.

Usage:
    cat wordlist.txt | python3 permute.py > permutations.txt

Each line of input should be:
    <word> <weight>

The script reads all entries, generates every ordered pair of distinct words,
calculates the total weight (weight1 + weight2), sorts by total weight
(descending) then by first-word weight (descending), and prints each pair
as "word1 word2" to stdout. If any weight is missing or invalid, the line
is treated as unweighted and pairs are output in input order.
"""
import sys

def permute_by_value(lines):
    """
    Generate and print ordered word pairs based on optional weights.

    Reads lines of 'word' + optional 'weight' from the iterable `lines`, computes every
    ordered pair (word1, word2) where word1 != word2.

    If all weights parse as numbers, sorts pairs descending by (weight1 + weight2)
    then by weight1. If any weight is missing or invalid, treats input as unweighted
    and outputs pairs in the same order words appeared in the file.

    Args:
        lines: Iterable of strings, each containing a word and optionally a weight.
    """
    entries = []
    unweighted_mode = False

    # Read all entries, track if any weight is missing or invalid
    for line in lines:
        line = line.strip()
        if not line:
            continue

        parts = line.split()
        if len(parts) < 2:
            # No weight → unweighted mode
            entries.append((parts[0], None))
            unweighted_mode = True
        else:
            word = " ".join(parts[:-1])
            w_str = parts[-1]
            try:
                wt = float(w_str)
                entries.append((word, wt))
            except ValueError:
                # Invalid weight → unweighted mode
                entries.append((word, None))
                unweighted_mode = True

    if not entries:
        return

    # Unweighted mode: preserve the input order of words
    if unweighted_mode:
        words = [word for word, _ in entries]
        for w1 in words:
            for w2 in words:
                if w1 != w2:
                    print(f"{w1} {w2}")
        return

    # Weighted mode: build and sort by (total weight, first-word weight)
    pairs = []
    for word1, wt1 in entries:
        for word2, wt2 in entries:
            if word1 == word2:
                continue
            pairs.append((wt1 + wt2, wt1, word1, word2))

    pairs.sort(key=lambda x: (x[0], x[1]), reverse=True)
    for _, _, w1, w2 in pairs:
        print(f"{w1} {w2}")

if __name__ == "__main__":
    permute_by_value(sys.stdin)
