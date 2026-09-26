import io
import shutil
from pathlib import Path

from axiom.cli import main
from helpers import repo_root


def copy_docs(tmp_path: Path) -> Path:
    shutil.copytree(repo_root() / "docs", tmp_path / "docs")
    return tmp_path


def test_entities_check_and_index(tmp_path: Path) -> None:
    root = copy_docs(tmp_path)
    out = io.StringIO()
    assert main(["entities", "check", "--project", str(root)], out) == 0
    assert "docs/tasks/TASK-0001.md VALID" in out.getvalue()
    (root / "docs" / "tasks" / "_index.md").unlink()
    assert main(["index", "--check", "--project", str(root)], io.StringIO()) == 1
    out = io.StringIO()
    assert main(["index", "--project", str(root)], out) == 0
    assert "wrote docs/tasks/_index.md" in out.getvalue()
    assert main(["entities", "check", "--project", str(root)], io.StringIO()) == 0


def test_entities_check_reports_problems(tmp_path: Path) -> None:
    root = copy_docs(tmp_path)
    task = root / "docs" / "tasks" / "TASK-0001.md"
    task.write_text(task.read_text().replace("## Description", "## Summary"))
    out = io.StringIO()
    assert main(["entities", "check", "--project", str(root)], out) == 1
    assert "docs/tasks/TASK-0001.md INVALID\n    missing section Description" in out.getvalue()
