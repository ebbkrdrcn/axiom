"""Syntax issues: facts the lexer and parser record about malformed lines.

They are data, not diagnostics. The validity rules decide which rule each one breaks and report it.
"""

from __future__ import annotations

import enum
from dataclasses import dataclass


class IssueKind(enum.Enum):
    SYNTAX = "syntax"  # the line matches no statement form, or its indentation is malformed
    AUTO = "auto"  # AUTO is not immediately followed by a decision HITL
    BARE_FALLBACK = "bare-fallback"  # FALLBACK is written without its arrow


@dataclass(frozen=True)
class SyntaxIssue:
    line: int
    column: int
    kind: IssueKind
    message: str
