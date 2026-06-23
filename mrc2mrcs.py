#!/usr/bin/env python3
"""
fix_restacked_mrcs.py

In a whitespace-separated RELION STAR file, change every column-1 (the first
field of each line) value that ends in 'restacked.mrc' so that it ends in
'restacked.mrcs' instead.

Only the FIRST column is ever modified. All other columns (e.g. the
_rlnMicrographName '..._doseweighted.mrc' entries), header lines, blank lines,
and the original whitespace/formatting are left exactly as they were.

Usage:
    python3 fix_restacked_mrcs.py <input.star> [output.star]

If no output path is given, the file is edited in place and a '.bak' backup of
the original is written next to it.
"""

import re
import shutil
import sys

# Matches: (leading whitespace)(first token)(rest of line, incl. trailing newline)
LINE_RE = re.compile(r"^(\s*)(\S+)(.*)$", re.DOTALL)


def fix_line(line: str) -> str:
    m = LINE_RE.match(line)
    if not m:
        # Blank line or whitespace-only line: leave untouched.
        return line
    leading, first, rest = m.groups()
    if first.endswith("restacked.mrc"):
        first = first + "s"  # restacked.mrc -> restacked.mrcs
    return leading + first + rest


def main() -> int:
    if len(sys.argv) not in (2, 3):
        sys.stderr.write(
            "Usage: python3 fix_restacked_mrcs.py <input.star> [output.star]\n"
        )
        return 2

    in_path = sys.argv[1]
    out_path = sys.argv[2] if len(sys.argv) == 3 else in_path

    # If editing in place, back up the original first.
    if out_path == in_path:
        shutil.copy2(in_path, in_path + ".bak")

    changed = 0
    with open(in_path, "r") as fin:
        lines = fin.readlines()

    new_lines = []
    for line in lines:
        new_line = fix_line(line)
        if new_line != line:
            changed += 1
        new_lines.append(new_line)

    with open(out_path, "w") as fout:
        fout.writelines(new_lines)

    sys.stderr.write(
        f"Done. {changed} column-1 value(s) changed to restacked.mrcs -> {out_path}\n"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())