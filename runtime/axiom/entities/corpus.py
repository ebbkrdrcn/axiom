"""All entities of a project's `docs/`: loading, identity counts and relations."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import PurePosixPath
from types import MappingProxyType
from typing import Mapping

from axiom.entities.contracts import TypeCatalog
from axiom.entities.diagnostics import Code, EntityDiagnostic
from axiom.entities.model import Entity
from axiom.entities.store import EntityStore
from axiom.entities.validity import structural_problems

INDEX = "_index.md"


def collections(store: EntityStore, docs: PurePosixPath) -> tuple[str, ...]:
    """The directories directly under `docs/`, except hidden ones."""
    return tuple(d for d in store.list_dir(docs) if not d.startswith(".") and store.is_dir(docs / d))


@dataclass(frozen=True)
class Corpus:
    docs: PurePosixPath
    entities: tuple[Entity, ...]  # every Markdown file of every collection, except `_index.md`
    problems: Mapping[PurePosixPath, tuple[EntityDiagnostic, ...]]  # structural problems per file

    @classmethod
    def load(cls, store: EntityStore, catalog: TypeCatalog, docs: PurePosixPath = PurePosixPath("docs")) -> Corpus:
        entities = []
        for collection in collections(store, docs):
            for name in store.list_dir(docs / collection):
                path = docs / collection / name
                if name.endswith(".md") and name != INDEX and not store.is_dir(path):
                    entities.append(Entity.parse(path, store.read(path)))
        problems = {e.path: structural_problems(e, catalog) for e in entities}
        return cls(docs, tuple(entities), MappingProxyType(problems))

    def declaring(self, identity: str) -> tuple[Entity, ...]:
        """Every file whose `id` is `identity`. Identity comes only from the `id` field."""
        return tuple(e for e in self.entities if e.identity == identity)

    def is_valid(self, entity: Entity) -> bool:
        return not self.problems.get(entity.path)

    def duplicates(self) -> tuple[EntityDiagnostic, ...]:
        seen: dict[str, list[Entity]] = {}
        for e in self.entities:
            if e.identity:
                seen.setdefault(e.identity, []).append(e)
        return tuple(
            EntityDiagnostic(group[0].path, Code.DUPLICATE_ID,
                             f"duplicate id {identity}: {', '.join(str(e.path) for e in group)}")
            for identity, group in sorted(seen.items()) if len(group) > 1
        )

    def relation_problems(self, catalog: TypeCatalog) -> tuple[EntityDiagnostic, ...]:
        """Every relation field names existing entities of the declared target type."""
        out: list[EntityDiagnostic] = []
        for e in sorted(self.entities, key=lambda x: x.identity or ""):
            etype = catalog.get(e.type_name) if e.identity and e.type_name else None
            if etype is None:
                continue
            for rel in etype.relations:
                for ref in e.refs(rel.field):
                    targets = self.declaring(ref)
                    if not targets:
                        out.append(EntityDiagnostic(e.path, Code.MISSING_TARGET, f"{e.identity}: {rel.field} -> {ref} does not exist"))
                    elif targets[-1].type_name != rel.target:
                        out.append(EntityDiagnostic(e.path, Code.WRONG_TARGET_TYPE,
                                                    f"{e.identity}: {rel.field} -> {ref} is a {targets[-1].type_name}, not a {rel.target}"))
        return tuple(out)
