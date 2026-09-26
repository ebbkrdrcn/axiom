"""V3: BREAK inside a FORK branch that would leave a LOOP outside the branch."""

from __future__ import annotations

from typing import Sequence

from axiom.dsl import nodes as n
from axiom.dsl.diagnostics import Report
from axiom.dsl.rules.base import NodeRule
from axiom.dsl.symbols import SymbolTable


class V3BreakAcrossFork(NodeRule):
    id = "V3"

    def inspect(self, node: n.Node, path: Sequence[n.Node], symbols: SymbolTable, report: Report) -> None:
        if not isinstance(node, n.Break):
            return
        # walk outwards from the BREAK to its innermost LOOP; a FORK branch on the way is crossed
        chain = [*path, node]
        for i in range(len(chain) - 1, 0, -1):
            current, parent = chain[i], chain[i - 1]
            if isinstance(parent, n.Loop):
                return
            if current.arrow and isinstance(parent, n.Fork) and self._loop_outside(chain[:i]):
                report.add(self.id, node.line, node.column, "BREAK inside a FORK branch leaves a LOOP outside it")
                return

    @staticmethod
    def _loop_outside(outer: Sequence[n.Node]) -> bool:
        return any(isinstance(a, n.Loop) for a in outer)
