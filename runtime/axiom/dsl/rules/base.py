"""Rule base classes (Strategy) and the rule registry."""

from __future__ import annotations

import abc
from typing import Callable, ClassVar, Sequence

from axiom.dsl import nodes as n
from axiom.dsl.diagnostics import Diagnostic, Report
from axiom.dsl.issues import IssueKind
from axiom.dsl.symbols import SymbolTable
from axiom.dsl.visitor import Visitor


class Rule(abc.ABC):
    """One validity rule of `dsl.md` (V1…V12). A rule reports only under its own id."""

    id: ClassVar[str]

    @abc.abstractmethod
    def check(self, program: n.Program, symbols: SymbolTable, report: Report) -> None: ...

    def report_issues(self, program: n.Program, kind: IssueKind, report: Report) -> None:
        """Report the parser's syntax issues of `kind` under this rule."""
        for issue in program.issues:
            if issue.kind is kind:
                report.add(self.id, issue.line, issue.column, issue.message)


class _Walker(Visitor):
    def __init__(self, callback: Callable[[n.Node, Sequence[n.Node]], None]) -> None:
        super().__init__()
        self._callback = callback

    def generic_visit(self, node: n.Node) -> None:
        if not isinstance(node, (n.Program, n.Invalid)):
            self._callback(node, tuple(self.path))
        super().generic_visit(node)


class NodeRule(Rule):
    """A rule that inspects every readable node together with its ancestors (outermost first)."""

    def check(self, program: n.Program, symbols: SymbolTable, report: Report) -> None:
        _Walker(lambda node, path: self.inspect(node, path, symbols, report)).visit(program)

    @abc.abstractmethod
    def inspect(self, node: n.Node, path: Sequence[n.Node], symbols: SymbolTable, report: Report) -> None: ...


class RuleRegistry:
    """The rules a check applies. Rule ids are unique."""

    def __init__(self, rules: Sequence[Rule]) -> None:
        ids = [rule.id for rule in rules]
        if len(set(ids)) != len(ids):
            raise ValueError(f"duplicate rule ids in {ids}")  # a programming error, not a user problem
        self._rules = tuple(rules)

    @property
    def ids(self) -> tuple[str, ...]:
        return tuple(rule.id for rule in self._rules)

    def check(self, program: n.Program) -> tuple[Diagnostic, ...]:
        symbols = SymbolTable.build(program)
        report = Report()
        for rule in self._rules:
            rule.check(program, symbols, report)
        return report.diagnostics
