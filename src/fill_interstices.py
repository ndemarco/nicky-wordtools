#!/usr/bin/env python3
"""
fill_interstices.py

Read lines of "word1 word2" from stdin, and for each mask generate
all combinations of:
    word1 + <expanded-separator> + word2

Mask domain specific language (DSL) supports:
  ?d         consume one digit (0–9)
  ?^         pop earliest un-referenced ?d and output its shift-row symbol
  { ... }    group elements as one unit
  -          when trailing a group, reverse that group's printed output

Example:
  mask = "?d?d{?^?^}-" on line "foo bar" generates:
    foo56^%bar   (digits 5,6, then group "%^" reversed to "^%")

Usage:
    cat two_word_list.txt | python3 fill_interstices.py "?d?d{?^?^}-" ...
"""
import sys
import itertools
from copy import deepcopy
from typing import Union, Tuple, List

# mapping for shift-row symbols, index by digit char
_SHIFT_MAP = {
    '1': '!', '2': '@', '3': '#', '4': '$', '5': '%',
    '6': '^', '7': '&', '8': '*', '9': '(', '0': ')'
}

# Abstract Syntax Tree (AST) element types
element_base = Tuple[str]
element_group = Tuple[str, List["Element"], bool]
element_lit = Tuple[str, str]
Element = Union[element_base, element_group, element_lit]

def parse_mask(mask: str) -> List[Element]:
    """
    Parse mask string into AST elements.
    """
    elements = []
    i = 0
    n = len(mask)
    while i < n:
        if mask.startswith('?d', i):
            elements.append(('d',))
            i += 2
        elif mask.startswith('?^', i):
            elements.append(('caret',))
            i += 2
        elif mask[i] == '{':
            # parse group
            depth = 1
            j = i + 1
            while j < n and depth:
                if mask[j] == '{': depth += 1
                elif mask[j] == '}': depth -= 1
                j += 1
            if depth != 0:
                raise ValueError(f"Unmatched '{{' in mask: {mask}")
            # content between i+1 and j-1
            content = mask[i+1:j-1]
            # check for trailing -
            reverse = False
            if j < n and mask[j] == '-':
                reverse = True
                j += 1
            sub = parse_mask(content)
            elements.append(('group', sub, reverse))
            i = j
        else:
            # literal char
            elements.append(('lit', mask[i]))
            i += 1
    return elements

class State:
    """Holds digit queue and next reference index."""
    __slots__ = ('digits', 'next_ref')
    def __init__(self):
        self.digits = []     # list of digit chars
        self.next_ref = 0    # index of next to caret-reference
    def clone(self):
        st = State()
        st.digits = self.digits.copy()
        st.next_ref = self.next_ref
        return st


def expand_elements(elems: List[Element], state: State) -> List[Tuple[str, State]]:
    """
    Recursively expand AST elements, returning list of (output, new_state).
    """
    results = [('', state)]
    for el in elems:
        new_results = []
        typ = el[0]
        if typ == 'd':
            # branch on digits
            for out, st in results:
                for d in map(str, range(10)):
                    st2 = st.clone()
                    st2.digits.append(d)
                    new_results.append((out + d, st2))
        elif typ == 'caret':
            for out, st in results:
                if st.next_ref >= len(st.digits):
                    # not enough digits to reference
                    continue
                d = st.digits[st.next_ref]
                sym = _SHIFT_MAP[d]
                st2 = st.clone()
                st2.next_ref += 1
                new_results.append((out + sym, st2))
        elif typ == 'group':
            _, sub_elems, rev = el
            for out, st in results:
                # expand group content from this state
                grp_exp = expand_elements(sub_elems, st)
                for grp_out, st2 in grp_exp:
                    if rev:
                        grp_out = grp_out[::-1]
                    new_results.append((out + grp_out, st2))
        elif typ == 'lit':
            lit = el[1]
            for out, st in results:
                new_results.append((out + lit, st))
        else:
            raise ValueError(f"Unknown element type: {typ}")
        results = new_results
    return results


def generate_separators(mask: str) -> List[str]:
    """
    Given a mask DSL string, return all concrete separators.
    """
    ast = parse_mask(mask)
    init = State()
    exps = expand_elements(ast, init)
    # return only output strings
    return [out for out, _ in exps]


def fill_interstices(lines, masks):
    """
    Yield word1+sep+word2 for each line and each mask.
    """
    # cache generated separators per mask
    cache: dict[str, List[str]] = {}
    for mask in masks:
        cache[mask] = generate_separators(mask)

    for raw in lines:
        parts = raw.strip().split()
        if len(parts) != 2:
            continue
        w1, w2 = parts
        for mask in masks:
            for sep in cache[mask]:
                yield f"{w1}{sep}{w2}"

if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit("Usage: fill_interstices.py <mask1> [<mask2> ...]")
    masks = sys.argv[1:]
    for combo in fill_interstices(sys.stdin, masks):
        print(combo)
