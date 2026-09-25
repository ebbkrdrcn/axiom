# S14 — Execution trace: a FORK branch fails; JOIN; multiple WHEN matches

Type: execution trace · Edge cases: FORK branch fails, JOIN, more than one WHEN satisfied

## Task
Consider this go_harness DSL:
```text
FORK
  → DELEGATE unit-tests
      VERIFY unit-tests
  → DELEGATE integration-tests
      VERIFY integration-tests
JOIN
WHEN unit-tests.accepted
  → TRANSITION "Ready"
WHEN integration-tests.rejected
  → TRANSITION "Debugging"
```
Injected events:
- `VERIFY unit-tests` establishes `accepted`.
- `VERIFY integration-tests` establishes `rejected`; it finishes later than the unit-tests branch.

Produce the step-by-step execution and state the final process state.

## Expected
### Determined by spec
- D1 Both branches execute concurrently; within each branch DELEGATE precedes VERIFY. (FORK)
- D2 A rejected VERIFY is an outcome, not an aborted flow; the integration branch completes. JOIN waits for both branches, then execution continues. (VERIFY, JOIN)

### Most likely reading (by inference only — F-06)
- D3 After JOIN, WHEN constructs are evaluated in declaration order; `unit-tests.accepted` holds → TRANSITION "Ready"; then `integration-tests.rejected` holds → TRANSITION "Debugging". (WHEN is a statement; Flow: declaration order; nothing states exclusivity)
- D4 Final state: "Debugging".

### Underdetermined (→ findings)
- U1 Whether multiple satisfied WHENs all execute or only the first (F-06).
- U2 Meaning of "required forked flows" and whether a rejected branch counts as completed (F-12).

### Pass rule
D1–D2 in all probes, and all probes agree on D3/D4 (disagreement = ambiguity F-06).
