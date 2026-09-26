"""V2: BREAK outside a LOOP."""

from __future__ import annotations

from typing import Sequence

from axiom.dsl import nodes as n
from axiom.dsl.diagnostics import Report
from axiom.dsl.rules.base import NodeRule
from axiom.dsl.symbols import SymbolTable


class V2BreakOutsideLoop(NodeRule):
    id = "V2"

    def inspect(self, node: n.Node, path: Sequence[n.Node], symbols: SymbolTable, report: Report) -> None:
        if isinstance(node, n.Break) and not any(isinstance(a, n.Loop) for a in path):
            report.add(self.id, node.line, node.column, "BREAK is not inside a LOOP")
