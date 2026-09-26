from axiom.entities import Failure, Project
from helpers import adr, project, task


def resolve(p: Project, identity: str, type_name: str) -> Failure | None:
    return p.resolve(identity, type_name).failure


def test_exactly_one_match_resolves() -> None:
    p = project({"docs/tasks/whatever-name.md": task("TASK-0001")})
    r = p.resolve("TASK-0001", "Task")
    assert r.satisfied and r.entity is not None and str(r.entity.path) == "docs/tasks/whatever-name.md"


def test_identity_counting_failures() -> None:
    assert resolve(project({}), "TASK-0001", "Task") is Failure.NOT_FOUND
    two = project({"docs/tasks/a.md": task("TASK-0001"), "docs/other/b.md": task("TASK-0001")})
    assert resolve(two, "TASK-0001", "Task") is Failure.AMBIGUOUS


def test_file_name_is_not_identity() -> None:
    assert resolve(project({"docs/tasks/TASK-0001.md": task("TASK-0002")}), "TASK-0001", "Task") is Failure.NOT_FOUND


def test_wrong_type_and_invalid_entity() -> None:
    assert resolve(project({"docs/adr/ADR-0001.md": adr("ADR-0001")}), "ADR-0001", "Task") is Failure.WRONG_TYPE
    broken = task("TASK-0001", body="## Description\n\nx\n")
    assert resolve(project({"docs/tasks/TASK-0001.md": broken}), "TASK-0001", "Task") is Failure.INVALID


def test_relation_with_zero_one_or_two_targets() -> None:
    files = {
        "docs/tasks/TASK-0001.md": task("TASK-0001"),
        "docs/tasks/TASK-0002.md": task("TASK-0002", extra="adr: ADR-0001\n"),
        "docs/tasks/TASK-0003.md": task("TASK-0003", extra="adr: ADR-0001, ADR-0002\n"),
        "docs/adr/ADR-0001.md": adr("ADR-0001"),
        "docs/adr/ADR-0002.md": adr("ADR-0002"),
    }
    p = project(files)

    def via(identity: str) -> Failure | None:
        source = p.resolve(identity, "Task").entity or p.corpus().declaring(identity)[0]
        return p.resolve_relation(source, "adr", "ADR").failure

    assert via("TASK-0001") is Failure.NO_TARGET
    assert via("TASK-0002") is None
    assert via("TASK-0003") is Failure.MANY_TARGETS
    t2 = p.resolve("TASK-0002", "Task").entity
    assert t2 is not None and p.resolve_relation(t2, "nope", "ADR").failure is Failure.UNKNOWN_RELATION
