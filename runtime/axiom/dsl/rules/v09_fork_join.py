"""V9: every JOIN has a FORK, and every FORK has at least two branches."""

from __future__ import annotations

from typing import Sequence

from axiom.dsl import nodes as n
from axiom.dsl.diagnostics import Report
from axiom.dsl.rules.base import NodeRule
from axiom.dsl.rules.forks import open_forks_before
from axiom.dsl.rules.shape import items
from axiom.dsl.symbols import SymbolTable


class V9ForkJoin(NodeRule):
    id = "V9"

    def inspect(self, node: n.Node, path: Sequence[n.Node], symbols: SymbolTable, report: Report) -> None:
        if isinstance(node, n.Fork) and len(items(node)) < 2:
            report.add(self.id, node.line, node.column, "FORK has fewer than two branches")
        if isinstance(node, n.Join) and not open_forks_before(node, path[-1]):
            report.add(self.id, node.line, node.column, "JOIN has no corresponding FORK")
