"""V1: indentation and statement forms."""

from __future__ import annotations

from typing import Sequence

from axiom.dsl import nodes as n
from axiom.dsl.diagnostics import Report
from axiom.dsl.issues import IssueKind
from axiom.dsl.rules.base import NodeRule
from axiom.dsl.rules.shape import fallback_problem, fallbacks, is_fallback_host, is_simple, items, plain
from axiom.dsl.symbols import SymbolTable
from axiom.dsl.visitor import valid_children


class V1Structure(NodeRule):
    id = "V1"

    def check(self, program: n.Program, symbols: SymbolTable, report: Report) -> None:
        self.report_issues(program, IssueKind.SYNTAX, report)
        super().check(program, symbols, report)

    def inspect(self, node: n.Node, path: Sequence[n.Node], symbols: SymbolTable, report: Report) -> None:
        def add(message: str) -> None:
            report.add(self.id, node.line, node.column, message)

        if isinstance(node, n.Loop) and not valid_children(node):
            add("LOOP has an empty body")
        elif isinstance(node, n.When) and (not items(node) or plain(node) or fallbacks(node)):
            add("WHEN must contain only '→' items (at least one)")
        elif isinstance(node, n.Fork) and (plain(node) or fallbacks(node)):
            add("FORK must contain only '→' branches")
        elif is_fallback_host(node) and plain(node):
            add(f"{type(node).__name__.upper()} may only contain '→ FALLBACK'")
        elif isinstance(node, n.Fallback) and fallback_problem(node):
            add("FALLBACK must contain only '→' items (at least one)")
        elif is_simple(node) and valid_children(node) and not node.arrow:
            add("this statement cannot have indented children")
