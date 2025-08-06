#!/usr/bin/env python3
"""
Toolchain wrapper for password candidate pipeline stages: permute, fill_interstices, morph_caps, and stats.

Usage:
  toolchain.py [--input INPUT] [--output OUTPUT] [--log LOGFILE]
               [--permute]
               [--fill MASK [MASK ...]]
               [--morph SPEC [SPEC ...]]
               [--stats]

Layers of help:
  toolchain.py --help                # show overall help
  toolchain.py --help --permute      # show permute stage help
  toolchain.py --help --fill         # show fill_interstices stage help
  toolchain.py --help --morph        # show morph_caps stage help
  toolchain.py --help --stats        # show stats stage help
"""
import sys
import os
import argparse
import subprocess
import logging
from statistics import mean

# Locate utilities directory relative to this script
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UTIL_DIR = os.path.join(BASE_DIR, 'utilities')
PYTHON = sys.executable

# Stage help texts
_STAGE_HELP = {
    'permute':
        """
permute stage:
  Reads 'word weight' lines from stdin and outputs all ordered
  word pairs sorted by combined weight then first-word weight.
Usage:
  <previous> | toolchain.py --permute [other options]
""",
    'fill':
        """
fill_interstices stage:
  Reads 'word1 word2' lines and a list of mask DSLs, outputs
  concatenated word1 + separator + word2 for each mask.
Usage:
  <previous> | toolchain.py --fill ?d?d ?d{?^?^}- [other options]
""",
    'morph':
        """
morph_caps stage:
  Reads lines of text and morphs capitalization per spec DSL:
    w<idx>[-<idx2>]<^|$><pos>{<min>-<max>}
Usage:
  <previous> | toolchain.py --morph w1^2{1-2} [other options]
""",
    'stats':
        """
stats mode:
  Instead of output, prints:
    - Total candidate count
    - Shortest line length
    - Longest line length
    - Average line length
Usage:
  toolchain.py --stats [with other stages]
"""
}


def print_stage_help(stage):
    help_text = _STAGE_HELP.get(stage)
    if help_text:
        print(help_text.strip())
        sys.exit(0)


def parse_args():
    # Pre-check for layered help
    if '--help' in sys.argv:
        for stage in ('--permute', '--fill', '--morph', '--stats'):
            if stage in sys.argv and sys.argv.index('--help') < sys.argv.index(stage):
                # show help for that stage
                print_stage_help(stage.lstrip('-'))
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument('--help', action='store_true', help='show this help message')
    parser.add_argument('--input', '-i', help='input file (default stdin)')
    parser.add_argument('--output', '-o', help='output file (default stdout)')
    parser.add_argument('--log', help='log file (default toolchain.log)', default='toolchain.log')
    parser.add_argument('--permute', action='store_true', help='run permute stage')
    parser.add_argument('--fill', nargs='+', metavar='MASK', help='run fill_interstices stage with given masks')
    parser.add_argument('--morph', nargs='+', metavar='SPEC', help='run morph_caps stage with given specs')
    parser.add_argument('--stats', action='store_true', help='stats mode (no output, only stats)')
    args = parser.parse_args()
    # Top-level help
    if args.help:
        print(__doc__)
        sys.exit(0)
    return args


def build_pipeline(args):
    # Returns tuple (last_stdout, process_list)
    proc_list = []
    # Determine initial input
    if args.input:
        input_stream = open(args.input, 'r')
    else:
        input_stream = None  # means use stdin

    current_stdin = input_stream or sys.stdin
    # permute stage
    if args.permute:
        proc = subprocess.Popen(
            [PYTHON, os.path.join(UTIL_DIR, 'permute.py')],
            stdin=current_stdin, stdout=subprocess.PIPE, text=True)
        proc_list.append(proc)
        current_stdin = proc.stdout
    # fill stage
    if args.fill:
        proc = subprocess.Popen(
            [PYTHON, os.path.join(UTIL_DIR, 'fill_interstices.py')] + args.fill,
            stdin=current_stdin, stdout=subprocess.PIPE, text=True)
        proc_list.append(proc)
        current_stdin = proc.stdout
    # morph stage
    if args.morph:
        proc = subprocess.Popen(
            [PYTHON, os.path.join(UTIL_DIR, 'morph_caps.py')] + args.morph,
            stdin=current_stdin, stdout=subprocess.PIPE, text=True)
        proc_list.append(proc)
        current_stdin = proc.stdout

    return current_stdin, proc_list


def do_stats(input_stream):
    lines = [line.rstrip('\n') for line in input_stream]
    if not lines:
        print("No candidates generated.")
        return
    lengths = [len(line) for line in lines]
    print(f"Total candidates: {len(lines)}")
    print(f"Shortest length: {min(lengths)}")
    print(f"Longest length: {max(lengths)}")
    print(f"Average length: {mean(lengths):.2f}")


def main():
    args = parse_args()
    last_stream, procs = build_pipeline(args)

    # Stats mode
    if args.stats:
        do_stats(last_stream)
    else:
        # Logging setup
        logging.basicConfig(filename=args.log, level=logging.INFO,
                            format='%(asctime)s %(message)s')
        # Read and write output
        out_f = open(args.output, 'w') if args.output else sys.stdout
        count = 0
        for line in last_stream:
            out_f.write(line)
            count += 1
        if args.output:
            out_f.close()
        # Log the initial command, word count, and output filename
        cmd = ' '.join(sys.argv)
        logging.info(f"Command: {cmd}")
        logging.info(f"Candidates generated: {count}")
        logging.info(f"Output file: {args.output or 'stdout'}")

    # Wait for subprocesses to finish
    for p in procs:
        p.wait()

if __name__ == '__main__':
    main()
