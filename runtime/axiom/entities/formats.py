"""Field formats of a Template (Strategy): each Format column value becomes a checker."""

from __future__ import annotations

import abc
import re
from dataclasses import dataclass

_DIGITS = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6}


class FieldFormat(abc.ABC):
    @abc.abstractmethod
    def problem(self, value: str) -> str | None:
        """None if `value` conforms, otherwise what is wrong with it."""


@dataclass(frozen=True)
class IdFormat(FieldFormat):
    prefix: str
    digits: int
    text: str

    def problem(self, value: str) -> str | None:
        if re.fullmatch(rf"{re.escape(self.prefix)}\d{{{self.digits}}}", value):
            return None
        return f"{value!r} does not match {self.text}"


@dataclass(frozen=True)
class LiteralFormat(FieldFormat):
    value: str

    def problem(self, value: str) -> str | None:
        return None if value == self.value else f"{value!r} is not `{self.value}`"


@dataclass(frozen=True)
class ChoiceFormat(FieldFormat):
    choices: tuple[str, ...]

    def problem(self, value: str) -> str | None:
        return None if value in self.choices else f"{value!r} is not one of {', '.join(self.choices)}"


@dataclass(frozen=True)
class DateFormat(FieldFormat):
    def problem(self, value: str) -> str | None:
        return None if re.fullmatch(r"\d{4}-\d{2}-\d{2}", value) else f"{value!r} is not a date (YYYY-MM-DD)"


@dataclass(frozen=True)
class UncheckedFormat(FieldFormat):
    """Statuses and relations are checked by their own rules; free-text formats are not checked."""

    text: str

    def problem(self, value: str) -> str | None:
        return None


def parse_format(text: str) -> FieldFormat:
    m = re.fullmatch(r"`([\w-]+-)` followed by (\w+) digits", text)
    if m and m[2] in _DIGITS:
        return IdFormat(m[1], _DIGITS[m[2]], text)
    if text == "`YYYY-MM-DD`":
        return DateFormat()
    choices = re.fullmatch(r"`(\w+)`(?: or `(\w+)`)*", text)
    if choices:
        values = tuple(re.findall(r"`(\w+)`", text))
        return LiteralFormat(values[0]) if len(values) == 1 else ChoiceFormat(values)
    return UncheckedFormat(text)
