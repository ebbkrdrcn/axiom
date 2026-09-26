"""V11: where and how inputs and bindings are written."""

from __future__ import annotations

from axiom.dsl import nodes as n
from axiom.dsl.diagnostics import Report
from axiom.dsl.rules.base import Rule
from axiom.dsl.symbols import SymbolTable
from axiom.dsl.visitor import walk


class V11Declarations(Rule):
    id = "V11"

    def check(self, program: n.Program, symbols: SymbolTable, report: Report) -> None:
        top_level = {id(c) for c in program.children}
        bound: set[str] = set()
        seen_binding = seen_other = False
        for node in walk(program):
            if isinstance(node, n.Invalid):
                continue
            if not isinstance(node, (n.Input, n.Binding)):
                seen_other = True
                continue
            at_top = id(node) in top_level and not node.arrow
            if isinstance(node, n.Input) and (not at_top or seen_other or seen_binding):
                report.add(self.id, node.line, node.column,
                           "an input must be at the top of the program, unindented, before bindings and other statements")
            if isinstance(node, n.Binding):
                seen_binding = True
                if not at_top or seen_other:
                    report.add(self.id, node.line, node.column,
                               "a binding must be at the top of the program, unindented, before other statements")
                if node.relation is not None and node.target not in bound:
                    report.add(self.id, node.line, node.column,
                               f"the relation starts from '{node.target}', which is not bound on an earlier line")
            if node.name in bound:
                report.add(self.id, node.line, node.column, f"name '{node.name}' is already bound")
            bound.add(node.name)
