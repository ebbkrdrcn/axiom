"""The DSL core: `check(source)` parses a program and applies the validity rules V1…V12.

Layers: tokens → lexer → parser (AST in `nodes`) → symbol table → rules (registry). `check` is the
facade over them. It never raises for a malformed program; every problem is a `Diagnostic`.
"""

from __future__ import annotations

from dataclasses import dataclass, replace

from axiom.dsl.diagnostics import Diagnostic
from axiom.dsl.lexer import Lexer
from axiom.dsl.nodes import Program
from axiom.dsl.parser import Parser
from axiom.dsl.rules import RuleRegistry, default_registry


@dataclass(frozen=True)
class CheckResult:
    program: Program
    diagnostics: tuple[Diagnostic, ...]

    @property
    def valid(self) -> bool:
        return not self.diagnostics

    @property
    def rule_ids(self) -> frozenset[str]:
        return frozenset(d.rule for d in self.diagnostics)


def parse(source: str) -> Program:
    """Parse a program. Malformed lines become `Invalid` nodes and `Program.issues`."""
    lexer = Lexer(source)
    parser = Parser(lexer.tokens(), source.split("\n"))
    program = parser.parse()
    return replace(program, issues=tuple(sorted(lexer.issues + list(program.issues), key=lambda i: (i.line, i.column))))


def check(source: str, registry: RuleRegistry | None = None) -> CheckResult:
    """Parse `source` and apply the validity rules."""
    program = parse(source)
    return CheckResult(program, (registry or default_registry()).check(program))


__all__ = ["CheckResult", "Diagnostic", "check", "parse"]
