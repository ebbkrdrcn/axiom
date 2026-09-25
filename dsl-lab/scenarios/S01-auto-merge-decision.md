# S01 — Authoring: AUTO-permitted merge decision

Type: authoring · Edge cases: AUTO syntax, AUTO↔HITL binding

## Task
Write go_harness DSL for the following requirement:

"Delegate the implementation and verify it. Then a merge decision is needed: the agent may make the merge decision itself when the decision is clearly determined by the available information and criteria; otherwise a human must be asked "Merge this change?". If the decision is to merge, transition to state "Merged". If the decision is not to merge, transition to state "Rework"."

Output the DSL in a code block, then list every assumption you had to make.

## Expected
### Determined by spec
- D1 `DELEGATE implementation` precedes `VERIFY implementation`. (DELEGATE, VERIFY)
- D2 The human decision is `HITL("Merge this change?")`. (HITL)
- D3 Automatic resolution is expressed with `AUTO`; without it the agent may not replace the HITL decision. (HITL: "must not be silently replaced … unless … AUTO")
- D4 `AUTO` contains no `WHEN`/`→`; no `WHEN *.uncertain` (or any uncertainty condition) appears anywhere. (AUTO)
- D5 Two `WHEN` constructs route to `TRANSITION "Merged"` / `TRANSITION "Rework"`. (WHEN, TRANSITION)

### Underdetermined (→ findings)
- U1 Concrete syntax of AUTO and how it is attached to this HITL (F-01, F-02).
- U2 Condition names for the decision outcome used in WHEN (F-03).

### Pass rule
All probes satisfy D1–D5 and converge on the same form for U1/U2. Under the baseline spec, U1/U2 are expected to diverge.
