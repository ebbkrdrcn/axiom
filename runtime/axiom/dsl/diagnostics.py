"""Diagnostics (Notification pattern): checks add problems to a `Report` and return it; nothing is raised."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, order=True)
class Diagnostic:
    line: int
    column: int
    rule: str  # a validity rule id, for example "V6"
    message: str
    hint: str = ""

    def __str__(self) -> str:
        text = f"line {self.line}: {self.rule}: {self.message}"
        return f"{text} (hint: {self.hint})" if self.hint else text


class Report:
    """Collects the diagnostics of one check."""

    def __init__(self) -> None:
        self._items: list[Diagnostic] = []

    def add(self, rule: str, line: int, column: int, message: str, hint: str = "") -> None:
        self._items.append(Diagnostic(line, column, rule, message, hint))

    @property
    def diagnostics(self) -> tuple[Diagnostic, ...]:
        return tuple(sorted(self._items))
