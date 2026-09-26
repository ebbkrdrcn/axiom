"""Repository port for a project's files, with paths relative to the project root, and its adapters."""

from __future__ import annotations

from pathlib import Path, PurePosixPath
from typing import Mapping, Protocol


class EntityStore(Protocol):
    def exists(self, path: PurePosixPath) -> bool: ...

    def is_dir(self, path: PurePosixPath) -> bool: ...

    def list_dir(self, path: PurePosixPath) -> tuple[str, ...]:
        """Entry names of a directory, sorted; empty if it does not exist."""
        ...

    def read(self, path: PurePosixPath) -> str: ...

    def write(self, path: PurePosixPath, text: str) -> None: ...


class FileSystemStore:
    """Adapter onto a directory. Every path is relative to `root`, and never leaves it."""

    def __init__(self, root: Path) -> None:
        self._root = root.resolve()

    def _abs(self, path: PurePosixPath) -> Path:
        full = (self._root / path).resolve()
        if full != self._root and self._root not in full.parents:
            raise ValueError(f"{path} is outside the project root")  # a caller bug, never user data
        return full

    def exists(self, path: PurePosixPath) -> bool:
        return self._abs(path).exists()

    def is_dir(self, path: PurePosixPath) -> bool:
        return self._abs(path).is_dir()

    def list_dir(self, path: PurePosixPath) -> tuple[str, ...]:
        full = self._abs(path)
        return tuple(sorted(p.name for p in full.iterdir())) if full.is_dir() else ()

    def read(self, path: PurePosixPath) -> str:
        return self._abs(path).read_text(encoding="utf-8")

    def write(self, path: PurePosixPath, text: str) -> None:
        self._abs(path).write_text(text, encoding="utf-8")


class MemoryStore:
    """Adapter onto a dict of path → text; directories are implied by the paths."""

    def __init__(self, files: Mapping[str, str] | None = None) -> None:
        self.files: dict[PurePosixPath, str] = {PurePosixPath(k): v for k, v in (files or {}).items()}

    def exists(self, path: PurePosixPath) -> bool:
        return path in self.files or self.is_dir(path)

    def is_dir(self, path: PurePosixPath) -> bool:
        return any(path in f.parents for f in self.files)

    def list_dir(self, path: PurePosixPath) -> tuple[str, ...]:
        names = {f.relative_to(path).parts[0] for f in self.files if path in f.parents}
        return tuple(sorted(names))

    def read(self, path: PurePosixPath) -> str:
        return self.files[path]

    def write(self, path: PurePosixPath, text: str) -> None:
        self.files[path] = text
