"""V12: entity TRANSITIONs and text references use bound names; a bound name is not a HITL name."""

from __future__ import annotations

from axiom.dsl import nodes as n
from axiom.dsl.diagnostics import Report
from axiom.dsl.rules.base import Rule
from axiom.dsl.symbols import SymbolTable
from axiom.dsl.visitor import walk


class V12BoundNames(Rule):
    id = "V12"

    def check(self, program: n.Program, symbols: SymbolTable, report: Report) -> None:
        bound = symbols.bound
        for node in walk(program):
            if isinstance(node, n.EntityTransition) and node.name not in bound:
                report.add(self.id, node.line, node.column, f"TRANSITION on '{node.name}', which is not bound")
            if isinstance(node, n.Hitl):
                if node.name is not None and node.name in bound:
                    report.add(self.id, node.line, node.column, f"bound name '{node.name}' is used as a HITL name")
                for ref in node.text.references:
                    if ref.name not in bound:
                        report.add(self.id, ref.line, ref.column, f"the text refers to '{{{ref.name}}}', which is not bound")
