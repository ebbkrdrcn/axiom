"""Command line: `axiom check FILE…` and `axiom check --md FILE…`.

`--md` checks the fenced blocks of a markdown file: a ```text block must be valid and an
```invalid block must be invalid. Paths are printed as given.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import TextIO

from axiom import dsl

_BLOCK = re.compile(r"```(text|invalid)\n(.*?)```", re.S)


def _check_files(paths: list[str], out: TextIO) -> int:
    rc = 0
    for path in paths:
        result = dsl.check(Path(path).read_text(encoding="utf-8"))
        print(f"{path} {'VALID' if result.valid else 'INVALID'}", file=out)
        for d in result.diagnostics:
            print(f"    {d}", file=out)
        rc |= not result.valid
    return rc


def _check_markdown(paths: list[str], out: TextIO) -> int:
    rc = 0
    for path in paths:
        for tag, block in _BLOCK.findall(Path(path).read_text(encoding="utf-8")):
            result = dsl.check(block)
            good = (tag == "text") == result.valid
            rc |= not good
            first = block.strip().split("\n")[0]
            print(f"{'ok  ' if good else 'FAIL'} {path} [{tag}] {first[:60]}", file=out)
            for d in result.diagnostics:
                print(f"      {d}", file=out)
    return rc


def main(argv: list[str], out: TextIO = sys.stdout) -> int:
    parser = argparse.ArgumentParser(prog="axiom")
    commands = parser.add_subparsers(dest="command", required=True)
    check = commands.add_parser("check", help="check DSL programs against the validity rules V1…V12")
    check.add_argument("--md", action="store_true", help="check the ```text and ```invalid blocks of markdown files")
    check.add_argument("files", nargs="+")
    args = parser.parse_args(argv)
    if args.md:
        return _check_markdown(args.files, out)
    return _check_files(args.files, out)


def main_entry() -> None:
    """Console-script entry point."""
    sys.exit(main(sys.argv[1:]))
