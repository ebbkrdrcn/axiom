# AUTO placement experiment: report

**Setup.** Four spec variants that differ only in where `AUTO` is written:

| Variant | Form |
|---|---|
| A | `AUTO HITL:x("…")` |
| B | `HITL:x("…") AUTO` |
| C | `HITL:x("…")` followed by an indented `→ AUTO` |
| D | an `AUTO` line directly before `HITL:x("…")` |

- The semantic text, the decision table, the examples and the counter-examples are identical in all four.
- HITL naming (`HITL:<name>`, DP-3 A) is used provisionally in all variants.
- There are 6 scenarios (X01–X06). Each ran on each variant with 3 blind sonnet probes, plus 1 AUTO-focused confusion probe per variant: 76 probes in total.
- One critic graded each variant (`critic/<V>.md`).

## Results

| Variant | Scenarios passed | D-items met | Divergent scenarios | FORM | SCOPE | DANGER | OVERCAUTION | FALLBACK-CONFUSION | OTHER | Hesitations about AUTO form | CONF items about AUTO form |
|---|---|---|---|---|---|---|---|---|---|---|---|
| A (prefix) | 6/6 | 66/66 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| B (suffix) | 6/6 | 66/66 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| C (`→ AUTO`) | 6/6 | 66/66 | 0 | 0 | 0 | 0 | 0 | 0 | 1* | 0 | 0 |
| D (own line) | 6/6 | 66/66 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |

\* C's OTHER error is not about AUTO. In X06-p1 an untested answer (`release.declined`) was treated as a possible outcome. One C probe also briefly misread whether `→ FALLBACK` was present under a HITL that carried `→ AUTO`, then corrected itself. This is a weak signal that stacking `→` items under HITL is harder to scan.

## Interpretation

1. **Ceiling effect: the experiment does not discriminate between the placements.** Once the spec contains a syntax block, a decision table, a worked example and counter-examples, all four placements are learned perfectly by sonnet. The failures in iteration 1 (S01 had 3 different forms) came from the **missing definition**, not from any one placement being unnatural.
2. **Safety behaviour does not depend on the placement.**
   - There were 0 DANGER errors. No probe let the agent decide when the decision was uncertain or when the HITL had no AUTO.
   - There were 0 SCOPE errors. In variant D, AUTO stayed bound to exactly the next HITL.
   - The decision table did this work.
3. **Remaining confusion is independent of the placement.** It sits in HITL, FALLBACK and outcome semantics and is the same in all four variants (new findings F-29…F-35):
   - F-29: a HITL without FALLBACK whose response is unavailable or insufficient. All probes assume it suspends indefinitely.
   - F-30: the scope of "the WHEN constructs that follow", which defines a HITL's answer set.
   - F-31: two definitions of "insufficient": the answer matches no tested answer, or the response does not provide the requested decision.
   - F-32: must an AUTO answer come from the tested answer set? "protocol-compatible" is undefined.
   - F-33: outcome lifetime, overwriting and name reuse, for example in loops. This overlaps DP-2.
   - F-34: flow after a FALLBACK flow that does not stop (DP-6), flagged in all 4 CONF probes.
   - F-35: a response that matches more than one tested answer.

## What would break the tie

Choosing among A–D needs a **harder** test:

- **(a) Cold reading.** Give only the one-line syntax, with no table and no examples. This measures how intuitive each placement is on its own.
- **(b) A weaker model** (haiku) as the probe.
- **(c) Stress programs.** Several HITLs, AUTO inside FORK or LOOP, long messages, and edit tasks such as "make only decision X automatic" or "remove AUTO from Y".

Without such a test, the choice rests on design criteria. On those, A or B is favoured:

- one line
- the AUTO marker cannot be separated from its HITL
- no overloading of `→`
- AUTO is not a free-standing line as in D
