"""Command line: `axiom check [--md] FILE…`, `axiom entities check [DOCS]` and `axiom index [--check] [DOCS]`.

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
from axiom.entities import Project

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


def _check_entities(project: Project, out: TextIO) -> int:
    report = project.check()
    for path, problems in report.files:
        print(f"{path} {'INVALID' if problems else 'VALID'}", file=out)
        for d in problems:
            print(f"    {d.message}", file=out)
    for d in report.duplicates:
        print(d.message, file=out)
    for d in report.relations:
        print(f"relation: {d.message}", file=out)
    for p in report.stale_indexes:
        print(f"index out of date: {p}", file=out)
    return 0 if report.valid else 1


def _index(project: Project, check_only: bool, out: TextIO) -> int:
    if check_only:
        stale = project.indexes().stale()
        for p in stale:
            print(f"index out of date: {p}", file=out)
        return 1 if stale else 0
    for p in project.indexes().write():
        print(f"wrote {p}", file=out)
    return 0


def main(argv: list[str], out: TextIO = sys.stdout) -> int:
    parser = argparse.ArgumentParser(prog="axiom")
    commands = parser.add_subparsers(dest="command", required=True)
    check = commands.add_parser("check", help="check DSL programs against the validity rules V1…V12")
    check.add_argument("--md", action="store_true", help="check the ```text and ```invalid blocks of markdown files")
    check.add_argument("files", nargs="+")
    entities = commands.add_parser("entities", help="entity operations")
    entity_commands = entities.add_subparsers(dest="entity_command", required=True)
    entity_check = entity_commands.add_parser("check", help="check every entity, relation and index under DOCS")
    index = commands.add_parser("index", help="generate the _index.md files under DOCS")
    index.add_argument("--check", action="store_true", help="only report indexes that are out of date")
    for sub in (entity_check, index):
        sub.add_argument("docs", nargs="?", default="docs", help="the docs directory, relative to --project (default: docs)")
        sub.add_argument("--project", default=".", help="the project root (default: the current directory)")
        sub.add_argument("--rules", default=None, help="axiom's root, which holds rules/types/ (default: this installation)")
    args = parser.parse_args(argv)
    if args.command in ("entities", "index"):
        project = Project.open(Path(args.project), Path(args.rules) if args.rules else None, args.docs)
        return _check_entities(project, out) if args.command == "entities" else _index(project, args.check, out)
    if args.md:
        return _check_markdown(args.files, out)
    return _check_files(args.files, out)


def main_entry() -> None:
    """Console-script entry point."""
    sys.exit(main(sys.argv[1:]))
