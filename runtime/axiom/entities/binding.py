"""Binding resolution (`dsl.md`, Entities › Binding): a name refers to exactly one valid entity of the expected type."""

from __future__ import annotations

import enum
from dataclasses import dataclass

from axiom.entities.contracts import TypeCatalog
from axiom.entities.corpus import Corpus
from axiom.entities.model import Entity


class Failure(enum.Enum):
    NOT_FOUND = "no file declares the identity"
    AMBIGUOUS = "more than one file declares the identity"
    WRONG_TYPE = "the entity is of another type"
    INVALID = "the entity is not structurally valid"
    NO_TARGET = "the relation has no target"
    MANY_TARGETS = "the relation has more than one target"
    UNKNOWN_RELATION = "the type declares no such relation"


@dataclass(frozen=True)
class Resolution:
    entity: Entity | None
    failure: Failure | None = None
    detail: str = ""

    @property
    def satisfied(self) -> bool:
        return self.entity is not None


def resolve(corpus: Corpus, identity: str, type_name: str) -> Resolution:
    """`<name>:<Type> = <identity>`."""
    found = corpus.declaring(identity)
    if not found:
        return Resolution(None, Failure.NOT_FOUND, identity)
    if len(found) > 1:
        return Resolution(None, Failure.AMBIGUOUS, ", ".join(str(e.path) for e in found))
    entity = found[0]
    if entity.type_name != type_name:
        return Resolution(None, Failure.WRONG_TYPE, f"{identity} is a {entity.type_name or 'untyped entity'}, not a {type_name}")
    if not corpus.is_valid(entity):
        return Resolution(None, Failure.INVALID, "; ".join(d.message for d in corpus.problems[entity.path]))
    return Resolution(entity)


def resolve_relation(corpus: Corpus, catalog: TypeCatalog, source: Entity, relation: str, type_name: str) -> Resolution:
    """`<name>:<Type> = <bound>.<relation>`: the relation must have exactly one target."""
    etype = catalog.get(source.type_name)
    spec = next((r for r in etype.relations if r.name == relation), None) if etype else None
    if spec is None:
        return Resolution(None, Failure.UNKNOWN_RELATION, f"{source.type_name}.{relation}")
    targets = source.refs(spec.field)
    if not targets:
        return Resolution(None, Failure.NO_TARGET, f"{source.identity}.{relation}")
    if len(targets) > 1:
        return Resolution(None, Failure.MANY_TARGETS, f"{source.identity}.{relation} = {', '.join(targets)}")
    return resolve(corpus, targets[0], type_name)
