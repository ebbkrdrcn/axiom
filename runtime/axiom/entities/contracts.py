"""Type contracts: an Entity Type read from its `template.md`, `definition.md` and `representation.md`."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import PurePosixPath
from types import MappingProxyType
from typing import Mapping

from axiom.entities.formats import FieldFormat, parse_format
from axiom.entities.markdown import section, table
from axiom.entities.store import EntityStore


@dataclass(frozen=True)
class FieldSpec:
    name: str
    required: bool
    format: FieldFormat


@dataclass(frozen=True)
class SectionSpec:
    name: str
    required: bool
    needs_item: bool  # "yes, at least one item"


@dataclass(frozen=True)
class RelationSpec:
    name: str
    field: str
    target: str
    many: bool  # cardinality 0..n or 1..n


@dataclass(frozen=True)
class StatusSpec:
    name: str
    initial: bool
    terminal: bool


@dataclass(frozen=True)
class TransitionSpec:
    source: str
    target: str
    precondition: str  # parsed into typed preconditions by TASK-0020


@dataclass(frozen=True)
class EntityType:
    name: str
    fields: tuple[FieldSpec, ...]
    sections: tuple[SectionSpec, ...]
    relations: tuple[RelationSpec, ...]
    statuses: tuple[StatusSpec, ...]
    transitions: tuple[TransitionSpec, ...]
    collection: PurePosixPath | None  # e.g. docs/tasks, relative to the project root

    @property
    def status_names(self) -> tuple[str, ...]:
        return tuple(s.name for s in self.statuses)

    def field(self, name: str) -> FieldSpec | None:
        return next((f for f in self.fields if f.name == name), None)


def parse_type(name: str, template: str, definition: str, representation: str) -> EntityType:
    fields = tuple(FieldSpec(r[0], r[1] == "yes", parse_format(r[2])) for r in table(template, "Fields") if len(r) >= 3)
    sections = tuple(
        SectionSpec(r[0], r[1].startswith("yes"), "at least one item" in r[1]) for r in table(template, "Sections") if len(r) >= 2
    )
    relations = tuple(
        RelationSpec(r[0], r[1], r[2], r[3].endswith("n")) for r in table(template, "Relations") if len(r) >= 4
    )
    statuses = tuple(
        StatusSpec(m[1], "(initial)" in m[2], "(terminal)" in m[2])
        for m in re.finditer(r"^- (\w+)(.*)$", section(definition, "Statuses"), re.M)
    )
    transitions = tuple(TransitionSpec(r[0], r[1], r[2]) for r in table(definition, "Transitions") if len(r) >= 3)
    m = re.search(r"`(docs/[^`]+?)/?`", representation)
    collection = PurePosixPath(m[1]) if m else None
    return EntityType(name, fields, sections, relations, statuses, transitions, collection)


class TypeCatalog:
    """The Entity Types of a rulebook, found by name (case-insensitive) under `rules/types/<type>/`."""

    def __init__(self, store: EntityStore, root: PurePosixPath = PurePosixPath("rules/types")) -> None:
        types: dict[str, EntityType] = {}
        for directory in store.list_dir(root):
            base = root / directory
            files = [base / f for f in ("template.md", "definition.md", "representation.md")]
            if not all(store.exists(f) for f in files):
                continue
            template, definition, representation = (store.read(f) for f in files)
            m = re.search(r"^# (.+?) Template$", template, re.M)
            types[directory] = parse_type(m[1] if m else directory, template, definition, representation)
        self._types: Mapping[str, EntityType] = MappingProxyType(types)

    def get(self, name: str) -> EntityType | None:
        return self._types.get(name.lower())

    @property
    def names(self) -> tuple[str, ...]:
        return tuple(t.name for t in self._types.values())
