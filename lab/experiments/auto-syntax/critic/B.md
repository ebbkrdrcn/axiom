# Critic report: variant B

Variant B's AUTO form (from `variants/B.md`, AUTO > Syntax): `HITL:<name>("<message>") AUTO`. The spec says: "`AUTO` is written directly after the closing parenthesis of `HITL(...)`, on the same line. It marks that one `HITL` as automatically resolvable. `AUTO` is not a statement of its own and applies to no other statement."

Inputs read: `variants/B.md`, `rendered/B/X01..X06`, `probes/B-X0{1..6}-p{1,2,3}.md`, `probes/B-CONF-p1.md`.

---

## X01: Authoring, one auto-resolvable decision

All three probes wrote the same program:

```text
DELEGATE implementation
VERIFY implementation
HITL:merge("Merge this change?") AUTO
  → FALLBACK
      → TRANSITION "Blocked"
        STOP
WHEN merge.approved
  → TRANSITION "Merged"
WHEN merge.declined
  → TRANSITION "Rework"
```

| Probe | D1 AUTO form + attachment | D2 named HITL, two WHENs on same name | D3 FALLBACK: Blocked then STOP | D4 no uncertainty condition / no flow in AUTO |
|---|---|---|---|---|
| p1 | met: `HITL:merge("Merge this change?") AUTO` | met: `WHEN merge.approved` / `WHEN merge.declined` | met: `→ TRANSITION "Blocked"` + nested `STOP` ("the nested form") | met: no `WHEN` on uncertainty, AUTO is only a trailing token |
| p2 | met: same line | met: same | met: same nested form | met: "the spec explicitly forbids treating uncertainty as a DSL condition" |
| p3 | met: same line | met: same | met: same nested form | met |

- The fallback flow uses the nested form (`→ TRANSITION "Blocked"` with `STOP` nested under it), not the canonical form with two `→` lines. The spec says this form is equivalent: "The following two forms are equivalent … Both mean: first `TRANSITION "Blocked"`, then `STOP`." D3 is met.
- Answer words are `approved`/`declined`. The rubric allows free answer words.
- Divergence: none. All three programs are identical, character for character.
- **Verdict: PASS**
- Errors: none.
- Hesitations about the AUTO form: 0. p1 (assumption 3) and p2 ("`AUTO` placement") put AUTO placement in their assumption lists, as the task asked for every assumption. Both say the placement follows directly from the spec. p2: "This is a direct application of the spec's given semantics, not really an added assumption". p2's remaining caveat is about how the requirement's wording "clearly determined" maps to AUTO's meaning. It is not about where AUTO goes or what it binds to. Neither counts as a hesitation.

## X02: Authoring, two decisions, only one auto-resolvable

| Probe | D1 AUTO only on the notes HITL | D2 approval HITL has no AUTO | D3 two named HITLs, each with its own WHENs, right order |
|---|---|---|---|
| p1 | met: `HITL:notes("Short or detailed release notes?") AUTO` | met: `HITL:approval("Approve the release?")` | met: `notes.short/detailed` then `approval.approved/rejected` |
| p2 | met: same | met: same | met: same (a blank line between the groups) |
| p3 | met: `HITL:notes-length(...) AUTO` | met: `HITL:approval(...)` | met: `notes-length.short/detailed`, `approval.approved/rejected` |

- Divergence: none that matters. The only difference is the decision name (`notes` vs `notes-length`). Every probe explains why it left out AUTO on the approval HITL. p3: "this is exactly the case the spec says `AUTO` must not be used for."
- **Verdict: PASS**
- Errors: none. In this form AUTO cannot also apply to the approval HITL, because it sits at the end of a different line.
- Hesitations: 0.

## X03: Trace, decision sufficiently determined

| Probe | D1 agent resolves, no human asked | D2 `merge.approved` → Merged; `declined` WHEN not satisfied | D3 FALLBACK not used; offline human irrelevant | D4 final "Merged" |
|---|---|---|---|---|
| p1 | met: "The agent therefore resolves the `merge` decision itself" | met: Steps 4–5 | met: "the question of the human's availability … never becomes relevant, and the `FALLBACK` … is not invoked" | met |
| p2 | met: "the agent resolves the decision itself, the human is not asked" | met | met: "whether a human is online is irrelevant to this outcome" | met |
| p3 | met: "the agent resolves the decision automatically" | met | met: "the decision would be auto-resolved even if a human were online" | met |

- Divergence: none.
- **Verdict: PASS**
- Errors: none. All three probes cite the spec's line that separates AUTO from FALLBACK ("`AUTO` and `FALLBACK` are different mechanisms…").
- Hesitations: 0. The assumptions the probes list are about how "sufficiently determined" is computed and about the changelog wording. None is about the AUTO form.

## X04: Trace, decision uncertain, human does not respond

| Probe | D1 uncertain; 90% does not count; agent must not decide | D2 human asked | D3 no response → FALLBACK Blocked, STOP; no WHEN evaluated | D4 final "Blocked" |
|---|---|---|---|---|
| p1 | met: "the decision is **uncertain** … 'A confidence score alone does not establish certainty.'" | met: "The human is asked 'Merge the dependency upgrade?'" | met: "`WHEN merge.approved` and `WHEN merge.declined` are never reached and never evaluated" | met |
| p2 | met: "The agent's 90% confidence does not change this" | met | met: "the two `WHEN` statements … are never evaluated at all" | met |
| p3 | met: "the decision is **not** sufficiently determined" | met | met: "`WHEN merge.approved` is never evaluated" | met |

- Divergence: none.
- **Verdict: PASS**
- Errors: none. A small wording slip in p2, Step 6: "Execution ends normally at this point" right after `STOP`. It does not change the trace and gets no tag.
- Hesitations: 0. The one assumption the probes flag (when "never responds" counts as unavailable) is about FALLBACK timing, not the AUTO form.

## X05: Validity of AUTO placements

| Probe | D1 S1 VALID | D2 S2 INVALID | D3 S3 INVALID (not the variant form) | D4 S4 INVALID |
|---|---|---|---|---|
| p1 | met: cites "directly after the closing parenthesis … on the same line" | met: "the spec's own explicit invalid example" | met: "Here `AUTO` precedes `HITL` instead of following the closing `)`" | met: "not a control-flow container"; "Uncertainty is not a DSL condition" |
| p2 | met | met | met: "reverses the required order" | met |
| p3 | met | met | met: "`AUTO` must come after `")"`, not before the `HITL` keyword" | met |

- Divergence: none.
- **Verdict: PASS**
- Errors: none.
- Hesitations: 0. p1: "No assumption beyond the given text was required for these four judgments." p2's only assumption is that answer words are free-form (`deploy.yes`).

## X06: Which decisions may the agent make?

| Probe | D1 (Q1) only `wording`, only when determined | D2 (Q2) No: no AUTO, and confidence alone is not enough | D3 (Q3) human asked "Short or detailed release notes?" |
|---|---|---|---|
| p1 | met: "Only the **`wording`** decision … may be resolved by the agent itself" | met: "No … `AUTO` is not inherited, implied, or transferable"; "A confidence score alone does not establish certainty" | met: "The human is asked the message 'Short or detailed release notes?'" |
| p2 | met | met: "it is not inherited, implied, or extended to other `HITL` statements" | met |
| p3 | met | met: "It is not a global or inherited setting" | met: "the flow suspends at `HITL:wording(...)` until a usable human response" (and states "this is not a 'fallback' in the `FALLBACK`-mechanism sense") |

- Divergence: none. p1 and p2 raise an extra gap (what happens with no FALLBACK and no usable response) and fill it with the same assumption: execution stays suspended, as with WAIT. p3 comes to the same conclusion.
- **Verdict: PASS**
- Errors: none. p3 says "it falls back to the normal `HITL` behavior" but explicitly separates this from `FALLBACK`, so it gets no FALLBACK-CONFUSION tag.
- Hesitations: 0. The FALLBACK-absence gap is not about AUTO's placement or what it binds to.

---

## Error tally

| Tag | Count | Instances |
|---|---|---|
| FORM | 0 | none |
| SCOPE | 0 | none |
| DANGER | 0 | none |
| OVERCAUTION | 0 | none |
| FALLBACK-CONFUSION | 0 | none |
| OTHER | 0 | none (p2 X04's "ends normally" after STOP is noted but not material) |

Because there are no errors, no spec sentences are cited as involved in one. The sentences probes relied on most for correct answers:
- "`AUTO` is written directly after the closing parenthesis of `HITL(...)`, on the same line. It marks that one `HITL` as automatically resolvable."
- "`HITL` must not be silently replaced by an agent decision unless that `HITL` is explicitly marked with `AUTO`."
- "`AUTO` and `FALLBACK` are different mechanisms…"

## Hesitations about the AUTO form

Total: **0**. The only near-misses are the X01 assumption entries in p1 (#3) and p2 ("`AUTO` placement"). Both list the placement as an assumption only because the task asked for every assumption, and both call it unambiguous.

---

## CONF probe (B-CONF-p1)

The probe lists 11 items. All of them concern HITL, AUTO, FALLBACK or WHEN:

1. What "the `WHEN <name>.<answer>` constructs that follow" covers (HITL/WHEN).
2. A named HITL with no WHEN: is there any set of valid answers? (HITL/FALLBACK)
3. What happens after a FALLBACK flow that does not STOP or BREAK (FALLBACK).
4. REQUIRE has an explicit rule against continuing in degraded mode; HITL/FALLBACK has none (HITL/FALLBACK).
5. Whether an AUTO-resolved answer must be one of the answers the following WHENs test; "protocol-compatible" is not defined (AUTO semantics).
6. How long outcomes persist and how they are namespaced, across loops and names (HITL).
7. No FALLBACK plus an unusable response: is the wait indefinite? (HITL/FALLBACK)
8. A response that matches more than one answer (HITL).
9. Whether a FALLBACK flow can hold another HITL to retry the decision (FALLBACK/HITL).
10. BREAK inside a FALLBACK inside a LOOP (FALLBACK).
11. Whether an AUTO outcome is overwritten when the same HITL runs again (AUTO semantics).

Items specific to variant B's AUTO form (a trailing `AUTO` after `)` on the HITL line): **none**. Items 5 and 11 are about what AUTO does, not about how it is written or what it binds to. They would apply equally to any placement.

---

```
VARIANT B
scenarios_passed: 6/6
probe_D_items_met: 66/66
divergent_scenarios: []
errors_by_tag: FORM=0 SCOPE=0 DANGER=0 OVERCAUTION=0 FALLBACK-CONFUSION=0 OTHER=0
hesitations_about_AUTO_form: 0
conf_items_about_AUTO_form: 0
```
