"""Tokens of the DSL: the token kinds, the keyword table and the token value object."""

from __future__ import annotations

import enum
from dataclasses import dataclass
from types import MappingProxyType
from typing import Mapping


class TokenKind(enum.Enum):
    # layout
    NEWLINE = "NEWLINE"
    INDENT = "INDENT"
    DEDENT = "DEDENT"
    EOF = "EOF"
    # atoms
    IDENT = "IDENT"
    STRING = "STRING"
    ARROW = "→"
    COLON = ":"
    DOT = "."
    EQUALS = "="
    COMMA = ","
    LBRACKET = "["
    RBRACKET = "]"
    LPAREN = "("
    RPAREN = ")"
    ERROR = "ERROR"
    # keywords
    INPUT = "INPUT"
    LOOP = "LOOP"
    WHEN = "WHEN"
    FORK = "FORK"
    JOIN = "JOIN"
    BREAK = "BREAK"
    WAIT = "WAIT"
    STOP = "STOP"
    REQUIRE = "REQUIRE"
    DELEGATE = "DELEGATE"
    VERIFY = "VERIFY"
    EMIT = "EMIT"
    TRANSITION = "TRANSITION"
    HITL = "HITL"
    AUTO = "AUTO"
    FALLBACK = "FALLBACK"


KEYWORDS: Mapping[str, TokenKind] = MappingProxyType(
    {
        kind.value: kind
        for kind in (
            TokenKind.INPUT, TokenKind.LOOP, TokenKind.WHEN, TokenKind.FORK, TokenKind.JOIN,
            TokenKind.BREAK, TokenKind.WAIT, TokenKind.STOP, TokenKind.REQUIRE, TokenKind.DELEGATE,
            TokenKind.VERIFY, TokenKind.EMIT, TokenKind.TRANSITION, TokenKind.HITL, TokenKind.AUTO,
            TokenKind.FALLBACK,
        )
    }
)

PUNCTUATION: Mapping[str, TokenKind] = MappingProxyType(
    {
        "→": TokenKind.ARROW,
        ":": TokenKind.COLON,
        ".": TokenKind.DOT,
        "=": TokenKind.EQUALS,
        ",": TokenKind.COMMA,
        "[": TokenKind.LBRACKET,
        "]": TokenKind.RBRACKET,
        "(": TokenKind.LPAREN,
        ")": TokenKind.RPAREN,
    }
)


@dataclass(frozen=True)
class Token:
    """One token. `spaced` is true when whitespace separates it from the previous token on its line."""

    kind: TokenKind
    text: str
    line: int
    column: int
    spaced: bool = False

    @property
    def is_keyword(self) -> bool:
        return self.kind in KEYWORDS.values()

    @property
    def is_word(self) -> bool:
        """An identifier, or a keyword used where an identifier is expected."""
        return self.kind is TokenKind.IDENT or self.is_keyword
