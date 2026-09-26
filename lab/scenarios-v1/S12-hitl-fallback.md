# S12 — Execution trace: HITL no response / insufficient response → FALLBACK

Type: execution trace · Edge cases: when FALLBACK triggers, HITL no response

## Task
Consider this DSL:
```text
DELEGATE release-notes
HITL("Approve the release notes?")
  → FALLBACK
      → TRANSITION "Blocked"
      → STOP
TRANSITION "Published"
EMIT release-notes
```
Produce the step-by-step execution for each of three independent runs:
- Run A: the human responds "Approved."
- Run B: the human never responds.
- Run C: the human responds "I haven't had time to look yet."

## Expected
### Determined by spec
- D1 Run A: DELEGATE → HITL → usable response → FALLBACK flow NOT executed → TRANSITION "Published" → EMIT release-notes → end. (FALLBACK: "not … after the normal flow")
- D2 Run B: response unavailable → fallback flow: TRANSITION "Blocked" → STOP; "Published"/EMIT not executed; agent does not invent an approval. (FALLBACK, STOP, HITL)
- D3 Run C: response cannot be used to continue the normal flow (insufficient) → same fallback flow as Run B. (FALLBACK: "unavailable or insufficient")
- D4 The two `→` lines inside FALLBACK execute sequentially. (Flow)

### Underdetermined (→ findings)
- U1 When a missing response counts as "unavailable" (no timeout concept) (F-11).
- U2 The normal flow does not branch on approve/reject; the spec does not say how the HITL response determines the subsequent flow (F-03). Not required for pass.

### Pass rule
D1–D4 in all probes.
