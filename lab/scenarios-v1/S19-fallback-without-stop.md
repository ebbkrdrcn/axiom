# S19 — Execution trace: FALLBACK flow that does not STOP

Type: execution trace · Edge cases: what happens after a fallback flow (F-11)

## Task
Consider this DSL:
```text
HITL("Which region should we deploy to?")
  → FALLBACK
      → TRANSITION "Deferred"
      → EMIT deferral-notice
TRANSITION "Deploying"
DELEGATE deployment
```
Injected event: the human never responds.

Produce the step-by-step execution. Is `TRANSITION "Deploying"` executed? What is the final process state?

## Expected
### Determined by spec
- D1 The response is unavailable → the fallback flow runs: `TRANSITION "Deferred"` then `EMIT deferral-notice`, sequentially. (FALLBACK)
- D2 The agent does not invent a region. (FALLBACK, HITL)

### Underdetermined (→ findings)
- U1 Whether execution continues with `TRANSITION "Deploying"` after a fallback flow that does not end in STOP (F-11 / DP-6). Final state depends on it.

### Pass rule
D1–D2 in all probes; consistent answer to U1.
