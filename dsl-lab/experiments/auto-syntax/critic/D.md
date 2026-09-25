# Critic report: variant D

Variant D form: `AUTO` goes on its own line directly before the `HITL`, at the same indentation (`hitl = [ "AUTO" , NL ] , "HITL" , ...`).

Inputs read: `variants/D.md`, `rendered/D/X01`–`X06`, `probes/D-X0{1..6}-p{1,2,3}.md`, `probes/D-CONF-p1.md`.

**Counting rule for hesitations.** A hesitation is counted only when a probe says that the placement or binding of AUTO is unclear, underdetermined by the spec, or had to be assumed. Some probes list AUTO placement in their "Assumptions" section but justify it only as required by the spec, for example "as required by the grammar" or "directly follows the spec's rule". These entries are **not** counted as hesitations. They are listed separately in the "Hesitations" section below so that the choice can be checked.

---

## X01: Authoring, one auto-resolvable decision

All three probes produced the same program:

```text
DELEGATE implementation
VERIFY implementation
AUTO
HITL:merge("Merge this change?")
  → FALLBACK
      → TRANSITION "Blocked"
        STOP
WHEN merge.approved
  → TRANSITION "Merged"
WHEN merge.declined
  → TRANSITION "Rework"
```

| D-item | p1 | p2 | p3 |
|---|---|---|---|
| D1: AUTO in the variant form, on the merge HITL | met: `AUTO` / `HITL:merge(...)` on consecutive lines, same indentation | met: same | met: same |
| D2: named HITL, two WHENs on the same name | met: `merge.approved` / `merge.declined` | met: same | met: same |
| D3: FALLBACK with TRANSITION "Blocked" then STOP | met: nested second form (`→ TRANSITION "Blocked"` / `STOP`), which the spec lists as equivalent | met: same | met: same. p3 says so explicitly: "follows the spec's example exactly … second equivalent form" |
| D4: no uncertainty condition, no flow inside AUTO | met | met | met |

- **Divergence:** none. The three outputs are identical character for character.
- **Verdict:** PASS
- **Errors:** none
- **Hesitations:** 0

## X02: Authoring, two decisions, only one auto-resolvable

- p1: `AUTO` / `HITL:format(...)` … blank line … `HITL:approval(...)`
- p2: `AUTO` / `HITL:notes(...)` … `HITL:approve(...)`
- p3: `AUTO` / `HITL:notes(...)` … blank line … `HITL:approval(...)`

| D-item | p1 | p2 | p3 |
|---|---|---|---|
| D1: AUTO on the notes-style HITL only | met: `AUTO` directly above `HITL:format(...)` | met: `AUTO` directly above `HITL:notes(...)` | met: `AUTO` directly above `HITL:notes(...)` |
| D2: release approval has no AUTO | met: "the second `HITL` has no `AUTO`" | met: "no `AUTO` line precedes the second `HITL`" | met: "no `AUTO` line precedes that `HITL`" |
| D3: two named HITLs, each followed by its own WHENs, in order | met: `format.short/detailed`, then `approval.approved/rejected` | met: `notes.*`, then `approve.*` | met: `notes.*`, then `approval.*` |

- **Divergence:** none material. The probes differ only in identifier names and in blank lines between the two groups. None of them puts a blank line between `AUTO` and its `HITL`.
- **Verdict:** PASS
- **Errors:** none
- **Hesitations:** 0
- **Note, not tagged:** p2 assumption 3 paraphrases the spec loosely: "the specification says a program must not have behavior invented for it". The spec has no such sentence. This has no effect on any D-item.

## X03: Trace, AUTO with a determined decision

| D-item | p1 | p2 | p3 |
|---|---|---|---|
| D1: determined, agent resolves, no human asked | met: "the agent resolves the decision itself. The human is not asked." | met: "the agent resolves the decision itself; the human is not asked" | met: "`AUTO` resolves the decision automatically" |
| D2: `merge.approved`, "Merged" transition, `declined` not satisfied | met: Steps 5 and 6 | met: Steps 5 and 6 | met: Steps 5 and 6 |
| D3: FALLBACK not used; no human online is irrelevant | met: "The human being offline is immaterial" | met: "has no effect on this run" | met: "that fact simply never becomes operative" |
| D4: final state "Merged" | met | met | met |

- **Divergence:** none material. p3 considers another reading in which "a changelog listing only bug fixes" is not conclusive, which would make the decision uncertain. p3 rejects that reading and concludes "Merged" like the others.
- **Verdict:** PASS
- **Errors:** none
- **Hesitations:** 0. All three probes treat the binding of `AUTO` to `HITL:merge` as settled. For example, p2 writes: "This line is immediately followed by a `HITL`, so it is valid and marks that `HITL:merge(...)`". The assumptions they do raise are about how sufficiency is judged, not about the AUTO form.

## X04: Trace, AUTO with an uncertain decision and no human response

| D-item | p1 | p2 | p3 |
|---|---|---|---|
| D1: uncertain; 90% does not count; agent must not decide | met: "A confidence score alone does not establish certainty … The agent must not decide" | met: criterion "silent on breaking changes", notes "disagree", and it quotes the confidence rule | met: "despite its 90% confidence … does not resolve" |
| D2: human is asked | met: "The human is asked 'Merge the dependency upgrade?'" | met: "the runtime poses the question … to a human" | met: "the human is asked" |
| D3: no response leads to FALLBACK ("Blocked", then STOP); no WHEN evaluated | met: "never reached and never evaluated" | met: "never reached" | met: "They are never evaluated" |
| D4: final state "Blocked" | met | met | met |

- **Divergence:** none material. All three assume that the runtime eventually treats the missing response as "unavailable". p2 also mentions the other literal reading, suspension forever, as permitted by the spec. That point concerns the timeout, not AUTO, and p2's conclusion is the same.
- **Verdict:** PASS
- **Errors:** none
- **Hesitations:** 0

## X05: Validity of AUTO placements

| D-item | p1 | p2 | p3 |
|---|---|---|---|
| D1: snippet 1 VALID | met: cites the `hitl` production and "own line directly before a `HITL`, at the same indentation" | met: same citation | met: same citation |
| D2: snippet 2 INVALID | met: "`AUTO` applies only to `HITL`" and "not immediately followed by a `HITL` is invalid" | met: same | met: same |
| D3: snippet 3 INVALID | met: "a `NL` (newline) token is required between `AUTO` and `HITL`" | met: "there is no `NL` between `AUTO` and `HITL`" | met: "mandates a line break between `AUTO` and `HITL`" |
| D4: snippet 4 INVALID | met: "`AUTO` never contains a flow and uncertainty is not a condition" | met: same | met: same |

- **Divergence:** none
- **Verdict:** PASS
- **Errors:** none
- **Hesitations:** 0. p1 and p3 both state that no assumptions were needed.

## X06: Which decisions the agent may make (scope)

| D-item | p1 | p2 | p3 |
|---|---|---|---|
| D1 (Q1): only `wording`, only when sufficiently determined | met: "Only the `wording` decision … only if … exactly one of `short`/`detailed` is reasonably compatible" | met: "only when it is sufficiently determined" | met: "Only the wording decision … only when it can determine a single protocol-compatible decision" |
| D2 (Q2): no, because there is no AUTO and confidence alone is not certainty | met: gives both reasons | met: gives both reasons | met: gives both reasons, "either of which is sufficient" |
| D3 (Q3): the human is asked "Short or detailed release notes?" | met | met | met |

- **Divergence:** none material. All three add the same assumption about what happens when `HITL:wording` has no FALLBACK: execution stays suspended. That point concerns FALLBACK, not AUTO.
- **Verdict:** PASS
- **Errors:** none
- **Hesitations:** 0. All three bind AUTO correctly using "marks only the `HITL` on the immediately following line", and none of them says the binding is unclear.

---

## Error tally

| Tag | Count | Instances |
|---|---|---|
| FORM | 0 | none |
| SCOPE | 0 | none |
| DANGER | 0 | none |
| OVERCAUTION | 0 | none |
| FALLBACK-CONFUSION | 0 | none. All trace and interpretation probes correctly separate "AUTO cannot resolve, so the human is asked" from "the human gives no usable response, so FALLBACK". This follows the spec sentence: "When `AUTO` cannot resolve a decision, the decision goes to the human through the normal `HITL`; this is not a fallback." |
| OTHER | 0 | none |

## Hesitations about the AUTO form

Strict count (the rule used in the summary block): **0**.

The following entries mention AUTO placement or binding inside an "Assumptions" list. Each one justifies the placement as required by the spec, so none is counted. The loose count, which would include them, is 6:

- X01-p1 #3, "Placement and scope of `AUTO`": "per the required syntax `AUTO NL HITL ...`"
- X01-p2, "`AUTO` placement": "as required by the grammar (`AUTO` on its own line, immediately preceding the `HITL`)"
- X01-p3 #6: "Per spec, `AUTO` can only immediately precede a `HITL` and applies only to that one `HITL`."
- X02-p1 #4, X02-p2 #2, X02-p3 #3, "`AUTO` only on the first `HITL`": each derives this from the requirement text and the rule that a HITL without AUTO is always asked. X02-p2's list header frames its items as choices the spec leaves open, but the AUTO item itself cites the spec as deciding the placement.

## CONF probe (D-CONF-p1)

All 14 items concern HITL, AUTO, FALLBACK, or WHEN outcomes:

1. WHEN cannot tell a VERIFY outcome from a HITL outcome (outcome namespace). HITL. Not form-specific.
2. What "the `WHEN <name>.<answer>` constructs that follow" covers. HITL. Not form-specific.
3. What it means for a response to "correspond" to an answer (literal or semantic match). HITL/FALLBACK. Not form-specific.
4. Duplicate HITL names, with no "most recent wins" rule as TRANSITION has. HITL. Not form-specific.
5. A WHEN that names a HITL which does not exist. HITL. Not form-specific.
6. How to parse "must not be *silently* replaced … unless marked `AUTO`". AUTO semantics. Not form-specific.
7. AUTO before an unnamed `HITL("...")`, which the grammar allows. AUTO. It quotes variant D's production `[ "AUTO", NL ], "HITL", [ ":", identifier ]`, but the problem (AUTO with no `<name>` to bind) exists whatever form AUTO takes. **Borderline. Not counted as form-specific.**
8. "Protocol-compatible decision" is never defined. AUTO semantics. Not form-specific.
9. Whether AUTO's answer must be one of the answers the WHENs test. AUTO semantics. Not form-specific.
10. The "sufficiently determined" threshold is open-ended. AUTO semantics. Not form-specific.
11. Whether execution rejoins the normal flow after a FALLBACK that does not STOP. FALLBACK. Not form-specific.
12. Whether a HITL inside a FALLBACK may ask the same question again. FALLBACK. Not form-specific.
13. "Insufficient" is a judgment call. FALLBACK. Not form-specific.
14. Whether FALLBACK applies after AUTO defers to the human (the AUTO table does not mention FALLBACK). AUTO/FALLBACK interplay. Not form-specific.

AUTO-related items: 6, 7, 8, 9, 10, 14. **None is about variant D's form** (a separate line before the HITL, same indentation, binding only to the immediately following line). Item 7 is the only one that uses D's grammar text.

The CONF probe did not raise any D-specific form question. Possible ones include whether a blank line or comment may sit between `AUTO` and `HITL`, and how to write `AUTO` + `HITL` as a `→` item inside a WHEN, FALLBACK, or FORK flow (`→ AUTO` followed by an aligned `HITL` line). No scenario probe hesitated on either question.

---

```
VARIANT D
scenarios_passed: 6/6
probe_D_items_met: 66/66
divergent_scenarios: []
errors_by_tag: FORM=0 SCOPE=0 DANGER=0 OVERCAUTION=0 FALLBACK-CONFUSION=0 OTHER=0
hesitations_about_AUTO_form: 0
conf_items_about_AUTO_form: 0
```
