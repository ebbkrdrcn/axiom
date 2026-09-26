# X03 — Trace: AUTO, decision sufficiently determined

## Task
Consider this go_harness DSL:
```text
DELEGATE dependency-upgrade
VERIFY dependency-upgrade
HITL:merge("Merge the dependency upgrade?")
  → AUTO
  → FALLBACK
      → TRANSITION "Blocked"
      → STOP
WHEN merge.approved
  → TRANSITION "Merged"
WHEN merge.declined
  → TRANSITION "Deferred"
```
Context: the process's merge criterion is "merge when verification accepts the upgrade and the changelog announces no breaking change". The process gives the agent authority to merge dependency upgrades. `VERIFY dependency-upgrade` establishes `accepted`. The changelog lists only bug fixes. No human is currently online.

Produce the step-by-step execution and state the final process state. Is a human asked? Is the FALLBACK used?

## Expected
- D1 The decision is sufficiently determined → the agent resolves it. No human is asked.
- D2 `merge.approved` is established; `TRANSITION "Merged"` executes; `WHEN merge.declined` is not satisfied.
- D3 FALLBACK is not used. No human being online is irrelevant, because no human is asked.
- D4 Final state "Merged".
### Pass rule
D1–D4 in all probes.
