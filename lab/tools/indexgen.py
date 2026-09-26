#!/usr/bin/env python3
"""indexgen: generate the `_index.md` files of a docs/ tree (temporary, until axiom MCP owns entity writes).

usage: indexgen.py DOCS_DIR          write every index
       indexgen.py --check DOCS_DIR  report indexes that differ from what would be generated (exit 1)

Each collection index keeps its hand-written part (everything outside the generated block) and
replaces the block between the markers. Entity contracts are read from rules/types/ of this repo.
"""
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
TYPES = os.path.join(ROOT, "rules", "types")
START, END = "<!-- axiom:generated:start -->", "<!-- axiom:generated:end -->"
NOTE = "_Generated from the entities in this directory. Do not edit by hand._"
INDEX = "_index.md"


def table(md, heading):
    m = re.search(rf"^## {heading}\n(.*?)(?=^## |\Z)", md, re.S | re.M)
    rows = [l for l in (m[1] if m else "").splitlines() if l.startswith("|")][2:]
    return [[c.strip() for c in r.strip("|").split("|")] for r in rows]


def front_matter(text):
    m = re.match(r"---\n(.*?)\n---\n", text, re.S)
    if not m:
        return None, text
    fm = {}
    for line in m[1].splitlines():
        k, _, v = line.partition(":")
        fm[k.strip()] = v.strip()
    return fm, text[m.end():]


class TypeInfo:
    def __init__(self, name):
        d = os.path.join(TYPES, name.lower())
        tpl = open(os.path.join(d, "template.md")).read()
        dfn = open(os.path.join(d, "definition.md")).read()
        self.name = name
        self.fields = [r[0] for r in table(tpl, "Fields")]
        self.relations = {r[1]: r[2] for r in table(tpl, "Relations")}  # field -> target type
        sts = re.search(r"^## Statuses\n(.*?)(?=^## )", dfn, re.S | re.M)[1]
        self.terminal = set(re.findall(r"^- (\w+) \(terminal\)", sts, re.M))
        self.has_done = "Done" in re.findall(r"^- (\w+)", sts, re.M)


def load_collection(path):
    """Return the entities of one collection directory as dicts (front matter + title + file)."""
    out = []
    for f in sorted(os.listdir(path)):
        if not f.endswith(".md") or f == INDEX:
            continue
        fm, body = front_matter(open(os.path.join(path, f)).read())
        if fm is None or "type" not in fm:
            continue
        m = re.search(r"^# (.+)$", body, re.M)
        fm = dict(fm, _title=m[1].strip() if m else "", _file=f)
        out.append(fm)
    return out


def collections(docs):
    return [d for d in sorted(os.listdir(docs)) if os.path.isdir(os.path.join(docs, d)) and not d.startswith(".")]


def load_all(docs):
    return {c: load_collection(os.path.join(docs, c)) for c in collections(docs)}


def status_summary(ents):
    counts = {}
    for e in ents:
        counts[e.get("status", "?")] = counts.get(e.get("status", "?"), 0) + 1
    return ", ".join(f"{k} {v}" for k, v in sorted(counts.items()))


def collection_block(name, ents, all_ents):
    if not ents:
        return "\n".join([START, NOTE, "", "No entries yet.", END])
    t = TypeInfo(ents[0]["type"])
    cols = [f for f in t.fields if f not in ("id", "type") and any(e.get(f) for e in ents)]
    # reverse relations: other collections whose entities point at this type
    back = []
    for cname, cents in all_ents.items():
        if not cents:
            continue
        ct = TypeInfo(cents[0]["type"])
        for field, target in ct.relations.items():
            if target == t.name and cname != name:
                back.append((cname, field, ct))
    head = ["ID", "Title"] + [c.capitalize() for c in cols] + [f"{c.capitalize()} done" if ct.has_done else c.capitalize() for c, _, ct in back]
    lines = [START, NOTE, "", "| " + " | ".join(head) + " |", "|" + "---|" * len(head)]
    for e in sorted(ents, key=lambda e: e.get("id", "")):
        row = [f"[{e['id']}]({e['_file']})", e["_title"].replace("|", "\\|")] + [e.get(c, "") for c in cols]
        for cname, field, ct in back:
            refs = [x for x in all_ents[cname] if e["id"] in [v.strip() for v in x.get(field, "").split(",")]]
            done = sum(1 for x in refs if x.get("status") == "Done")
            row.append((f"{done}/{len(refs)}" if ct.has_done else str(len(refs))) if refs else "")
        lines.append("| " + " | ".join(row) + " |")
    lines.append(END)
    return "\n".join(lines)


def hand_written(path, default):
    if not os.path.exists(path):
        return default, ""
    text = open(path).read()
    if START in text and END in text:
        return text[: text.index(START)].rstrip() + "\n", text[text.index(END) + len(END):]
    return text.rstrip() + "\n", ""


def purpose(path):
    """First paragraph after the title of an index's hand-written part."""
    head, _ = hand_written(path, "")
    paras = [p.strip() for p in head.split("\n\n") if p.strip() and not p.strip().startswith("#")]
    return paras[0].replace("\n", " ") if paras else ""


def root_block(docs, all_ents):
    lines = [START, NOTE, "", "| Section | Purpose | Entries |", "|---|---|---|"]
    for c in collections(docs):
        ents = all_ents.get(c, [])
        entries = f"{len(ents)} ({status_summary(ents)})" if ents else "0"
        lines.append(f"| [{c}/]({c}/{INDEX}) | {purpose(os.path.join(docs, c, INDEX))} | {entries} |")
    lines.append(END)
    return "\n".join(lines)


def render(path, default_head, block):
    head, tail = hand_written(path, default_head)
    return head + "\n" + block + "\n" + tail.lstrip("\n")


def expected(docs):
    """Map of index path -> expected content."""
    all_ents = load_all(docs)
    out = {}
    for c in collections(docs):
        p = os.path.join(docs, c, INDEX)
        out[p] = render(p, f"# {c}\n\nTODO: describe the purpose of this directory.\n", collection_block(c, all_ents[c], all_ents))
    rp = os.path.join(docs, INDEX)
    # the root index needs the collection indexes first (for their purpose lines)
    out[rp] = None
    return out, all_ents


def run(docs, check):
    out, all_ents = expected(docs)
    bad = []
    for p, content in out.items():
        if content is None:
            continue
        if check:
            if not os.path.exists(p) or open(p).read() != content:
                bad.append(p)
        else:
            open(p, "w").write(content)
    rp = os.path.join(docs, INDEX)
    content = render(rp, "# docs\n\nTODO: describe this project's knowledge.\n", root_block(docs, all_ents))
    if check:
        if not os.path.exists(rp) or open(rp).read() != content:
            bad.append(rp)
    else:
        open(rp, "w").write(content)
    return bad


def main(argv):
    check = argv[:1] == ["--check"]
    docs = argv[1] if check else argv[0]
    bad = run(docs, check)
    for p in bad:
        print(f"index out of date: {p}")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
