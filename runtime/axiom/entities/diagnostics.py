"""Problems found in entities. Checks return them; nothing is raised for a malformed entity (CONV-0005)."""

from __future__ import annotations

import enum
from dataclasses import dataclass
from pathlib import PurePosixPath


class Code(enum.Enum):
    NO_FRONT_MATTER = "no-front-matter"
    UNKNOWN_TYPE = "unknown-type"
    MISSING_FIELD = "missing-field"
    BAD_FORMAT = "bad-format"
    UNDECLARED_STATUS = "undeclared-status"
    MISSING_SECTION = "missing-section"
    EMPTY_SECTION = "empty-section"
    TOO_MANY_TARGETS = "too-many-targets"
    DUPLICATE_ID = "duplicate-id"
    MISSING_TARGET = "missing-target"
    WRONG_TARGET_TYPE = "wrong-target-type"
    STALE_INDEX = "stale-index"


@dataclass(frozen=True, order=True)
class EntityDiagnostic:
    path: PurePosixPath
    code: Code
    message: str

    def __str__(self) -> str:
        return f"{self.path}: {self.message}"
