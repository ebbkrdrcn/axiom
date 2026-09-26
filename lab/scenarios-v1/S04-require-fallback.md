# S04 — Authoring: REQUIRE + HITL with FALLBACK

Type: authoring · Edge cases: when FALLBACK triggers, multi-line flow after →, REQUIRE

## Task
Write DSL for the following requirement:

"The process needs the deployment-target before anything else. Then ask a human "Which region should we deploy to?". If no usable answer is obtained from the human, transition to state "Blocked" and terminate the whole execution. Otherwise, delegate the deployment and emit a deployment-log."

Output the DSL in a code block, then list every assumption you had to make.

## Expected
Canonical answer:
```text
REQUIRE deployment-target
HITL("Which region should we deploy to?")
  → FALLBACK
      → TRANSITION "Blocked"
      → STOP
DELEGATE deployment
EMIT deployment-log
```
### Determined by spec
- D1 `REQUIRE deployment-target` first. (REQUIRE)
- D2 `HITL("…")` with a string message. (HITL)
- D3 "No usable answer" handled by `→ FALLBACK` under the HITL, not by a WHEN on a timeout/no-response condition. (FALLBACK)
- D4 Fallback flow contains `TRANSITION "Blocked"` then `STOP` (not BREAK). (STOP, BREAK)
- D5 `DELEGATE deployment` and `EMIT deployment-log` follow the HITL in the normal flow (not inside FALLBACK). (FALLBACK: "not … after the normal flow"; Flow)
- D6 No AUTO (the requirement gives the agent no authority to answer). (HITL)

- D7 (from iteration 2) Either multi-statement form is accepted: one `→` per statement, or one `→` plus nested lines — the spec declares them equivalent (FALLBACK "Form").

### Underdetermined (→ findings)
- (iteration 1) U1 Form of a multi-statement fallback flow — resolved by spec edit in iteration 1.

### Pass rule
D1–D6 in all probes (D7 from iteration 2).
