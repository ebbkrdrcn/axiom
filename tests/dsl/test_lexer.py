from axiom.dsl.issues import IssueKind
from axiom.dsl.lexer import Lexer
from axiom.dsl.tokens import TokenKind as K


def kinds(source: str) -> list[K]:
    return [t.kind for t in Lexer(source).tokens()]


def test_statement_tokens_and_keywords() -> None:
    tokens = list(Lexer('HITL:merge[yes, no]("Merge {t}?")').tokens())
    assert [t.kind for t in tokens] == [
        K.HITL, K.COLON, K.IDENT, K.LBRACKET, K.IDENT, K.COMMA, K.IDENT, K.RBRACKET,
        K.LPAREN, K.STRING, K.RPAREN, K.NEWLINE, K.EOF,
    ]
    assert tokens[9].text == "Merge {t}?"


def test_positions_and_spacing() -> None:
    tokens = list(Lexer("t1:Task = TASK-0001.adr").tokens())
    assert [(t.text, t.column, t.spaced) for t in tokens[:6]] == [
        ("t1", 1, False), (":", 3, False), ("Task", 4, False), ("=", 9, True), ("TASK-0001", 11, True), (".", 20, False),
    ]


def test_arrow_is_a_token() -> None:
    assert kinds("→ STOP") == [K.ARROW, K.STOP, K.NEWLINE, K.EOF]


def test_indent_and_dedent_follow_nesting() -> None:
    source = "LOOP:a\n  VERIFY x\n    → FALLBACK\n        → STOP\nSTOP\n"
    layout = [k for k in kinds(source) if k in (K.INDENT, K.DEDENT, K.NEWLINE, K.EOF)]
    assert layout == [
        K.NEWLINE, K.INDENT, K.NEWLINE, K.INDENT, K.NEWLINE, K.INDENT, K.NEWLINE,
        K.DEDENT, K.DEDENT, K.DEDENT, K.NEWLINE, K.EOF,
    ]


def test_only_relative_depth_matters() -> None:
    # line 3 is indented less than line 2 but more than line 1: it is line 2's sibling (Indentation rule 2)
    source = "LOOP:a\n    DELEGATE x\n  STOP\n"
    layout = [k for k in kinds(source) if k in (K.INDENT, K.DEDENT)]
    assert layout == [K.INDENT, K.DEDENT]


def test_blank_lines_produce_no_tokens() -> None:
    assert kinds("STOP\n\n   \nSTOP") == [K.STOP, K.NEWLINE, K.STOP, K.NEWLINE, K.EOF]


def test_tabs_in_indentation_are_an_issue_not_an_exception() -> None:
    lexer = Lexer("LOOP:a\n\tSTOP")
    list(lexer.tokens())
    assert [(i.line, i.kind) for i in lexer.issues] == [(2, IssueKind.SYNTAX)]


def test_unterminated_string_and_unknown_characters_are_error_tokens() -> None:
    assert K.ERROR in kinds('HITL("open')
    assert K.ERROR in kinds("DELEGATE a$b")
