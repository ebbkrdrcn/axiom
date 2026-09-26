"""V10: a WHEN does not test an outcome of a FORK branch before that FORK is joined."""

from __future__ import annotations

from typing import Sequence

from axiom.dsl import nodes as n
from axiom.dsl.diagnostics import Report
from axiom.dsl.rules.base import NodeRule
from axiom.dsl.rules.forks import open_forks_before
from axiom.dsl.symbols import SymbolTable
from axiom.dsl.visitor import walk


class V10WhenBeforeJoin(NodeRule):
    id = "V10"

    def inspect(self, node: n.Node, path: Sequence[n.Node], symbols: SymbolTable, report: Report) -> None:
        if not isinstance(node, n.When):
            return
        for fork in open_forks_before(node, path[-1]):
            established = {x.subject for x in walk(fork) if isinstance(x, n.Verify)}
            established |= {x.name for x in walk(fork) if isinstance(x, n.Hitl) and x.name}
            if node.subject in established:
                report.add(self.id, node.line, node.column,
                           f"WHEN tests '{node.subject}' before the FORK at line {fork.line} is joined",
                           hint="add a JOIN between the FORK and the WHEN")
