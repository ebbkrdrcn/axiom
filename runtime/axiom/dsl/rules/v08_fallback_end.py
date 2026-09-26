"""V8: a fallback flow ends with STOP or BREAK."""

from __future__ import annotations

from typing import Sequence

from axiom.dsl import nodes as n
from axiom.dsl.diagnostics import Report
from axiom.dsl.rules.base import NodeRule
from axiom.dsl.rules.shape import fallback_problem, items
from axiom.dsl.symbols import SymbolTable
from axiom.dsl.visitor import valid_children


class V8FallbackEnd(NodeRule):
    id = "V8"

    def inspect(self, node: n.Node, path: Sequence[n.Node], symbols: SymbolTable, report: Report) -> None:
        if not isinstance(node, n.Fallback) or fallback_problem(node):
            return  # a malformed FALLBACK is V1
        last = items(node)[-1]
        # the continuation lines of a simple item continue its flow; a compound item is the last statement
        continuation = valid_children(last)
        final = continuation[-1] if continuation and not isinstance(last, n.COMPOUND) else last
        if not isinstance(final, (n.Stop, n.Break)):
            report.add(self.id, node.line, node.column, "the fallback flow does not end with STOP or BREAK")
