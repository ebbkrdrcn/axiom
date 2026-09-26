"""Reading the Markdown forms used by entity files and type contracts."""

from __future__ import annotations

import re
from types import MappingProxyType
from typing import Mapping

_FRONT_MATTER = re.compile(r"---\n(.*?)\n---\n", re.S)
_TITLE = re.compile(r"^# (.+)$", re.M)
_SECTION = re.compile(r"^## (.+)$", re.M)


def front_matter(text: str) -> tuple[Mapping[str, str] | None, str]:
    """The `key: value` pairs between the leading `---` lines, and the body after them."""
    m = _FRONT_MATTER.match(text)
    if not m:
        return None, text
    fields: dict[str, str] = {}
    for line in m[1].splitlines():
        key, _, value = line.partition(":")
        fields[key.strip()] = value.strip()
    return MappingProxyType(fields), text[m.end():]


def title(body: str) -> str:
    m = _TITLE.search(body)
    return m[1].strip() if m else ""


def sections(body: str) -> Mapping[str, str]:
    """Level-2 headings and the text under each, up to the next level-2 heading."""
    heads = list(_SECTION.finditer(body))
    out: dict[str, str] = {}
    for i, h in enumerate(heads):
        end = heads[i + 1].start() if i + 1 < len(heads) else len(body)
        out.setdefault(h[1].strip(), body[h.end():end])
    return MappingProxyType(out)


def section(md: str, heading: str) -> str:
    m = re.search(rf"^## {re.escape(heading)}\n(.*?)(?=^## |\Z)", md, re.S | re.M)
    return m[1] if m else ""


def table(md: str, heading: str) -> list[list[str]]:
    """The body rows of the first table under `## heading`, each as a list of stripped cells."""
    rows = [line for line in section(md, heading).splitlines() if line.startswith("|")][2:]
    return [[cell.strip() for cell in row.strip("|").split("|")] for row in rows]


def has_list_item(text: str) -> bool:
    return any(re.match(r"\s*(?:[-*]|\d+\.)\s+\S", line) for line in text.splitlines())
