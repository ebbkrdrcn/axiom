"""V5: AUTO must be immediately followed by a decision HITL on the same line."""

from __future__ import annotations

from axiom.dsl import nodes as n
from axiom.dsl.diagnostics import Report
from axiom.dsl.issues import IssueKind
from axiom.dsl.rules.base import Rule
from axiom.dsl.symbols import SymbolTable


class V5Auto(Rule):
    id = "V5"

    def check(self, program: n.Program, symbols: SymbolTable, report: Report) -> None:
        self.report_issues(program, IssueKind.AUTO, report)
