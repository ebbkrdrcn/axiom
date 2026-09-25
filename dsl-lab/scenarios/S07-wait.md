# S07 — Interpretation: what happens at and after WAIT

Type: interpretation · Edge cases: after WAIT

## Task
Consider this go_harness DSL:
```text
DELEGATE data-migration
WAIT
VERIFY data-migration
WHEN data-migration.accepted
  → TRANSITION "Migrated"
```
Answer:
1. What does `WAIT` wait for here?
2. What executes immediately after `WAIT` ends?
3. Does reaching `VERIFY data-migration` imply that the migration succeeded?
4. What happens if the awaited event never occurs?

## Expected
### Determined by spec
- D1 (Q2) `VERIFY data-migration` — execution continues according to the surrounding flow, i.e. the next statement. (WAIT, Flow)
- D2 (Q3) No. WAIT implies neither success nor failure; DELEGATE does not imply correctness; VERIFY is the evaluation. (WAIT, DELEGATE, VERIFY)

### Underdetermined (→ findings)
- U1 (Q1) WAIT takes no argument; the DSL does not say which event/response it waits for (F-09). A correct answer says the spec leaves it unspecified (may name "completion of the delegated migration" only as an assumption).
- U2 (Q4) No timeout/fallback defined for WAIT; execution stays suspended (F-09).

### Pass rule
D1, D2 in all probes; Q1/Q4 answered consistently.
