"""The `_index.md` files of `docs/`: generated listing blocks inside hand-written text.

Each collection index lists its entities: ID, Title, the Template's fields that any entity uses, and
one column per relation from another collection that points at this type. A relation column shows
"done/all" when the referring type has a Done status, otherwise a count. The root index lists the
collections with their purpose (the first paragraph of each index) and a status summary.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import PurePosixPath

from axiom.entities.contracts import TypeCatalog
from axiom.entities.corpus import INDEX, collections
from axiom.entities.model import Entity
from axiom.entities.store import EntityStore

START, END = "<!-- axiom:generated:start -->", "<!-- axiom:generated:end -->"
NOTE = "_Generated from the entities in this directory. Do not edit by hand._"


@dataclass(frozen=True)
class _TypeView:
    name: str
    fields: tuple[str, ...]
    relations: tuple[tuple[str, str], ...]  # (field, target type)
    has_done: bool


class IndexGenerator:
    def __init__(self, store: EntityStore, catalog: TypeCatalog, docs: PurePosixPath = PurePosixPath("docs")) -> None:
        self._store = store
        self._catalog = catalog
        self._docs = docs

    # --- public -----------------------------------------------------------------------------------

    def expected(self) -> dict[PurePosixPath, str]:
        """Every index path and the content it should have, collections first, then the root."""
        entities = {c: self._load(c) for c in collections(self._store, self._docs)}
        out: dict[PurePosixPath, str] = {}
        for c, ents in entities.items():
            path = self._docs / c / INDEX
            default = f"# {c}\n\nTODO: describe the purpose of this directory.\n"
            out[path] = self._render(path, default, self._collection_block(c, ents, entities))
        root = self._docs / INDEX
        # the root lists each collection's purpose as its index will read once written
        out[root] = self._render(root, "# docs\n\nTODO: describe this project's knowledge.\n", self._root_block(entities, out))
        return out

    def stale(self) -> tuple[PurePosixPath, ...]:
        return tuple(p for p, text in self.expected().items() if not self._store.exists(p) or self._store.read(p) != text)

    def write(self) -> tuple[PurePosixPath, ...]:
        """Write every index that differs; return their paths."""
        changed = []
        for path, text in self.expected().items():
            if not self._store.exists(path) or self._store.read(path) != text:
                self._store.write(path, text)
                changed.append(path)
        return tuple(changed)

    # --- blocks -----------------------------------------------------------------------------------

    def _load(self, collection: str) -> list[Entity]:
        base = self._docs / collection
        out = []
        for name in self._store.list_dir(base):
            if name.endswith(".md") and name != INDEX:
                e = Entity.parse(base / name, self._store.read(base / name))
                if e.fields is not None and "type" in e.fields:
                    out.append(e)
        return out

    def _view(self, type_name: str) -> _TypeView:
        t = self._catalog.get(type_name)
        if t is None:
            return _TypeView(type_name, (), (), False)
        return _TypeView(type_name, tuple(f.name for f in t.fields), tuple((r.field, r.target) for r in t.relations),
                         "Done" in t.status_names)

    def _collection_block(self, name: str, ents: list[Entity], every: dict[str, list[Entity]]) -> str:
        if not ents:
            return "\n".join([START, NOTE, "", "No entries yet.", END])
        t = self._view(ents[0].type_name)
        cols = [f for f in t.fields if f not in ("id", "type") and any(_get(e, f) for e in ents)]
        back: list[tuple[str, str, _TypeView]] = []
        for cname, cents in every.items():
            if not cents:
                continue
            ct = self._view(cents[0].type_name)
            back += [(cname, field, ct) for field, target in ct.relations if target == t.name and cname != name]
        head = ["ID", "Title"] + [c.capitalize() for c in cols]
        head += [f"{c.capitalize()} done" if ct.has_done else c.capitalize() for c, _, ct in back]
        lines = [START, NOTE, "", "| " + " | ".join(head) + " |", "|" + "---|" * len(head)]
        for e in sorted(ents, key=lambda x: _get(x, "id")):
            row = [f"[{_get(e, 'id')}]({e.path.name})", e.title.replace("|", "\\|")] + [_get(e, c) for c in cols]
            for cname, field, ct in back:
                refs = [x for x in every[cname] if _get(e, "id") in [v.strip() for v in _get(x, field).split(",")]]
                done = sum(1 for x in refs if _get(x, "status") == "Done")
                row.append((f"{done}/{len(refs)}" if ct.has_done else str(len(refs))) if refs else "")
            lines.append("| " + " | ".join(row) + " |")
        lines.append(END)
        return "\n".join(lines)

    def _root_block(self, every: dict[str, list[Entity]], indexes: dict[PurePosixPath, str]) -> str:
        lines = [START, NOTE, "", "| Section | Purpose | Entries |", "|---|---|---|"]
        for c in collections(self._store, self._docs):
            ents = every.get(c, [])
            entries = f"{len(ents)} ({_status_summary(ents)})" if ents else "0"
            lines.append(f"| [{c}/]({c}/{INDEX}) | {_purpose(indexes[self._docs / c / INDEX])} | {entries} |")
        lines.append(END)
        return "\n".join(lines)

    # --- hand-written parts -----------------------------------------------------------------------

    def _hand_written(self, path: PurePosixPath, default: str) -> tuple[str, str]:
        if not self._store.exists(path):
            return default, ""
        return _split(self._store.read(path))

    def _render(self, path: PurePosixPath, default_head: str, block: str) -> str:
        head, tail = self._hand_written(path, default_head)
        return head + "\n" + block + "\n" + tail.lstrip("\n")


def _split(text: str) -> tuple[str, str]:
    """The hand-written text before the generated block, and the text after it."""
    if START in text and END in text:
        return text[: text.index(START)].rstrip() + "\n", text[text.index(END) + len(END):]
    return text.rstrip() + "\n", ""


def _purpose(index_text: str) -> str:
    """The first paragraph of an index's hand-written part."""
    head, _ = _split(index_text)
    paras = [p.strip() for p in head.split("\n\n") if p.strip() and not p.strip().startswith("#")]
    return paras[0].replace("\n", " ") if paras else ""


def _get(e: Entity, field: str) -> str:
    return e.fields.get(field, "") if e.fields else ""


def _status_summary(ents: list[Entity]) -> str:
    counts: dict[str, int] = {}
    for e in ents:
        status = e.fields.get("status", "?") if e.fields else "?"
        counts[status] = counts.get(status, 0) + 1
    return ", ".join(f"{k} {v}" for k, v in sorted(counts.items()))
