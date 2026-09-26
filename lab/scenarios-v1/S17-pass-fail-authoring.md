# S17 — Authoring: outcome names for pass/fail wording

Type: authoring · Edge cases: VERIFY outcome names in WHEN (F-03), multiple WHENs

## Task
Write DSL for the following requirement:

"Delegate the test suite, then verify it. If the tests pass, move to state "Review". If the tests fail, move to state "Debugging" and delegate a diagnosis."

Output the DSL in a code block, then list every assumption you had to make.

## Expected
### Determined by spec
- D1 `DELEGATE <tests-id>` precedes `VERIFY <tests-id>` with the same identifier. (DELEGATE, VERIFY)
- D2 Two independent `WHEN` constructs; the fail-flow contains `TRANSITION "Debugging"` then `DELEGATE diagnosis` in that order (one sequential flow). (WHEN)
- D3 No LOOP, no STOP needed. (STOP: normal end)

### Underdetermined (→ findings)
- U1 Outcome names: `.accepted/.rejected` vs `.passed/.failed` (F-03 / DP-2).

### Pass rule
D1–D3 in all probes; all probes use the same outcome names.
