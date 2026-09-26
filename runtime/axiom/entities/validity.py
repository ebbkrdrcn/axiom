"""Structural validity of one entity against its Template (Entity Model, Template › Structural Validity)."""

from __future__ import annotations

from axiom.entities.contracts import TypeCatalog
from axiom.entities.diagnostics import Code, EntityDiagnostic
from axiom.entities.markdown import has_list_item
from axiom.entities.model import Entity


def structural_problems(entity: Entity, catalog: TypeCatalog) -> tuple[EntityDiagnostic, ...]:
    out: list[EntityDiagnostic] = []

    def add(code: Code, message: str) -> None:
        out.append(EntityDiagnostic(entity.path, code, message))

    if entity.fields is None:
        add(Code.NO_FRONT_MATTER, "no front matter")
        return tuple(out)
    etype = catalog.get(entity.type_name) if entity.type_name else None
    if etype is None:
        add(Code.UNKNOWN_TYPE, f"unknown type {entity.type_name!r}")
        return tuple(out)
    for spec in etype.fields:
        value = entity.fields.get(spec.name, "")
        if not value:
            if spec.required:
                add(Code.MISSING_FIELD, f"missing field {spec.name}")
            continue
        problem = spec.format.problem(value)
        if problem:
            add(Code.BAD_FORMAT, f"{spec.name} {problem}")
    if entity.status not in etype.status_names:
        add(Code.UNDECLARED_STATUS, f"status {entity.status!r} not declared ({', '.join(etype.status_names)})")
    for sec in etype.sections:
        if sec.name not in entity.sections:
            if sec.required:
                add(Code.MISSING_SECTION, f"missing section {sec.name}")
        elif sec.needs_item and not has_list_item(entity.sections[sec.name]):
            add(Code.EMPTY_SECTION, f"section {sec.name} has no item")
    for rel in etype.relations:
        if not rel.many and len(entity.refs(rel.field)) > 1:
            add(Code.TOO_MANY_TARGETS, f"{rel.field} has more than one target")
    return tuple(out)
