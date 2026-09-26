"""Recursive-descent parser for the DSL.

It mirrors the EBNF of `dsl.md`: a program is a block of lines, a line is an optional `→` and one
statement, and the lines indented under it (INDENT … DEDENT) are its children. Each statement form
has its own parse method, chosen by the statement's first token.

Recovery is panic mode at line granularity: a line that matches no statement form becomes an
`Invalid` node, its issue is recorded, and parsing resumes at the next line. The parser never
raises for malformed input.

Nesting is not restricted here. Which statement may have which children is decided by the validity
rules (V1, V4, V8, V9), so each violation is reported under the rule the spec assigns to it.
"""

from __future__ import annotations

import re
from dataclasses import replace
from types import MappingProxyType
from typing import Callable, Iterable, Mapping, Sequence

from axiom.dsl import nodes as n
from axiom.dsl.issues import IssueKind, SyntaxIssue
from axiom.dsl.tokens import Token, TokenKind

_REFERENCE = re.compile(r"\{([A-Za-z][A-Za-z0-9_-]*)\}")
_SIMPLE: Mapping[TokenKind, type[n.Node]] = MappingProxyType({
    TokenKind.FORK: n.Fork,
    TokenKind.JOIN: n.Join,
    TokenKind.BREAK: n.Break,
    TokenKind.WAIT: n.Wait,
    TokenKind.STOP: n.Stop,
})


class LineReader:
    """Cursor over the tokens of one line. The first failed expectation is kept in `error`."""

    def __init__(self, tokens: list[Token]) -> None:
        self._tokens = tokens
        self._pos = 0
        self.error: tuple[IssueKind, str] | None = None

    def peek(self, ahead: int = 0) -> Token:
        return self._tokens[min(self._pos + ahead, len(self._tokens) - 1)]

    def next(self) -> Token:
        token = self._tokens[self._pos]
        if token.kind is not TokenKind.NEWLINE:
            self._pos += 1
        return token

    def at(self, kind: TokenKind) -> bool:
        return self.peek().kind is kind

    def fail(self, message: str, kind: IssueKind = IssueKind.SYNTAX) -> None:
        if self.error is None:
            self.error = (kind, message)

    def _spacing_ok(self, token: Token, spaced: bool | None) -> bool:
        return spaced is None or token.spaced == spaced

    def expect(self, kind: TokenKind, spaced: bool | None = None) -> Token:
        """Consume a token of `kind`. `spaced` requires (True) or forbids (False) whitespace before it."""
        token = self.peek()
        if self.error is None and token.kind is kind and self._spacing_ok(token, spaced):
            return self.next()
        self.fail(f"expected {kind.value!r}")
        return token

    def word(self, spaced: bool | None = None) -> Token:
        """Consume an identifier. Keywords are accepted where a name is expected."""
        token = self.peek()
        if self.error is None and token.is_word and self._spacing_ok(token, spaced):
            return self.next()
        self.fail("expected a name")
        return token

    def end(self) -> None:
        if not self.at(TokenKind.NEWLINE):
            self.fail("unexpected text at the end of the statement")


class Parser:
    def __init__(self, tokens: Iterable[Token], lines: Sequence[str] = ()) -> None:
        self._tokens = list(tokens)
        self._lines = lines
        self._pos = 0
        self.issues: list[SyntaxIssue] = []
        self._statements: Mapping[TokenKind, Callable[[LineReader, Token, bool], n.Node | None]] = {
            TokenKind.INPUT: self._input,
            TokenKind.IDENT: self._binding,
            TokenKind.LOOP: self._loop,
            TokenKind.WHEN: self._when,
            TokenKind.REQUIRE: self._operation,
            TokenKind.DELEGATE: self._operation,
            TokenKind.VERIFY: self._operation,
            TokenKind.EMIT: self._operation,
            TokenKind.TRANSITION: self._transition,
            TokenKind.HITL: self._hitl,
            TokenKind.AUTO: self._auto,
            TokenKind.FALLBACK: self._fallback,
            **{kind: self._simple for kind in _SIMPLE},
        }

    # --- program structure ------------------------------------------------------------------------

    def parse(self) -> n.Program:
        children = self._block()
        return n.Program(line=0, column=0, children=children, issues=tuple(self.issues))

    def _peek(self) -> Token:
        return self._tokens[self._pos]

    def _advance(self) -> Token:
        token = self._tokens[self._pos]
        if token.kind is not TokenKind.EOF:
            self._pos += 1
        return token

    def _block(self) -> tuple[n.Node, ...]:
        lines: list[n.Node] = []
        while self._peek().kind not in (TokenKind.DEDENT, TokenKind.EOF):
            lines.append(self._line())
        return tuple(lines)

    def _line(self) -> n.Node:
        tokens: list[Token] = []
        while self._peek().kind is not TokenKind.NEWLINE:
            tokens.append(self._advance())
        tokens.append(self._advance())
        node = self._statement(tokens)
        if self._peek().kind is TokenKind.INDENT:
            self._advance()
            node = replace(node, children=self._block())
            if self._peek().kind is TokenKind.DEDENT:
                self._advance()
        return node

    def _statement(self, tokens: list[Token]) -> n.Node:
        reader = LineReader(tokens)
        start = reader.peek()
        arrow = reader.at(TokenKind.ARROW)
        if arrow:
            reader.next()
        first = reader.peek()
        method = self._statements.get(first.kind)
        if self._is_binding(reader):
            method = self._binding
        node = method(reader, start, arrow) if method else None
        if method is None:
            reader.fail("unrecognised statement")
        if node is None or reader.error is not None:
            kind, message = reader.error or (IssueKind.SYNTAX, "unrecognised statement")
            source = self._lines[start.line - 1].strip() if start.line <= len(self._lines) else ""
            self.issues.append(SyntaxIssue(start.line, start.column, kind, f"{message}: {source!r}"))
            return n.Invalid(line=start.line, column=start.column, arrow=arrow, source=source)
        return node

    @staticmethod
    def _is_binding(r: LineReader) -> bool:
        """`<name>:<Type> = …`; the name may be a keyword, for example `LOOP:Task = TASK-1`."""
        return r.peek().is_word and r.peek(1).kind is TokenKind.COLON and r.peek(3).kind is TokenKind.EQUALS

    # --- statements -------------------------------------------------------------------------------

    def _input(self, r: LineReader, start: Token, arrow: bool) -> n.Node | None:
        r.next()
        name = r.word(spaced=True)
        r.expect(TokenKind.COLON, spaced=False)
        type_ = r.word(spaced=False)
        r.end()
        return n.Input(line=start.line, column=start.column, arrow=arrow, name=name.text, type=type_.text)

    def _binding(self, r: LineReader, start: Token, arrow: bool) -> n.Node | None:
        name = r.word()
        r.expect(TokenKind.COLON, spaced=False)
        type_ = r.word(spaced=False)
        r.expect(TokenKind.EQUALS, spaced=True)
        target = r.word(spaced=True)
        relation: str | None = None
        if r.at(TokenKind.DOT):
            r.expect(TokenKind.DOT, spaced=False)
            relation = r.word(spaced=False).text
        r.end()
        return n.Binding(line=start.line, column=start.column, arrow=arrow,
                         name=name.text, type=type_.text, target=target.text, relation=relation)

    def _loop(self, r: LineReader, start: Token, arrow: bool) -> n.Node | None:
        r.next()
        r.expect(TokenKind.COLON, spaced=False)
        name = r.word(spaced=False)
        r.end()
        return n.Loop(line=start.line, column=start.column, arrow=arrow, name=name.text)

    def _when(self, r: LineReader, start: Token, arrow: bool) -> n.Node | None:
        r.next()
        subject = r.word(spaced=True)
        r.expect(TokenKind.DOT, spaced=False)
        outcome = r.word(spaced=False)
        r.end()
        return n.When(line=start.line, column=start.column, arrow=arrow, subject=subject.text, outcome=outcome.text)

    def _operation(self, r: LineReader, start: Token, arrow: bool) -> n.Node | None:
        keyword = r.next().kind
        arg = r.word(spaced=True).text
        r.end()
        line, column = start.line, start.column
        if keyword is TokenKind.REQUIRE:
            return n.Require(line=line, column=column, arrow=arrow, item=arg)
        if keyword is TokenKind.DELEGATE:
            return n.Delegate(line=line, column=column, arrow=arrow, work=arg)
        if keyword is TokenKind.VERIFY:
            return n.Verify(line=line, column=column, arrow=arrow, subject=arg)
        return n.Emit(line=line, column=column, arrow=arrow, artifact=arg)

    def _transition(self, r: LineReader, start: Token, arrow: bool) -> n.Node | None:
        r.next()
        name: Token | None = r.word(spaced=True) if r.peek().is_word else None
        value = r.expect(TokenKind.STRING, spaced=True)
        r.end()
        if r.error is None and (not value.text or "{" in value.text or "}" in value.text):
            r.fail("a state or status is a non-empty string without '{' or '}'")
        if name is None:
            return n.Transition(line=start.line, column=start.column, arrow=arrow, state=value.text)
        return n.EntityTransition(line=start.line, column=start.column, arrow=arrow,
                                  name=name.text, status=value.text)

    def _auto(self, r: LineReader, start: Token, arrow: bool) -> n.Node | None:
        r.next()
        hitl, colon = r.peek(), r.peek()
        if hitl.kind is TokenKind.HITL and hitl.spaced:
            r.next()
            colon = r.peek()
            if colon.kind is TokenKind.COLON and not colon.spaced:
                return self._decision(r, start, arrow, auto=True)
        r.fail("AUTO must be immediately followed by a decision HITL:<name>[…](…) on the same line", IssueKind.AUTO)
        return None

    def _hitl(self, r: LineReader, start: Token, arrow: bool) -> n.Node | None:
        r.next()
        if r.at(TokenKind.COLON):
            return self._decision(r, start, arrow, auto=False)
        text = self._text(r)
        r.end()
        return n.Hitl(line=start.line, column=start.column, arrow=arrow, text=text)

    def _decision(self, r: LineReader, start: Token, arrow: bool, auto: bool) -> n.Node | None:
        r.expect(TokenKind.COLON, spaced=False)
        name = r.word(spaced=False)
        r.expect(TokenKind.LBRACKET, spaced=False)
        answers: list[str] = []
        if not r.at(TokenKind.RBRACKET):
            answers.append(r.word().text)
            while r.error is None and r.at(TokenKind.COMMA):
                r.next()
                answers.append(r.word().text)
        if r.error is None and not r.at(TokenKind.RBRACKET):
            r.fail("malformed answer list")
        r.expect(TokenKind.RBRACKET)
        text = self._text(r)
        r.end()
        return n.Hitl(line=start.line, column=start.column, arrow=arrow,
                      name=name.text, answers=tuple(answers), auto=auto, text=text)

    def _text(self, r: LineReader) -> n.Text:
        r.expect(TokenKind.LPAREN, spaced=False)
        string = r.expect(TokenKind.STRING, spaced=False)
        r.expect(TokenKind.RPAREN, spaced=False)
        references = tuple(
            n.Reference(m[1], string.line, string.column + 1 + m.start()) for m in _REFERENCE.finditer(string.text)
        )
        rest = _REFERENCE.sub("", string.text)
        if r.error is None and ("{" in rest or "}" in rest):
            r.fail("'{' and '}' in a text must enclose a name")
        return n.Text(string.text, references, string.line, string.column)

    def _fallback(self, r: LineReader, start: Token, arrow: bool) -> n.Node | None:
        r.next()
        r.end()
        if not arrow and r.error is None:
            r.fail("FALLBACK must be written as '→ FALLBACK'", IssueKind.BARE_FALLBACK)
        return n.Fallback(line=start.line, column=start.column, arrow=arrow)

    def _simple(self, r: LineReader, start: Token, arrow: bool) -> n.Node | None:
        cls = _SIMPLE[r.next().kind]
        r.end()
        return cls(line=start.line, column=start.column, arrow=arrow)
