"""An in-memory project with axiom's real type contracts."""

from __future__ import annotations

from pathlib import Path, PurePosixPath

from axiom.entities import FileSystemStore, MemoryStore, Project, TypeCatalog, default_rules_root

CATALOG = TypeCatalog(FileSystemStore(default_rules_root()))


def task(identity: str, status: str = "Todo", extra: str = "", body: str | None = None) -> str:
    body = body if body is not None else "## Description\n\nWork.\n\n## Acceptance Criteria\n\n- It works.\n"
    return f"---\nid: {identity}\ntype: Task\nstatus: {status}\n{extra}---\n# Title of {identity}\n\n{body}"


def adr(identity: str, status: str = "Proposed") -> str:
    return (f"---\nid: {identity}\ntype: ADR\nstatus: {status}\ndate: 2026-09-26\n---\n# {identity}\n\n"
            "## Context\n\nC.\n\n## Decision\n\nD.\n\n## Consequences\n\nQ.\n")


def project(files: dict[str, str]) -> Project:
    return Project(MemoryStore(files), CATALOG, PurePosixPath("docs"))


def repo_root() -> Path:
    return default_rules_root()
