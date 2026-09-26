# S16 — Execution trace: test failed, then passed (baseline)

Type: execution trace · Edge cases: multi-line WHEN flows, BREAK, outcome names given by events

## Task
Consider this DSL:
```text
LOOP:tdd
  DELEGATE implementation
  DELEGATE tests
  VERIFY tests
  WHEN tests.passed
    → TRANSITION "Review"
    → BREAK
  WHEN tests.failed
    → TRANSITION "Debugging"
    → DELEGATE diagnosis
EMIT source-code
```
Injected events:
- Iteration 1: `VERIFY tests` establishes `failed`.
- Iteration 2: `VERIFY tests` establishes `passed`.

Produce the step-by-step execution until execution ends, and state the final process state.

## Expected
### Determined by spec
- D1 Iter 1: DELEGATE implementation → DELEGATE tests → VERIFY tests (failed) → `WHEN tests.passed` skipped → `WHEN tests.failed`: TRANSITION "Debugging" → DELEGATE diagnosis → end of body, loop repeats.
- D2 Iter 2: DELEGATE implementation → DELEGATE tests → VERIFY tests (passed) → TRANSITION "Review" → BREAK exits loop; `WHEN tests.failed` is not evaluated.
- D3 EMIT source-code executes once, after the loop; execution ends. Final state "Review".

### Underdetermined (→ findings)
- none expected (baseline control scenario).

### Pass rule
D1–D3 in all probes.
