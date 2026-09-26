from pathlib import Path, PurePosixPath

import pytest

from axiom.entities import FileSystemStore, MemoryStore


def test_file_system_store_uses_paths_relative_to_the_root(tmp_path: Path) -> None:
    store = FileSystemStore(tmp_path)
    (tmp_path / "docs").mkdir()
    store.write(PurePosixPath("docs/a.md"), "x")
    assert store.read(PurePosixPath("docs/a.md")) == "x"
    assert store.list_dir(PurePosixPath("docs")) == ("a.md",)
    assert store.list_dir(PurePosixPath("missing")) == ()


def test_file_system_store_never_leaves_the_root(tmp_path: Path) -> None:
    with pytest.raises(ValueError):
        FileSystemStore(tmp_path / "project").read(PurePosixPath("../secret"))


def test_memory_store_implies_directories() -> None:
    store = MemoryStore({"docs/tasks/a.md": "x", "docs/b.md": "y"})
    assert store.list_dir(PurePosixPath("docs")) == ("b.md", "tasks")
    assert store.is_dir(PurePosixPath("docs/tasks")) and not store.is_dir(PurePosixPath("docs/b.md"))
