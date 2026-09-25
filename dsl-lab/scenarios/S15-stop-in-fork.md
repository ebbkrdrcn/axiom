# S15 — Execution trace: STOP inside a FORK branch

Type: execution trace · Edge cases: STOP vs concurrent branches

## Task
Consider this go_harness DSL:
```text
FORK
  → DELEGATE lint
      VERIFY lint
      WHEN lint.rejected
        → STOP
  → DELEGATE docs
      EMIT docs
JOIN
EMIT build
```
Injected events:
- `VERIFY lint` establishes `rejected`.
- At that moment the docs branch has executed `DELEGATE docs` but has not yet executed `EMIT docs`.

Produce the step-by-step execution. Is `EMIT docs` executed? Is `JOIN` completed? Is `EMIT build` executed?

## Expected
### Determined by spec
- D1 STOP terminates the entire execution, including concurrent branches ("Use STOP to terminate the entire execution"; "No subsequent statement is executed after STOP"). (STOP, BREAK)
- D2 EMIT docs is not executed; JOIN does not complete; EMIT build is not executed.

### Underdetermined (→ findings)
- U1 The spec does not explicitly address STOP inside a concurrent branch (F-15).

### Pass rule
D1–D2 in all probes.
