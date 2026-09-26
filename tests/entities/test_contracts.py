from pathlib import PurePosixPath

from axiom.entities.formats import ChoiceFormat, DateFormat, IdFormat, LiteralFormat, UncheckedFormat, parse_format
from helpers import CATALOG


def test_every_type_of_the_rulebook_is_read() -> None:
    assert sorted(CATALOG.names) == ["ADR", "Convention", "Milestone", "Task"]


def test_task_contract() -> None:
    t = CATALOG.get("task")
    assert t is not None and t.name == "Task"
    assert [f.name for f in t.fields] == ["id", "type", "status", "adr", "milestone"]
    assert [(s.name, s.required, s.needs_item) for s in t.sections] == [
        ("Description", True, False), ("Acceptance Criteria", True, True), ("Notes", False, False)]
    assert [(r.name, r.target, r.many) for r in t.relations] == [("adr", "ADR", False), ("milestone", "Milestone", False)]
    assert t.status_names == ("Todo", "InProgress", "Debugging", "Review", "Done")
    assert [s.name for s in t.statuses if s.initial] == ["Todo"] and [s.name for s in t.statuses if s.terminal] == ["Done"]
    assert ("Review", "Done", "human: approved") in [(x.source, x.target, x.precondition) for x in t.transitions]
    assert t.collection == PurePosixPath("docs/tasks")


def test_collections_of_every_type() -> None:
    assert {n: str(CATALOG.get(n).collection) for n in CATALOG.names} == {  # type: ignore[union-attr]
        "ADR": "docs/adr", "Convention": "docs/contributing", "Milestone": "docs/roadmap", "Task": "docs/tasks"}


def test_milestone_requires_is_many() -> None:
    t = CATALOG.get("Milestone")
    assert t is not None and t.relations[0].many


def test_formats() -> None:
    assert parse_format("`TASK-` followed by four digits") == IdFormat("TASK-", 4, "`TASK-` followed by four digits")
    assert parse_format("`Task`") == LiteralFormat("Task")
    assert parse_format("`mechanical` or `review`") == ChoiceFormat(("mechanical", "review"))
    assert parse_format("`YYYY-MM-DD`") == DateFormat()
    assert isinstance(parse_format("identity of an ADR"), UncheckedFormat)
    assert IdFormat("TASK-", 4, "x").problem("TASK-001") is not None
    assert DateFormat().problem("2026-9-1") is not None
