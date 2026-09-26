# S03 — Authoring: parallel reviews with JOIN

Type: authoring · Edge cases: multi-line branch scope after →, FORK/JOIN placement

## Task
Write DSL for the following requirement:

"Run a security review and a performance review in parallel. Each review is delegated and then verified within its own parallel flow. Continue only after both flows have finished, then transition to state "Release"."

Output the DSL in a code block, then list every assumption you had to make.

## Expected
Canonical answer:
```text
FORK
  → DELEGATE security-review
      VERIFY security-review
  → DELEGATE performance-review
      VERIFY performance-review
JOIN
TRANSITION "Release"
```
### Determined by spec
- D1 One `FORK` with exactly two `→` branches. (FORK)
- D2 Each `VERIFY` is nested (indented) under its branch's `DELEGATE`, not a separate `→` (a separate `→` would be a separate concurrent branch). (FORK, Syntax/Forked Flow)
- D3 `JOIN` follows the FORK at the FORK's indentation. (JOIN)
- D4 `TRANSITION "Release"` after JOIN. (Flow)

### Underdetermined (→ findings)
- U1 Required indentation width for branch-nested statements (example uses column of the text after `→ `) (F-13).

### Pass rule
D1–D4 in all probes; no structural divergence.
