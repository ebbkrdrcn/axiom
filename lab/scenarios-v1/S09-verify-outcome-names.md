# S09 — Interpretation: VERIFY outcome names used in WHEN

Type: interpretation · Edge cases: VERIFY outcome names (passed/accepted/…) in WHEN

## Task
Consider this DSL:
```text
DELEGATE implementation
VERIFY implementation
WHEN implementation.passed
  → TRANSITION "Review"
WHEN tests.failed
  → TRANSITION "Debugging"
```
1. Which outcome names can `VERIFY implementation` establish?
2. Is `WHEN implementation.passed` a valid condition here?
3. Is `WHEN tests.failed` valid here, and where does `tests` come from?
4. If the verification of the implementation is negative, which TRANSITION (if any) is executed?

## Expected
### Determined by spec
- D1 VERIFY "may establish outcomes that can be used by WHEN"; the spec lists no outcome vocabulary. (VERIFY)

### Underdetermined (→ findings)
- U1 (Q1) Outcome names are not defined; examples use `.accepted/.rejected` (VERIFY section) and `.passed/.failed` (WHEN section) (F-03).
- U2 (Q2) Whether `implementation.passed` is valid after `VERIFY implementation` (F-03).
- U3 (Q3) `tests` is produced by no statement; the spec has no rule for condition identifiers that nothing established (F-03).
- D2 (Q4, partial) `TRANSITION "Review"` is not executed on a negative verification under every reading.
- U4 (Q4) Whether `TRANSITION "Debugging"` can execute depends on U3 (F-03).

### Pass rule
All probes state D1 and give the same answers to Q1–Q4. Expected to diverge on the baseline spec.
