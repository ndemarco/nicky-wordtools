#!/usr/bin/env python3
"""
morph_caps.py

Read lines from stdin and, for each capitalization morph spec, output all
possible uppercase-span variants per the DSL:

Spec syntax:
    w<start>[-<end>]<dir><pos>{<min>-<max>}

  w<start>[-<end>]   : word index or range (1-based)
  <dir>              : '^' (front) or '$' (back)
  <pos>              : position in word (1-based, relative to dir)
  {<min>-<max>}      : span of letters to uppercase (min..max contiguous)

Examples:
    w1^2{1-1}   # word1, front, start pos2, span1
    w2-3$1{2-3} # words2&3, back, start pos1 from end, spans2-3

Usage:
    cat lines.txt | python3 morph_caps.py w1^2{1-2} w2$1{1-1}
"""
import sys
import re
from typing import List, Tuple

SPEC_RE = re.compile(r'^w(?P<start>\d+)(?:-(?P<end>\d+))?(?P<dir>[\^$])(?P<pos>\d+)\{(?P<min>\d+)-(?P<max>\d+)\}$')

class Spec:
    def __init__(self, start: int, end: int, direction: str,
                 pos: int, min_span: int, max_span: int):
        self.start = start
        self.end = end
        self.direction = direction
        self.pos = pos
        self.min_span = min_span
        self.max_span = max_span

    def apply_to_line(self, line: str) -> List[str]:
        words = line.split()
        results = []
        # validate word indices
        n_words = len(words)
        if self.start < 1 or self.end > n_words:
            raise ValueError(f"Word index range {self.start}-{self.end} out of bounds for line '{line}'")
        # apply spec for each word index
        for wi in range(self.start - 1, self.end):
            word = words[wi]
            # validate pos
            if self.pos < 1 or self.pos > len(word):
                raise ValueError(f"Position {self.pos} out of bounds for word '{word}' in line '{line}'")
            # choose working representation
            if self.direction == '^':
                rep = word
                rev_flag = False
            else:
                rep = word[::-1]
                rev_flag = True
            # generate spans
            for span_len in range(self.min_span, self.max_span + 1):
                max_offset = self.max_span - span_len
                base = self.pos - 1
                for offset in range(max_offset + 1):
                    start = base + offset
                    end = start + span_len
                    if start < 0 or end > len(rep):
                        continue
                    mutated = rep[:start] + rep[start:end].upper() + rep[end:]
                    final_word = mutated[::-1] if rev_flag else mutated
                    new_words = words.copy()
                    new_words[wi] = final_word
                    results.append(' '.join(new_words))
        return results


def parse_spec(s: str) -> Spec:
    m = SPEC_RE.match(s)
    if not m:
        raise ValueError(f"Invalid spec '{s}'")
    start = int(m.group('start'))
    end = int(m.group('end')) if m.group('end') else start
    direction = m.group('dir')
    pos = int(m.group('pos'))
    min_span = int(m.group('min'))
    max_span = int(m.group('max'))
    if min_span < 1 or max_span < min_span:
        raise ValueError(f"Invalid span range {min_span}-{max_span} in spec '{s}'")
    return Spec(start, end, direction, pos, min_span, max_span)


def main():
    if len(sys.argv) < 2:
        sys.exit("Usage: morph_caps.py <spec1> [<spec2> ...]")
    specs = [parse_spec(arg) for arg in sys.argv[1:]]
    for line in sys.stdin:
        line = line.rstrip('\n')
        for spec in specs:
            try:
                for out in spec.apply_to_line(line):
                    print(out)
            except ValueError as e:
                print(f"Error: {e}", file=sys.stderr)
                continue

if __name__ == '__main__':
    main()
