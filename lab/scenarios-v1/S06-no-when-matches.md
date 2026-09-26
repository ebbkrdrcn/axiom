# S06 — Interpretation: a WHEN that no outcome matches

Type: interpretation · Edge cases: WHEN with no matching outcome, LOOP repetition

## Task
Consider this DSL:
```text
LOOP:build
  DELEGATE build
  VERIFY build
  WHEN build.accepted
    → BREAK
EMIT build-report
```
In every iteration, `VERIFY build` establishes the outcome `rejected`.

Describe step by step what happens during the first two iterations, and state whether and when `EMIT build-report` is executed.

## Expected
### Determined by spec (by inference; not stated explicitly)
- D1 Iteration 1: DELEGATE build → VERIFY build (rejected) → `WHEN build.accepted` condition not satisfied, its flow is not executed → end of loop body. (WHEN: flow "executed when the condition is satisfied"; Flow: declaration order)
- D2 The loop repeats: iteration 2 is identical. (LOOP: continues until BREAK/STOP)
- D3 An unmatched WHEN is not an error and does not stop, wait, or escalate. (inference, F-05)
- D4 EMIT build-report is never executed while the outcome stays `rejected`; the loop continues indefinitely (LOOP implies no iteration count). (LOOP)

### Underdetermined (→ findings)
- U1 Spec never states the no-match behavior explicitly (F-05).

### Pass rule
D1–D4 in all probes.
