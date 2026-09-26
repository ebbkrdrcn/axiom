# S13 — Execution trace: AUTO under uncertainty

Type: execution trace · Edge cases: AUTO syntax, AUTO↔HITL binding, AUTO uncertain

## Task
Consider this DSL:
```text
DELEGATE dependency-upgrade
VERIFY dependency-upgrade
AUTO HITL("Merge the dependency upgrade?")
WHEN merge.approved
  → TRANSITION "Merged"
WHEN merge.declined
  → TRANSITION "Deferred"
```
Context: the process's merge criterion is "merge when verification accepts the upgrade". `VERIFY dependency-upgrade` establishes `accepted`. However, the upgrade's changelog announces a breaking API change that the criterion does not address, and two maintainers' notes disagree about whether breaking changes may be merged. Later, a human answers "Declined."

1. Is the line `AUTO HITL("Merge the dependency upgrade?")` valid syntax?
2. Produce the step-by-step execution.

## Expected
### Determined by spec
- D1 The decision is uncertain (contradictory information; criteria do not address the case; materially different decisions remain compatible). Automatic resolution is not permitted; the agent must not guess or rely on a confidence score. (AUTO)
- D2 Human input is required: the HITL question is put to a human and execution waits for the response. (AUTO, HITL)
- D3 After "Declined": `TRANSITION "Deferred"`; `TRANSITION "Merged"` is not executed. (WHEN)
- D4 VERIFY `accepted` alone does not authorize the merge. (AUTO, VERIFY)

### Underdetermined (→ findings)
- U1 (Q1) The spec defines no syntax for AUTO, so validity of `AUTO HITL(...)` cannot be determined (F-01, F-02).
- U2 How the human's answer is bound to the condition identifier `merge` (F-03).

### Pass rule
D1–D4 in all probes; consistent answer to Q1.
