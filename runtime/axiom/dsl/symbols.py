"""Symbol table: the names a program declares and the subjects it establishes outcomes for."""

from __future__ import annotations

from dataclasses import dataclass
from types import MappingProxyType
from typing import Mapping

from axiom.dsl import nodes as n
from axiom.dsl.visitor import walk


@dataclass(frozen=True)
class SymbolTable:
    declarations: tuple[n.Input | n.Binding, ...]  # every input and binding, in source order
    verified: frozenset[str]  # subjects of a VERIFY
    decisions: tuple[n.Hitl, ...]  # every HITL with a name, in source order

    @property
    def bound(self) -> frozenset[str]:
        return frozenset(d.name for d in self.declarations)

    @property
    def answers(self) -> Mapping[str, tuple[str, ...]]:
        """Answers of each decision name; for a repeated name, the last one (the repeat is V7)."""
        return MappingProxyType({h.name: h.answers for h in self.decisions if h.name is not None})

    @classmethod
    def build(cls, program: n.Program) -> SymbolTable:
        declarations: list[n.Input | n.Binding] = []
        verified: set[str] = set()
        decisions: list[n.Hitl] = []
        for node in walk(program):
            if isinstance(node, (n.Input, n.Binding)):
                declarations.append(node)
            elif isinstance(node, n.Verify):
                verified.add(node.subject)
            elif isinstance(node, n.Hitl) and node.name is not None:
                decisions.append(node)
        return cls(tuple(declarations), frozenset(verified), tuple(decisions))
