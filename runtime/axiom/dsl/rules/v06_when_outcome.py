"""V6: a WHEN tests an outcome that the program can establish."""

from __future__ import annotations

from typing import Sequence

from axiom.dsl import nodes as n
from axiom.dsl.diagnostics import Report
from axiom.dsl.rules.base import NodeRule
from axiom.dsl.symbols import SymbolTable


class V6WhenOutcome(NodeRule):
    id = "V6"

    def inspect(self, node: n.Node, path: Sequence[n.Node], symbols: SymbolTable, report: Report) -> None:
        if not isinstance(node, n.When):
            return
        s, o = node.subject, node.outcome
        by_verify = s in symbols.verified and o in ("accepted", "rejected")
        by_decision = o in symbols.answers.get(s, ())
        if not (by_verify or by_decision):
            report.add(self.id, node.line, node.column, f"WHEN {s}.{o} refers to an outcome the program cannot produce",
                       hint=f"add VERIFY {s} or a HITL:{s}[…] that lists {o}")
