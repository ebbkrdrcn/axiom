"""Differential test: `axiom entities check` and `axiom index` agree with `lab/tools/entitycheck.py` and `indexgen.py`.

Each case copies a real `docs/` tree, applies one mutation, and runs both implementations on it.
"""

from __future__ import annotations

import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Callable

import pytest

from axiom.entities import Project
from helpers import repo_root

ROOT = repo_root()
TOOLS = ROOT / "lab" / "tools"
SOURCES = [ROOT / "docs"] + sorted(ROOT.glob("lab/iterations/*/fixture/docs"))


def first(docs: Path, collection: str) -> Path:
    return sorted(p for p in (docs / collection).glob("*.md") if p.name != "_index.md")[0]


def edit(collection: str, old: str, new: str) -> Callable[[Path], None]:
    def apply(docs: Path) -> None:
        path = first(docs, collection)
        text = path.read_text()
        assert re.search(old, text, re.M), (path, old)
        path.write_text(re.sub(old, new, text, count=1, flags=re.M))
    return apply


def duplicate(docs: Path) -> None:
    src = first(docs, "tasks")
    shutil.copy(src, src.with_name("copy.md"))


def stale(docs: Path) -> None:
    index = docs / "tasks" / "_index.md"
    index.write_text(index.read_text().replace("|", "¦", 1) if index.exists() else "# tasks\n")


MUTATIONS: dict[str, Callable[[Path], None]] = {
    "unchanged": lambda docs: None,
    "missing field": edit("tasks", r"^status: .*\n", ""),
    "bad id format": edit("tasks", r"^id: TASK-(\d+)", r"id: TASK-\1\1"),
    "undeclared status": edit("tasks", r"^status: .*", "status: Started"),
    "missing section": edit("tasks", r"^## Description$", "## Summary"),
    "duplicate id": duplicate,
    "missing relation target": edit("tasks", r"^type: Task$", "type: Task\nadr: ADR-9999"),
    "wrong target type": edit("tasks", r"^type: Task$", "type: Task\nadr: TASK-0001"),
    "stale index": stale,
}


def reference(docs: Path) -> tuple[dict[str, bool], bool, bool, set[str], int]:
    run = subprocess.run([sys.executable, str(TOOLS / "entitycheck.py"), "--all", str(docs)], capture_output=True, text=True)
    files = {m[1]: m[2] == "VALID" for m in re.finditer(rf"^{re.escape(str(docs))}/(\S+) (VALID|INVALID)$", run.stdout, re.M)}
    stale_ = {str(Path(m[1]).relative_to(docs)) for m in re.finditer(r"^index out of date: (.+)$", run.stdout, re.M)}
    return files, "duplicate id" in run.stdout, "relation:" in run.stdout, stale_, run.returncode


def axiom(project_root: Path) -> tuple[dict[str, bool], bool, bool, set[str], int]:
    report = Project.open(project_root, ROOT, "docs").check()
    files = {str(p.relative_to("docs")): not problems for p, problems in report.files}
    stale_ = {str(p.relative_to("docs")) for p in report.stale_indexes}
    return files, bool(report.duplicates), bool(report.relations), stale_, 0 if report.valid else 1


@pytest.mark.parametrize("source", SOURCES, ids=lambda p: str(p.relative_to(ROOT)))
@pytest.mark.parametrize("mutation", list(MUTATIONS))
def test_same_verdicts_as_entitycheck(tmp_path: Path, source: Path, mutation: str) -> None:
    docs = tmp_path / "docs"
    shutil.copytree(source, docs)
    if not (docs / "tasks").is_dir():
        pytest.skip("no tasks collection")
    MUTATIONS[mutation](docs)
    assert axiom(tmp_path) == reference(docs)


@pytest.mark.parametrize("source", SOURCES, ids=lambda p: str(p.relative_to(ROOT)))
@pytest.mark.parametrize("prepare", ["as is", "no indexes", "new entity"])
def test_same_indexes_as_indexgen(tmp_path: Path, source: Path, prepare: str) -> None:
    trees = []
    for name in ("reference", "axiom"):
        docs = tmp_path / name / "docs"
        shutil.copytree(source, docs)
        if prepare == "no indexes":
            for index in docs.rglob("_index.md"):
                index.unlink()
        if prepare == "new entity" and (docs / "tasks").is_dir():
            duplicate(docs)
            copy = docs / "tasks" / "copy.md"
            copy.write_text(re.sub(r"^id: .*", "id: TASK-9999", copy.read_text(), count=1, flags=re.M))
        trees.append(docs)
    subprocess.run([sys.executable, str(TOOLS / "indexgen.py"), str(trees[0])], check=True)
    Project.open(trees[1].parent, ROOT, "docs").indexes().write()
    indexes = sorted(p.relative_to(trees[0]) for p in trees[0].rglob("_index.md"))
    assert indexes == sorted(p.relative_to(trees[1]) for p in trees[1].rglob("_index.md"))
    for rel in indexes:
        assert (trees[1] / rel).read_bytes() == (trees[0] / rel).read_bytes(), rel
