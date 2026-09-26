# S18 — Execution trace: FORK without JOIN; sequential DELEGATEs

Type: execution trace · Edge cases: FORK without JOIN (F-12), DELEGATE completion (F-16)

## Task
Consider this DSL:
```text
DELEGATE design
DELEGATE implementation
FORK
  → DELEGATE docs
  → DELEGATE changelog
EMIT release
```
Injected events:
- The actor for `design` takes a long time to deliver the design.
- After the FORK starts, `docs` takes 1 hour and `changelog` takes 5 minutes.

Produce the step-by-step execution. Answer explicitly:
1. Can `DELEGATE implementation` start before the design has been delivered?
2. When is `EMIT release` executed relative to the docs and changelog branches?
3. Is it guaranteed that docs exist when `EMIT release` executes?

## Expected
### Determined by spec
- D1 (Q2) No JOIN → `EMIT release` executes immediately after the FORK has started its branches, while they are still running. (FORK: "If no JOIN follows…")
- D2 (Q3) No — nothing waits for the branches. (FORK, JOIN)
- D3 Within the top-level flow, statements are sequential; the two branches run concurrently. (Flow, FORK)

### Underdetermined (→ findings)
- U1 (Q1) Whether a `DELEGATE` "completes" when the work is assigned or when the actor delivers the result (F-16 / DP-7). Flow says a statement starts only after the previous one completed, but DELEGATE completion is not defined.

### Pass rule
D1–D3 in all probes; consistent answer to Q1.
