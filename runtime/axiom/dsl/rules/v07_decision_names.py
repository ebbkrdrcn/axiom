"""V7: decision names and answer lists."""

from __future__ import annotations

from axiom.dsl import nodes as n
from axiom.dsl.diagnostics import Report
from axiom.dsl.rules.base import Rule
from axiom.dsl.symbols import SymbolTable


class V7DecisionNames(Rule):
    id = "V7"

    def check(self, program: n.Program, symbols: SymbolTable, report: Report) -> None:
        seen: set[str] = set()
        for h in symbols.decisions:
            assert h.name is not None
            if h.name in seen:
                report.add(self.id, h.line, h.column, f"HITL name '{h.name}' is used twice")
            seen.add(h.name)
            if not h.answers or len(set(h.answers)) != len(h.answers):
                report.add(self.id, h.line, h.column, "the answer list is empty or repeats an answer")
            if h.name in symbols.verified:
                report.add(self.id, h.line, h.column, f"name '{h.name}' is used by both a HITL and a VERIFY")
