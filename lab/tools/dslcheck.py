#!/usr/bin/env python3
"""dslcheck: parser and validity checker (rules V1-V12) for the DSL.

usage: dslcheck.py FILE...      (each file = one program)
       dslcheck.py --md FILE    (check every ```text block in a markdown file)
Exit code 0 if every program is valid.
"""
import re
import sys

ARROW = "→"
IDENT = r"[A-Za-z][A-Za-z0-9_-]*"
COMPOUND = {"LOOP", "WHEN", "FORK", "HITL", "REQUIRE", "VERIFY", "ETRANS"}
FALLBACK_HOSTS = ("HITL", "REQUIRE", "VERIFY", "ETRANS")


class Node:
    def __init__(self, kind, line_no, indent, arrow=False, **kw):
        self.kind, self.line_no, self.indent, self.arrow = kind, line_no, indent, arrow
        self.children, self.parent = [], None
        self.__dict__.update(kw)

    def __repr__(self):
        return f"{'→ ' if self.arrow else ''}{self.kind}@{self.line_no}"


def parse_stmt(text):
    """Return (kind, attrs) for a statement text, or (None, error)."""
    t = text.strip()
    m = re.fullmatch(rf"LOOP:({IDENT})", t)
    if m:
        return "LOOP", {"name": m[1]}
    m = re.fullmatch(rf"WHEN ({IDENT})\.({IDENT})", t)
    if m:
        return "WHEN", {"subject": m[1], "outcome": m[2]}
    if t in ("FORK", "JOIN", "BREAK", "WAIT", "STOP"):
        return t, {}
    m = re.fullmatch(rf"(REQUIRE|DELEGATE|VERIFY|EMIT) ({IDENT})", t)
    if m:
        return m[1], {"arg": m[2]}
    m = re.fullmatch(rf"({IDENT}):({IDENT}) = ({IDENT})(?:\.({IDENT}))?", t)
    if m:
        return "BIND", {"name": m[1], "type": m[2], "target": m[3], "relation": m[4]}
    m = re.fullmatch(rf'TRANSITION ({IDENT}) "([^"]+)"', t)
    if m:
        return "ETRANS", {"name": m[1], "arg": m[2]}
    m = re.fullmatch(r'TRANSITION "([^"]+)"', t)
    if m:
        return "TRANSITION", {"arg": m[1]}
    m = re.fullmatch(rf'(AUTO )?HITL:({IDENT})\[([^\]]*)\]\("([^"]*)"\)', t)
    if m:
        answers = [a.strip() for a in m[3].split(",")] if m[3].strip() else []
        if any(not re.fullmatch(IDENT, a) for a in answers):
            return None, "V1: malformed answer list"
        return "HITL", {"auto": bool(m[1]), "name": m[2], "answers": answers}
    m = re.fullmatch(r'HITL\("([^"]*)"\)', t)
    if m:
        return "HITL", {"auto": False, "name": None, "answers": None}
    if t.startswith("AUTO"):
        return None, "V5: AUTO must be immediately followed by a decision HITL:<name>[…](…) on the same line"
    if t == "FALLBACK":
        return None, "V4: FALLBACK must be written as '→ FALLBACK'"
    return None, f"V1: unrecognised statement: {t!r}"


def parse(src):
    errors, root = [], Node("PROGRAM", 0, -1)
    stack = [root]
    for i, raw in enumerate(src.split("\n"), 1):
        if not raw.strip():
            continue
        if "\t" in raw[: len(raw) - len(raw.lstrip())]:
            errors.append(f"line {i}: V1: tabs are not allowed in indentation")
        indent = len(raw) - len(raw.lstrip())
        text = raw.strip()
        arrow = text.startswith(ARROW)
        if arrow:
            text = text[len(ARROW):].strip()
        if arrow and text == "FALLBACK":
            node = Node("FALLBACK", i, indent, arrow=True)
        else:
            kind, attrs = parse_stmt(text)
            if kind is None:
                errors.append(f"line {i}: {attrs}")
                continue
            node = Node(kind, i, indent, arrow=arrow, **attrs)
        while stack[-1].indent >= indent:
            stack.pop()
        parent = stack[-1]
        node.parent = parent
        parent.children.append(node)
        stack.append(node)
    return root, errors


def ancestors(n):
    p = n.parent
    while p is not None:
        yield p
        p = p.parent


def walk(n):
    for c in n.children:
        yield c
        yield from walk(c)


def check_structure(n, errors):
    """V1 / V4 / V8 / V9: which children each node may have."""
    kids = n.children
    items = [c for c in kids if c.arrow and c.kind != "FALLBACK"]
    fallbacks = [c for c in kids if c.kind == "FALLBACK"]
    plain = [c for c in kids if not c.arrow]
    k = n.kind
    loc = f"line {n.line_no}"
    if k in ("PROGRAM", "LOOP"):
        for c in kids:
            if c.arrow:
                errors.append(f"line {c.line_no}: V4: '→' item not under WHEN, FORK or FALLBACK")
        if k == "LOOP" and not kids:
            errors.append(f"{loc}: V1: LOOP has an empty body")
    elif k == "WHEN":
        if not items or plain or fallbacks:
            errors.append(f"{loc}: V1: WHEN must contain only '→' items (at least one)")
    elif k == "FORK":
        if plain or fallbacks:
            errors.append(f"{loc}: V1: FORK must contain only '→' branches")
        if len(items) < 2:
            errors.append(f"{loc}: V9: FORK has fewer than two branches")
    elif k in FALLBACK_HOSTS:
        if plain or items:
            errors.append(f"{loc}: V1/V4: {k} may only contain '→ FALLBACK'")
        if len(fallbacks) > 1:
            errors.append(f"{loc}: V4: {k} has more than one FALLBACK")
    elif k == "FALLBACK":
        if n.parent.kind not in FALLBACK_HOSTS:
            errors.append(f"{loc}: V4: '→ FALLBACK' not directly under HITL, REQUIRE, VERIFY or TRANSITION <name>")
        if not items or plain or fallbacks:
            errors.append(f"{loc}: V1: FALLBACK must contain only '→' items (at least one)")
        else:
            last = items[-1]
            last_stmt = last.children[-1] if (last.children and last.kind not in COMPOUND) else last
            if last_stmt.kind not in ("STOP", "BREAK"):
                errors.append(f"{loc}: V8: fallback flow does not end with STOP or BREAK")
    else:
        # simple statements; as '→' items they may have continuation lines
        if kids and not n.arrow:
            errors.append(f"{loc}: V1: {k} cannot have indented children")
        for c in kids:
            if n.arrow and c.arrow:
                errors.append(f"line {c.line_no}: V4: '→' item not under WHEN, FORK or FALLBACK")
    if n.arrow and n.kind != "FALLBACK" and n.parent.kind not in ("WHEN", "FORK", "FALLBACK"):
        errors.append(f"{loc}: V4: '→' item not under WHEN, FORK or FALLBACK")
    for c in kids:
        check_structure(c, errors)


def branch_of(n):
    """Nearest FORK branch item enclosing n (item whose parent is FORK), or None."""
    for a in [n, *ancestors(n)]:
        if a.arrow and a.parent is not None and a.parent.kind == "FORK":
            return a
    return None


def check_semantics(root, errors):
    nodes = list(walk(root))
    verify = {n.arg for n in nodes if n.kind == "VERIFY"}
    hitls = [n for n in nodes if n.kind == "HITL" and n.name]
    names = {}
    for h in hitls:
        if h.name in names:
            errors.append(f"line {h.line_no}: V7: HITL name '{h.name}' used twice")
        names[h.name] = h.answers
        if not h.answers or len(set(h.answers)) != len(h.answers):
            errors.append(f"line {h.line_no}: V7: answer list empty or repeated")
        if h.name in verify:
            errors.append(f"line {h.line_no}: V7: name '{h.name}' used by both HITL and VERIFY")
    # V11 / V12: bindings
    bound, seen_other = {}, False
    for n in nodes:
        if n.kind == "BIND":
            if n.parent.kind != "PROGRAM" or n.arrow or seen_other:
                errors.append(f"line {n.line_no}: V11: binding must be at the top of the program, unindented, before other statements")
            if n.name in bound:
                errors.append(f"line {n.line_no}: V11: name '{n.name}' is already bound")
            if n.relation and n.target not in bound:
                errors.append(f"line {n.line_no}: V11: relation starts from '{n.target}', which is not bound on an earlier line")
            bound[n.name] = n
        else:
            seen_other = True
    for n in nodes:
        if n.kind == "ETRANS" and n.name not in bound:
            errors.append(f"line {n.line_no}: V12: TRANSITION on '{n.name}', which is not bound")
    for h in hitls:
        if h.name in bound:
            errors.append(f"line {h.line_no}: V12: bound name '{h.name}' used as a HITL name")
    for n in nodes:
        if n.kind == "BREAK":
            loop = next((a for a in ancestors(n) if a.kind == "LOOP"), None)
            if loop is None:
                errors.append(f"line {n.line_no}: V2: BREAK is not inside a LOOP")
            else:
                for a in ancestors(n):
                    if a is loop:
                        break
                    if a.arrow and a.parent is not None and a.parent.kind == "FORK":
                        errors.append(f"line {n.line_no}: V3: BREAK inside a FORK branch leaves a LOOP outside it")
                        break
        if n.kind == "WHEN":
            s, o = n.subject, n.outcome
            ok = (s in verify and o in ("accepted", "rejected")) or (s in names and o in (names[s] or []))
            if not ok:
                errors.append(f"line {n.line_no}: V6: WHEN {s}.{o} refers to an outcome the program cannot produce")
        if n.kind == "JOIN" or n.kind == "WHEN":
            sib = n.parent.children
            idx = sib.index(n)
            open_forks = []
            for x in sib[:idx]:
                if x.kind == "FORK":
                    open_forks.append(x)
                elif x.kind == "JOIN" and open_forks:
                    open_forks.pop()
            if n.kind == "JOIN" and not open_forks:
                errors.append(f"line {n.line_no}: V9: JOIN has no corresponding FORK")
            if n.kind == "WHEN":
                for f in open_forks:
                    est = {x.arg for x in walk(f) if x.kind == "VERIFY"} | {x.name for x in walk(f) if x.kind == "HITL" and x.name}
                    if n.subject in est:
                        errors.append(f"line {n.line_no}: V10: WHEN tests '{n.subject}' before the FORK at line {f.line_no} is joined")


def check(src):
    root, errors = parse(src)
    check_structure(root, errors)
    check_semantics(root, errors)
    return errors


def main(argv):
    rc = 0
    if argv[:1] == ["--md"]:
        # ```text blocks must be valid, ```invalid blocks must be invalid
        text = open(argv[1]).read()
        for tag, b in re.findall(r"```(text|invalid)\n(.*?)```", text, re.S):
            errs = check(b)
            good = (tag == "text") == (not errs)
            rc |= not good
            first = b.strip().split("\n")[0]
            print(("ok   " if good else "FAIL ") + f"[{tag}] " + first[:60])
            for e in errs:
                print("     ", e)
        return rc
    for f in argv:
        errs = check(open(f).read())
        print(f, "VALID" if not errs else "INVALID")
        for e in errs:
            print("   ", e)
        rc |= bool(errs)
    return rc


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
