"""The entity core: type contracts, loading, structural validity, relations, bindings and indexes.

`Project` is the facade. It reads a project's files through an `EntityStore` (paths relative to the
project root) and the type contracts through a `TypeCatalog` (axiom's `rules/types/`).
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path, PurePosixPath

from axiom.entities.binding import Failure, Resolution, resolve, resolve_relation
from axiom.entities.contracts import EntityType, TypeCatalog
from axiom.entities.corpus import Corpus
from axiom.entities.diagnostics import Code, EntityDiagnostic
from axiom.entities.index import IndexGenerator
from axiom.entities.model import Entity
from axiom.entities.store import EntityStore, FileSystemStore, MemoryStore


def default_rules_root() -> Path:
    """Axiom's own repository root, which holds `rules/types/`."""
    return Path(__file__).resolve().parents[3]


@dataclass(frozen=True)
class CheckReport:
    files: tuple[tuple[PurePosixPath, tuple[EntityDiagnostic, ...]], ...]  # every entity file and its problems
    duplicates: tuple[EntityDiagnostic, ...]
    relations: tuple[EntityDiagnostic, ...]
    stale_indexes: tuple[PurePosixPath, ...]

    @property
    def valid(self) -> bool:
        return not (any(p for _, p in self.files) or self.duplicates or self.relations or self.stale_indexes)


class Project:
    def __init__(self, store: EntityStore, catalog: TypeCatalog, docs: PurePosixPath = PurePosixPath("docs")) -> None:
        self.store = store
        self.catalog = catalog
        self.docs = docs

    @classmethod
    def open(cls, root: Path, rules_root: Path | None = None, docs: str = "docs") -> Project:
        catalog = TypeCatalog(FileSystemStore(rules_root or default_rules_root()))
        return cls(FileSystemStore(root), catalog, PurePosixPath(docs))

    def corpus(self) -> Corpus:
        return Corpus.load(self.store, self.catalog, self.docs)

    def indexes(self) -> IndexGenerator:
        return IndexGenerator(self.store, self.catalog, self.docs)

    def check(self) -> CheckReport:
        corpus = self.corpus()
        files = tuple((e.path, corpus.problems[e.path]) for e in corpus.entities)
        return CheckReport(files, corpus.duplicates(), corpus.relation_problems(self.catalog), self.indexes().stale())

    def resolve(self, identity: str, type_name: str) -> Resolution:
        return resolve(self.corpus(), identity, type_name)

    def resolve_relation(self, source: Entity, relation: str, type_name: str) -> Resolution:
        return resolve_relation(self.corpus(), self.catalog, source, relation, type_name)


__all__ = [
    "CheckReport", "Code", "Corpus", "Entity", "EntityDiagnostic", "EntityStore", "EntityType", "Failure",
    "FileSystemStore", "IndexGenerator", "MemoryStore", "Project", "Resolution", "TypeCatalog",
    "default_rules_root", "resolve", "resolve_relation",
]
