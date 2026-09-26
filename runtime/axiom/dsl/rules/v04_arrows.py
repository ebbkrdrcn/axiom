"""V4: placement of `→` items and of `→ FALLBACK`."""

from __future__ import annotations

from typing import Sequence

from axiom.dsl import nodes as n
from axiom.dsl.diagnostics import Report
from axiom.dsl.issues import IssueKind
from axiom.dsl.rules.base import NodeRule
from axiom.dsl.rules.shape import fallbacks, is_fallback_host, is_flow_host, items
from axiom.dsl.symbols import SymbolTable


class V4Arrows(NodeRule):
    id = "V4"

    def check(self, program: n.Program, symbols: SymbolTable, report: Report) -> None:
        self.report_issues(program, IssueKind.BARE_FALLBACK, report)
        super().check(program, symbols, report)

    def inspect(self, node: n.Node, path: Sequence[n.Node], symbols: SymbolTable, report: Report) -> None:
        parent = path[-1]
        if isinstance(parent, n.Invalid):
            return  # the line above could not be read, so its children cannot be judged
        if isinstance(node, n.Fallback):
            if not is_fallback_host(parent):
                report.add(self.id, node.line, node.column,
                           "'→ FALLBACK' is not directly under HITL, REQUIRE, VERIFY or TRANSITION <name>")
        elif node.arrow and not is_flow_host(parent):
            report.add(self.id, node.line, node.column, "'→' item is not under WHEN, FORK or FALLBACK")
        if is_fallback_host(node):
            if items(node):
                report.add(self.id, node.line, node.column, f"{type(node).__name__.upper()} may only contain '→ FALLBACK'")
            if len(fallbacks(node)) > 1:
                report.add(self.id, node.line, node.column, "more than one FALLBACK")
