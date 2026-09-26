"""Lexer: turns program text into tokens, with INDENT and DEDENT for the line structure.

Line structure follows `dsl.md`, Syntax › Indentation and scope: a line belongs to the nearest
preceding line that is indented less than it. Only relative depth matters, so a line may be a
sibling of a deeper line without matching its indentation exactly. The lexer keeps the chain of
open lines and, for each new line:

- emits INDENT when the line is a child of the previous line;
- otherwise emits one DEDENT for every block the line closes.

Blank lines produce no tokens. Tabs in indentation are reported as `SyntaxIssue`s, never raised.
"""

from __future__ import annotations

from typing import Iterator

from axiom.dsl.issues import IssueKind, SyntaxIssue
from axiom.dsl.tokens import KEYWORDS, PUNCTUATION, Token, TokenKind


def _is_ident_start(ch: str) -> bool:
    return ch.isascii() and ch.isalpha()


def _is_ident_char(ch: str) -> bool:
    return ch.isascii() and (ch.isalnum() or ch in "-_")


class Lexer:
    """Scans one program. `tokens()` is a generator; `issues` holds what it found malformed."""

    def __init__(self, source: str) -> None:
        self._source = source
        self.issues: list[SyntaxIssue] = []

    def tokens(self) -> Iterator[Token]:
        open_lines: list[int] = []  # indentation of each open line, outermost first
        line_no = 0
        for line_no, raw in enumerate(self._source.split("\n"), 1):
            if not raw.strip():
                continue
            content = raw.lstrip()
            indent = len(raw) - len(content)
            if "\t" in raw[:indent]:
                self.issues.append(SyntaxIssue(line_no, 1, IssueKind.SYNTAX, "tabs are not allowed in indentation"))
            yield from self._layout(open_lines, indent, line_no)
            yield from self._scan_line(content.rstrip(), line_no, indent + 1)
            yield Token(TokenKind.NEWLINE, "", line_no, len(raw) + 1)
        for _ in range(max(len(open_lines) - 1, 0)):
            yield Token(TokenKind.DEDENT, "", line_no + 1, 1)
        yield Token(TokenKind.EOF, "", line_no + 1, 1)

    @staticmethod
    def _layout(open_lines: list[int], indent: int, line_no: int) -> Iterator[Token]:
        closed = 0
        while open_lines and open_lines[-1] >= indent:
            open_lines.pop()
            closed += 1
        if open_lines and closed == 0:
            yield Token(TokenKind.INDENT, "", line_no, 1)
        for _ in range(closed - 1):
            yield Token(TokenKind.DEDENT, "", line_no, 1)
        open_lines.append(indent)

    def _scan_line(self, text: str, line_no: int, first_column: int) -> Iterator[Token]:
        i, spaced = 0, False
        while i < len(text):
            ch = text[i]
            column = first_column + i
            if ch == " " or ch == "\t":
                i, spaced = i + 1, True
                continue
            if _is_ident_start(ch):
                j = i + 1
                while j < len(text) and _is_ident_char(text[j]):
                    j += 1
                word = text[i:j]
                yield Token(KEYWORDS.get(word, TokenKind.IDENT), word, line_no, column, spaced)
                i = j
            elif ch == '"':
                end = text.find('"', i + 1)
                if end < 0:
                    yield Token(TokenKind.ERROR, text[i:], line_no, column, spaced)
                    return
                yield Token(TokenKind.STRING, text[i + 1:end], line_no, column, spaced)
                i = end + 1
            elif ch in PUNCTUATION:
                yield Token(PUNCTUATION[ch], ch, line_no, column, spaced)
                i += 1
            else:
                yield Token(TokenKind.ERROR, ch, line_no, column, spaced)
                i += 1
            spaced = False
