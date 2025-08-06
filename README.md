# nicky-wordtools

A chained set of fast, composable wordlist transformation tools designed to attack passphrases comprising multiple words with interleaved numbers and symbols. The toolchain is best applied when a compatible password algorithm is known or suspected to have been used.

The toolchain pipeline begins by consuming a prioritized list of words. It builds all possible permutations of the list, applies transforms to each word of each result, then concatenates the words with interleaved digits and symbols.

This tool is designed for password recovery, passphrase cracking, and other custom wordlist generation scenarios.

## Future improvements
- Consider using Markov analysis to assign weights to words.
- Make word weights optional (use if detected).

# Installation

```bash
pip install nicky-wordtools
```

# Permutation approach

Each stage modifies the stage before it and accepts data from stdin and emits to stdout, making them all suitable for pipelines. The pipeline starts with a wordlist.

## Stage summary

- `permute` — Generate permutations of corpus inputs
- `fill-interstices` — Insert character patterns or masks between base words
- `morph` — Apply capitalization morphs using a flexible DSL
- `toolchain` — Compose and chain stages together for full workflows
- `stats` — Analyze resulting lists without emitting candidates

## Stages

## `permute`
Generate all ordered permutations of words using explicit and positional weighted input.
```bash
permute < corpus.txt > permuted.txt
```

- Input: lines of `word weight`
- Output: `word1` `word2` pairs sorted by combined weight then first-word weight

## `fill-interstices`
Insert separators between word pairs based on mask domain specific language (DSL).

```bash
fill-interstices '?d?d < permuted.txt > filled.txt
```

- Input: lines of `word1` `word2`
- Mask DSL
  - `?d` → any digit (0–9)
  - `?r` → any number-row symbol (!@#$%^&*())
  - `?^` → shift-row symbol of a previously consumed digit

  - `{ ... }` → group tokens
  - `-` → reverse grouped output

- Example: `?d?d{?^?^}-` expands to e.g. `56^%`

## `morph-caps`
Apply capitalization morphs using a domain specific language (DSL).


The morph stage uses a small DSL to define how and where capitalization is applied.

```bash
morph-caps w1^2{1-2} < filled.txt > morphed.txt
```

- Input: any text lines
- Spec DSL: `w<idx>[-<idx2>]<^|$><pos>{<min>-<max>}`
  - `w1` → first word (use `w2-3` for a range)
  - `^2` → start at position 2 from front
  - `$3` → start at position 3 from back
  - `{1-2}` → span of 1 to 2 letters to uppercase
- Example: `w1^2{1-2}` on `foo bar` yields `fOo bar`, `foO bar`, `fOO bar`

## `toolchain`
Wrap and chain multiple stages with a single command.
```bash
toolchain --permute --fill '?d' --morph 'w1^2{1-2}' --stats -i corpus.txt -o results.txt
```

- Runs stages in order: permute → fill-interstices → morph-caps
- --input/-i specify input file (default stdin)
- --output/-o specify output file (default stdout)
- --log specify log file (default toolchain.log)

## `stats`
Analyze candidate output (does not emit candiates).

- Outputs:
  - Total cnadidate count
  - Shortest / Longest line length
  - Average line length

# Example workflow
  ```bash
  cat corpus.txt \
    | permute \
    | fill-interstices '?d' \
    | morph-caps w1^2{1-2} \
    | stats
```

This will:
1. Generate permutations from corpus.txt
1. Insert a digit between joined words (?d mask = 0–9)
1. Apply capitalization variations to the first word
1. Output statistics only (no candidate output)

# Logging
The `toolchain` command logs key details about each run:
- Timestamp and command line
- Word count from input
- Output filename (if redirected)

# Contributing
Nicky likes helpers. Contributions are welcome! See `tests/` for pytest-based test coverage.

# License
MIT license



# More examples

- w1 → First word (you can also use a range like w1-2)
- ^2 → Start at position 2 from the front (LTR)
- $3 → Start at position 3 from the back (RTL)
- {1-2} → Capitalize 1 to 2 letters

| Spec          | Description                                            |
| ------------- | ------------------------------------------------------ |
| `w1^1{1-1}`   | Capitalize 1 letter starting from position 1 in word 1 |
| `w1$2{2-2}`   | Capitalize 2 letters starting 2 from the end of word 1 |
| `w2^1{1-1}`   | Capitalize the first letter of word 2                  |
| `w1-2^1{1-1}` | Capitalize first letter of words 1 and 2 (range)       |

### Example input
`foo bar`

### Example spec
`w1-2^1{1-1}`

### Output
```
Foo bar
foo Bar
```
