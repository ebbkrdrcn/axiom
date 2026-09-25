# S11 — Execution trace: BREAK inside FORK inside LOOP

Type: execution trace · Edge cases: BREAK inside FORK inside LOOP

## Task
Consider this go_harness DSL:
```text
LOOP:review
  FORK
    → DELEGATE security-review
        VERIFY security-review
        WHEN security-review.rejected
          → BREAK
    → DELEGATE docs-review
        VERIFY docs-review
  JOIN
  TRANSITION "Reviewed"
EMIT review-summary
```
Injected events:
- Iteration 1: both branches start.
- `VERIFY security-review` establishes `rejected` while the docs-review branch is still running (its VERIFY has not happened yet).

Produce the step-by-step execution until execution ends or cannot proceed. State explicitly what happens to the docs-review branch, to `JOIN`, to `TRANSITION "Reviewed"`, and to `EMIT review-summary`.

## Expected
### Determined by spec
- D1 BREAK exits the current LOOP (`review`); it does not terminate the entire execution. (BREAK)
- D2 The loop does not start another iteration; `TRANSITION "Reviewed"` is not executed in iteration 1. (BREAK, LOOP)
- D3 `EMIT review-summary` is executed after the loop is exited. (BREAK, Flow)

### Underdetermined (→ findings)
- U1 Whether BREAK from inside a concurrent FORK branch is permitted at all (F-08).
- U2 Fate of the sibling docs-review branch (cancelled / runs to completion / awaited) and of the pending JOIN (F-08).
- U3 Ordering of EMIT review-summary relative to docs-review completion (F-08).

### Pass rule
D1–D3 in all probes and the same answer for U1–U3. Expected to diverge on the baseline spec.
