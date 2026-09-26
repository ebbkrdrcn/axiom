# S10 — Interpretation: scope of multi-line flows after →

Type: interpretation · Edge cases: scope of multi-line flows after →

## Task
Consider this DSL:
```text
VERIFY review
WHEN review.rejected
  → DELEGATE correction
      VERIFY correction
  → TRANSITION "Rework"
EMIT review-report
```
Assume `VERIFY review` establishes the outcome `rejected`.

1. Which statements belong to the WHEN flow?
2. Are the statements in the WHEN flow executed sequentially or concurrently, and in what order?
3. Is `VERIFY correction` part of the WHEN flow?
4. Is `EMIT review-report` part of the WHEN flow? Is it executed?
5. If `VERIFY review` had established `accepted` instead, which statements would execute?

## Expected
### Determined by spec
- D1 (Q2) Sequentially in declaration order: DELEGATE correction, VERIFY correction, TRANSITION "Rework". The `→` lines under WHEN "form the flow"; only FORK makes `→` concurrent. (WHEN, Syntax/Conditional Flow, Flow)
- D2 (Q4) EMIT review-report is outside the WHEN (outer indentation) and executes after the WHEN flow. (Syntax/Scope)
- D3 (Q5) VERIFY review → WHEN not satisfied, flow skipped → EMIT review-report. (WHEN, Flow)

### Underdetermined (→ findings)
- U1 (Q1/Q3) Nested statements under a `→` are defined only for FORK branches (Syntax/Forked Flow); for WHEN it is only implied by the generic Scope rule (F-04). Canonical reading: VERIFY correction belongs to the WHEN flow.

### Pass rule
D1–D3 in all probes; all probes agree VERIFY correction is in the WHEN flow.
