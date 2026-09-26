"""An entity instance as read from its representation."""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from pathlib import PurePosixPath
from typing import Mapping

from axiom.entities.markdown import front_matter, sections, title


@dataclass(frozen=True)
class Entity:
    path: PurePosixPath  # relative to the project root
    text: str
    fields: Mapping[str, str] | None  # None when the file has no front matter
    title: str
    sections: Mapping[str, str]

    @property
    def identity(self) -> str | None:
        return self.fields.get("id") or None if self.fields else None

    @property
    def type_name(self) -> str:
        return self.fields.get("type", "") if self.fields else ""

    @property
    def status(self) -> str:
        return self.fields.get("status", "") if self.fields else ""

    @property
    def content_hash(self) -> str:
        """SHA-256 of the representation; any change to the entity changes it."""
        return hashlib.sha256(self.text.encode("utf-8")).hexdigest()

    def refs(self, field: str) -> tuple[str, ...]:
        """The comma-separated identities in a relation field."""
        raw = self.fields.get(field, "") if self.fields else ""
        return tuple(v.strip() for v in raw.split(",") if v.strip())

    @classmethod
    def parse(cls, path: PurePosixPath, text: str) -> Entity:
        fields, body = front_matter(text)
        return cls(path, text, fields, title(body), sections(body))
