# S02 — Authoring: verify-until-accepted loop

Type: authoring · Edge cases: VERIFY outcome names in WHEN, BREAK, scope

## Task
Write DSL for the following requirement:

"Repeatedly: delegate the implementation, then verify it. If the verification accepts it, leave the repetition. If the verification rejects it, delegate a correction and then repeat from the start. After the repetition ends, emit source-code."

Output the DSL in a code block, then list every assumption you had to make.

## Expected
Canonical answer:
```text
LOOP:implementation
  DELEGATE implementation
  VERIFY implementation
  WHEN implementation.accepted
    → BREAK
  WHEN implementation.rejected
    → DELEGATE correction
EMIT source-code
```
### Determined by spec
- D1 `LOOP:<name>` header; body indented under it. (LOOP, Syntax/Scope)
- D2 Body order: DELEGATE → VERIFY → WHEN constructs. (Flow)
- D3 `BREAK` is inside the accept-WHEN flow (not STOP). (BREAK)
- D4 `DELEGATE correction` inside the reject-WHEN flow. (WHEN)
- D5 `EMIT source-code` is after the loop at the outer indentation. (Scope)

### Underdetermined (→ findings)
- U1 Outcome names: the VERIFY example uses `.accepted/.rejected`, the WHEN example uses `.passed/.failed`; neither is declared canonical (F-03).

### Pass rule
D1–D5 in all probes; all probes use the same outcome names.
