#!/usr/bin/env python3
"""entitycheck: structural validity of entity files against their Template.

usage: entitycheck.py FILE...   (reads rules/types/<type>/template.md and definition.md)
Checks: required fields present, id format, type, status declared, required sections present,
duplicate ids across the given files. Exit code 0 if all valid.
"""
import os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


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


def check(path):
    errs = []
    fm, body = front_matter(open(path).read())
    if fm is None:
        return ["no front matter"], None
    t = fm.get("type", "")
    tdir = os.path.join(ROOT, "rules", "types", t.lower())
    if not t or not os.path.isdir(tdir):
        return [f"unknown type {t!r}"], fm.get("id")
    tpl = open(os.path.join(tdir, "template.md")).read()
    dfn = open(os.path.join(tdir, "definition.md")).read()
    statuses = re.findall(r"^- (\w+)", re.search(r"^## Statuses\n(.*?)(?=^## )", dfn, re.S | re.M)[1], re.M)
    for name, req, fmt in table(tpl, "Fields"):
        if req == "yes" and not fm.get(name):
            errs.append(f"missing field {name}")
        m = re.fullmatch(r"`(\w+)-` followed by (\w+) digits", fmt)
        if m and fm.get(name):
            n = {"four": 4}.get(m[2], 0)
            if not re.fullmatch(rf"{m[1]}-\d{{{n}}}", fm[name]):
                errs.append(f"{name} {fm[name]!r} does not match {fmt}")
    if fm.get("status") not in statuses:
        errs.append(f"status {fm.get('status')!r} not declared ({', '.join(statuses)})")
    heads = set(re.findall(r"^## (.+)$", body, re.M))
    for name, req in table(tpl, "Sections"):
        if req.startswith("yes") and name not in heads:
            errs.append(f"missing section {name}")
    return errs, fm.get("id")


def main(files):
    rc, ids = 0, {}
    for f in files:
        errs, i = check(f)
        if i:
            ids.setdefault(i, []).append(f)
        print(f, "VALID" if not errs else "INVALID")
        for e in errs:
            print("   ", e)
        rc |= bool(errs)
    for i, fs in ids.items():
        if len(fs) > 1:
            print(f"duplicate id {i}: {fs}")
            rc = 1
    return rc


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
