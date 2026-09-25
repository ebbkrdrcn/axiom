# S21 — Execution trace: WHEN evaluated before its outcome exists

Type: execution trace · Edge cases: WHEN is not a standing trigger; TRANSITION overwrite

## Task
Consider this go_harness DSL:
```text
TRANSITION "Testing"
WHEN tests.accepted
  → TRANSITION "Review"
DELEGATE tests
VERIFY tests
EMIT test-report
```
Injected event: `VERIFY tests` establishes `accepted`.

Produce the step-by-step execution and state the final process state. Is `TRANSITION "Review"` ever executed?

## Expected
### Determined by spec
- D1 `WHEN tests.accepted` is evaluated once, when reached — before `VERIFY tests` — and is not satisfied then; its flow is skipped. (WHEN rules)
- D2 It is not re-evaluated after `VERIFY tests`; `TRANSITION "Review"` is never executed. (WHEN: "not a standing trigger")
- D3 `EMIT test-report` executes; execution ends normally; final state "Testing". (Flow, STOP, TRANSITION)

### Underdetermined (→ findings)
- U1 Whether referencing an outcome that has not been established yet is invalid or merely unsatisfied (DP-2).

### Pass rule
D1–D3 in all probes.
