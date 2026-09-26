import pytest

from axiom.entities import Code
from helpers import adr, project, task


def codes(files: dict[str, str]) -> set[Code]:
    report = project(files).check()
    found = {d.code for _, problems in report.files for d in problems}
    found |= {d.code for d in report.duplicates + report.relations}
    return found


def with_indexes(files: dict[str, str]) -> dict[str, str]:
    p = project(files)
    p.indexes().write()
    return {str(k): v for k, v in p.store.files.items()}  # type: ignore[attr-defined]


def test_a_valid_project_passes() -> None:
    files = with_indexes({"docs/tasks/TASK-0001.md": task("TASK-0001", extra="adr: ADR-0001\n"),
                          "docs/adr/ADR-0001.md": adr("ADR-0001")})
    report = project(files).check()
    assert report.valid, report


@pytest.mark.parametrize(
    "text, code",
    [
        ("# no front matter\n", Code.NO_FRONT_MATTER),
        (task("TASK-0001").replace("type: Task", "type: Story"), Code.UNKNOWN_TYPE),
        (task("TASK-0001").replace("status: Todo\n", ""), Code.MISSING_FIELD),
        (task("TASK-01"), Code.BAD_FORMAT),
        (task("TASK-0001", status="Started"), Code.UNDECLARED_STATUS),
        (task("TASK-0001", body="## Acceptance Criteria\n\n- x\n"), Code.MISSING_SECTION),
        (task("TASK-0001", body="## Description\n\nx\n\n## Acceptance Criteria\n\nnone\n"), Code.EMPTY_SECTION),
        (task("TASK-0001", extra="adr: ADR-0001, ADR-0002\n"), Code.TOO_MANY_TARGETS),
    ],
)
def test_structural_problems(text: str, code: Code) -> None:
    assert code in codes({"docs/tasks/TASK-0001.md": text})


def test_duplicate_ids_and_relations() -> None:
    assert Code.DUPLICATE_ID in codes({"docs/tasks/a.md": task("TASK-0001"), "docs/tasks/b.md": task("TASK-0001")})
    assert Code.MISSING_TARGET in codes({"docs/tasks/TASK-0001.md": task("TASK-0001", extra="adr: ADR-0009\n")})
    assert Code.WRONG_TARGET_TYPE in codes({"docs/tasks/TASK-0001.md": task("TASK-0001", extra="adr: TASK-0002\n"),
                                            "docs/tasks/TASK-0002.md": task("TASK-0002")})


def test_index_files_are_not_entities_and_stale_indexes_are_reported() -> None:
    files = with_indexes({"docs/tasks/TASK-0001.md": task("TASK-0001")})
    assert [str(p) for p, _ in project(files).check().files] == ["docs/tasks/TASK-0001.md"]
    files["docs/tasks/TASK-0002.md"] = task("TASK-0002")
    assert [str(p) for p in project(files).check().stale_indexes] == ["docs/tasks/_index.md", "docs/_index.md"]


def test_index_keeps_the_hand_written_part() -> None:
    files = {"docs/tasks/TASK-0001.md": task("TASK-0001"), "docs/tasks/_index.md": "# tasks\n\nWhat we do.\n"}
    out = with_indexes(files)
    assert out["docs/tasks/_index.md"].startswith("# tasks\n\nWhat we do.\n\n<!-- axiom:generated:start -->")
    assert "| [TASK-0001](TASK-0001.md) | Title of TASK-0001 | Todo |" in out["docs/tasks/_index.md"]
    assert "| [tasks/](tasks/_index.md) | What we do. | 1 (Todo 1) |" in out["docs/_index.md"]
