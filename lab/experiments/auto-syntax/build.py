#!/usr/bin/env python3
"""AUTO-placement experiment: build 4 spec variants (A-D) from dsl.md and
render the X-scenarios for each variant. Only the AUTO form differs."""
import re, pathlib, sys
HERE = pathlib.Path(__file__).parent
ROOT = HERE.parents[2]
base = (ROOT / "dsl.md").read_text()
VARIANTS = "ABCD"

# ---------- rendering of AUTO-marked HITL in code ----------
def auto_hitl(v, ind, name, msg):
    h = f'HITL:{name}("{msg}")'
    if v == "A": return [f"{ind}AUTO {h}"]
    if v == "B": return [f"{ind}{h} AUTO"]
    if v == "C": return [f"{ind}{h}", f"{ind}  → AUTO"]
    if v == "D": return [f"{ind}AUTO", f"{ind}{h}"]
def auto_other(v, ind, stmt):          # AUTO applied to a non-HITL statement
    if v == "A": return [f"{ind}AUTO {stmt}"]
    if v == "B": return [f"{ind}{stmt} AUTO"]
    if v == "C": return [f"{ind}{stmt}", f"{ind}  → AUTO"]
    if v == "D": return [f"{ind}AUTO", f"{ind}{stmt}"]
def wrong_form(v, ind, name, msg):     # most natural alternative placement, invalid in v
    h = f'HITL:{name}("{msg}")'
    if v == "A": return [f"{ind}{h} AUTO"]
    if v == "B": return [f"{ind}AUTO {h}"]
    if v == "C": return [f"{ind}AUTO {h}"]
    if v == "D": return [f"{ind}AUTO {h}"]
def render(text, v):
    out = []
    for line in text.split("\n"):
        m = re.match(r"^(\s*)\{\{(AUTOHITL|WRONG) ([\w-]+)\|(.*)\}\}$", line)
        m2 = re.match(r"^(\s*)\{\{AUTOOTHER (.*)\}\}$", line)
        if m:
            f = auto_hitl if m.group(2) == "AUTOHITL" else wrong_form
            out += f(v, m.group(1), m.group(3), m.group(4))
        elif m2:
            out += auto_other(v, m2.group(1), m2.group(2))
        else:
            out.append(line)
    return "\n".join(out)

# ---------- variant-specific spec text ----------
FORM = {
 "A": ("AUTO HITL:<name>(\"<message>\")",
       "`AUTO` is written directly before `HITL`, on the same line. It marks that one `HITL` as automatically resolvable."),
 "B": ("HITL:<name>(\"<message>\") AUTO",
       "`AUTO` is written directly after the closing parenthesis of `HITL(...)`, on the same line. It marks that one `HITL` as automatically resolvable."),
 "C": ("HITL:<name>(\"<message>\")\n  → AUTO",
       "`→ AUTO` is written directly under a `HITL`, indented one level. It marks that one `HITL` as automatically resolvable. If the `HITL` also has a `→ FALLBACK`, `→ AUTO` comes first. `→ AUTO` has no children."),
 "D": ("AUTO\nHITL:<name>(\"<message>\")",
       "`AUTO` is written on its own line directly before a `HITL`, at the same indentation. It marks only the `HITL` on the immediately following line as automatically resolvable. An `AUTO` line that is not immediately followed by a `HITL` is invalid."),
}
STMT_ROW = {
 "A": '| `[AUTO] HITL[:<name>]("<message>")` | `HITL`, `AUTO` |',
 "B": '| `HITL[:<name>]("<message>") [AUTO]` | `HITL`, `AUTO` |',
 "C": '| `HITL[:<name>]("<message>")` | `HITL` |\n| `→ AUTO` (only directly under a `HITL`) | `AUTO` |',
 "D": '| `HITL[:<name>]("<message>")` | `HITL` |\n| `AUTO` (only on the line directly before a `HITL`) | `AUTO` |',
}
GRAMMAR = {
 "A": 'hitl        = [ "AUTO" ] , "HITL" , [ ":" , identifier ] , "(" , string , ")" , NL ,\n              [ INDENT , "→" , "FALLBACK" , NL , INDENT , flow , DEDENT , DEDENT ] ;',
 "B": 'hitl        = "HITL" , [ ":" , identifier ] , "(" , string , ")" , [ "AUTO" ] , NL ,\n              [ INDENT , "→" , "FALLBACK" , NL , INDENT , flow , DEDENT , DEDENT ] ;',
 "C": 'hitl        = "HITL" , [ ":" , identifier ] , "(" , string , ")" , NL ,\n              [ INDENT , [ "→" , "AUTO" , NL ] ,\n                [ "→" , "FALLBACK" , NL , INDENT , flow , DEDENT ] , DEDENT ] ;',
 "D": 'hitl        = [ "AUTO" , NL ] , "HITL" , [ ":" , identifier ] , "(" , string , ")" , NL ,\n              [ INDENT , "→" , "FALLBACK" , NL , INDENT , flow , DEDENT , DEDENT ] ;',
}

EX_DETERMINED = '''DELEGATE dependency-upgrade
VERIFY dependency-upgrade
{{AUTOHITL merge|Merge the dependency upgrade?}}
WHEN merge.approved
  → TRANSITION "Merged"
WHEN merge.declined
  → TRANSITION "Deferred"'''

def auto_section(v, semantic):
    code, rule = FORM[v]
    ex = render(EX_DETERMINED, v)
    bad = render('{{AUTOOTHER DELEGATE implementation}}', v)
    return f'''### AUTO

{semantic}

Syntax:

```text
{code}
```

{rule} `AUTO` is not a statement of its own and applies to no other statement. `AUTO` applies only to `HITL`.

Execution:

| `AUTO` on this `HITL`? | Decision sufficiently determined? | What happens |
|---|---|---|
| no | — | The human is asked. The agent must not decide. |
| yes | yes | The agent resolves the decision. The human is **not** asked. The outcome `<name>.<answer>` is established exactly as if a human had given that answer. |
| yes | no (uncertain, or outside the agent's authority) | The human is asked, as for a `HITL` without `AUTO`. |

After the decision is made, by the agent or by the human, execution continues with the statement after the `HITL` construct. `FALLBACK` is used only if the human is asked and the response is unavailable or insufficient.

Example:

```text
{ex}
```

- If the process's merge criteria clearly determine "approve", the agent establishes `merge.approved` without asking anyone. Then `TRANSITION "Merged"` executes.
- If the information is contradictory or the criteria do not cover the case, the human is asked "Merge the dependency upgrade?". Their answer establishes `merge.approved` or `merge.declined`.

Invalid, because `AUTO` applies only to `HITL`:

```text
{bad}
```

Also invalid, because `AUTO` never contains a flow and uncertainty is not a condition:

```text
AUTO
  WHEN decision.uncertain
    → HITL("Approve?")
```

The DSL runtime determines uncertainty as part of automatic decision resolution.

`AUTO` and `FALLBACK` are different mechanisms. When `AUTO` cannot resolve a decision, the decision goes to the human through the normal `HITL`; this is not a fallback. `FALLBACK` applies only afterwards, if the human's response is unavailable or insufficient.

---

'''

HITL_NEW = '''### HITL

Requests a decision, input, or action from a human.

```text
HITL:<name>("<message>")
HITL("<message>")
```

`HITL` establishes a human decision boundary.

The human response may determine the subsequent flow.

`<name>` names the decision. The response establishes the outcome `<name>.<answer>`, where `<answer>` is one of the answers tested by the `WHEN <name>.<answer>` constructs that follow. A response that corresponds to none of these answers is insufficient (see `FALLBACK`). The name may be omitted when no `WHEN` refers to the decision.

`HITL` must not be silently replaced by an agent decision unless that `HITL` is explicitly marked with `AUTO` (see `AUTO`).

The flow containing a `HITL` waits at the `HITL` until either a usable response is available or its `FALLBACK` flow is used (see `FALLBACK`). With a usable response, execution continues with the next statement after the `HITL` construct.

---

'''

def build_variant(v):
    s = base
    i, j = s.index("### HITL\n"), s.index("### AUTO\n")
    s = s[:i] + HITL_NEW + s[j:]
    i = s.index("### AUTO\n"); j = s.index("### FALLBACK\n")
    a = s[i:j]
    sem_start = a.index("Allows a decision"); sem_end = a.index("`AUTO` is not a control-flow container.")
    semantic = a[sem_start:sem_end].strip() + "\n\n`AUTO` is not a control-flow container.\n\nIt does not contain `WHEN`, `→`, or an arbitrary flow.\n\nUncertainty is not a DSL condition, state, variable, or keyword."
    s = s[:i] + auto_section(v, semantic) + s[j:]
    s = s.replace('| `HITL("<message>")` | `HITL` |', STMT_ROW[v])
    s = s.replace('hitl        = "HITL(" , string , ")" , NL ,\n              [ INDENT , "→" , "FALLBACK" , NL , INDENT , flow , DEDENT , DEDENT ] ;', GRAMMAR[v])
    if v == "C":
        s = s.replace("| `HITL` | only `→ FALLBACK`, which attaches the fallback |", "| `HITL` | only `→ AUTO` (marks the decision as automatically resolvable) and `→ FALLBACK` (attaches the fallback) |")
        s = s.replace("`HITL` (only for `→ FALLBACK`)", "`HITL` (only for `→ AUTO` and `→ FALLBACK`)")
    for must in ["HITL:<name>", "### AUTO", GRAMMAR[v].split("\n")[0]]:
        assert must in s, (v, must)
    return s

HEADER = """You are given the complete specification of a small process DSL and one task.
Use ONLY the specification below. Where the specification does not determine
something you need, say so explicitly and state what you assumed.

<specification>
"""
CONF_TASK = """Read the specification carefully as if you had to write or execute processes
with it. Focus on HITL, AUTO and FALLBACK and how they interact with WHEN.
List EVERY place that is unclear, contradictory, or underspecified.
For each item: cite the section heading, quote the relevant text, explain the
problem, and show how two reasonable readers could interpret it differently.
"""
def main(outdir):
    out = pathlib.Path(outdir); (out/"in").mkdir(parents=True, exist_ok=True); (out/"out").mkdir(exist_ok=True)
    for v in VARIANTS:
        spec = build_variant(v)
        (HERE/"variants"/f"{v}.md").write_text(spec)
        for sc in sorted((HERE/"scenarios").glob("X*.md")):
            r = render(sc.read_text(), v)
            (HERE/"rendered"/v).mkdir(parents=True, exist_ok=True)
            (HERE/"rendered"/v/sc.name).write_text(r)
            task = r.split("## Task\n",1)[1].split("## Expected",1)[0]
            (out/"in"/f"{v}-{sc.name[:3]}.md").write_text(HEADER+spec+"\n</specification>\n\n<task>\n"+task+"</task>\n")
        (out/"in"/f"{v}-CONF.md").write_text(HEADER+spec+"\n</specification>\n\n<task>\n"+CONF_TASK+"</task>\n")
    print(sorted(p.name for p in (out/"in").iterdir()))
if __name__ == "__main__":
    main(sys.argv[1])
