import dataclasses

import pytest

from axiom.dsl import nodes as n
from axiom.dsl import parse
from axiom.dsl.issues import IssueKind


def only(source: str) -> n.Node:
    program = parse(source)
    assert len(program.children) == 1
    return program.children[0]


@pytest.mark.parametrize(
    "source, expected",
    [
        ("INPUT t:Task", n.Input(line=1, column=1, name="t", type="Task")),
        ("t:Task = TASK-0001", n.Binding(line=1, column=1, name="t", type="Task", target="TASK-0001")),
        ("a:ADR = t.adr", n.Binding(line=1, column=1, name="a", type="ADR", target="t", relation="adr")),
        ("REQUIRE repo", n.Require(line=1, column=1, item="repo")),
        ("DELEGATE build", n.Delegate(line=1, column=1, work="build")),
        ("VERIFY build", n.Verify(line=1, column=1, subject="build")),
        ("EMIT report", n.Emit(line=1, column=1, artifact="report")),
        ('TRANSITION "Done"', n.Transition(line=1, column=1, state="Done")),
        ('TRANSITION t "Done"', n.EntityTransition(line=1, column=1, name="t", status="Done")),
        ("WAIT", n.Wait(line=1, column=1)),
        ("STOP", n.Stop(line=1, column=1)),
    ],
)
def test_statement_forms(source: str, expected: n.Node) -> None:
    assert only(source) == expected


def test_decision_hitl_with_references() -> None:
    node = only('AUTO HITL:merge[yes, no]("Merge {t} into {b}?")')
    assert isinstance(node, n.Hitl)
    assert (node.name, node.answers, node.auto) == ("merge", ("yes", "no"), True)
    assert [(r.name, r.column) for r in node.text.references] == [("t", 33), ("b", 42)]


def test_request_hitl_has_no_name() -> None:
    node = only('HITL("Please review")')
    assert isinstance(node, n.Hitl) and node.name is None and node.text.value == "Please review"


def test_children_and_arrows() -> None:
    source = "WHEN x.accepted\n  → DELEGATE fix\n      VERIFY fix\n  → STOP\n"
    when = only(source)
    assert isinstance(when, n.When)
    first, second = when.children
    assert first.arrow and isinstance(first, n.Delegate)
    assert isinstance(first.children[0], n.Verify) and not first.children[0].arrow
    assert second.arrow and isinstance(second, n.Stop)


def test_keywords_are_accepted_as_names() -> None:
    assert only("DELEGATE STOP") == n.Delegate(line=1, column=1, work="STOP")
    assert only("LOOP:Task = TASK-0001") == n.Binding(line=1, column=1, name="LOOP", type="Task", target="TASK-0001")


@pytest.mark.parametrize(
    "source, kind",
    [
        ("LOOP : a", IssueKind.SYNTAX),  # spaces around ':' are not allowed
        ("WHEN x . y", IssueKind.SYNTAX),
        ("BREAK release", IssueKind.SYNTAX),
        ('HITL:m[a,]("q")', IssueKind.SYNTAX),
        ('HITL("unbalanced {")', IssueKind.SYNTAX),
        ('TRANSITION ""', IssueKind.SYNTAX),
        ("AUTO DELEGATE x", IssueKind.AUTO),
        ('AUTO HITL("q")', IssueKind.AUTO),
        ("FALLBACK", IssueKind.BARE_FALLBACK),
    ],
)
def test_malformed_lines_become_invalid_nodes_with_an_issue(source: str, kind: IssueKind) -> None:
    program = parse(source)
    assert isinstance(program.children[0], n.Invalid)
    assert [i.kind for i in program.issues] == [kind]


def test_recovery_keeps_the_children_of_an_unreadable_line() -> None:
    program = parse("AUTO\n  WHEN d.x\n    → STOP\nSTOP")
    invalid, stop = program.children
    assert isinstance(invalid, n.Invalid) and isinstance(invalid.children[0], n.When)
    assert isinstance(stop, n.Stop)


def test_nodes_are_frozen() -> None:
    node = only("STOP")
    with pytest.raises(dataclasses.FrozenInstanceError):
        node.line = 2  # type: ignore[misc]
