# Critic part E — iteration 03

Scenarios: N06, N07, N08, N09, N10 (scenarios-hard), S01 (scenarios, DSL only).
Spec: `iterations/03/DSL.md`, `iterations/03/ENTITY.md`. Fixture: `iterations/03/fixture/docs/`.
Linter: `iterations/03/lint.txt` (N09 and S01 blocks all VALID). I also ran `tools/dslcheck.py` on every N09/S01 program (including the blocks with no `text` label, which `--md` skips) and on the five N10 snippets. All results agree with lint.txt and with the expected verdicts (A: V1, B: VALID, C: V10, D: VALID, E: V12).

Relevant fixture facts, checked directly:
- TASK-0100: `status: InProgress`, `adr: ADR-0100`, two Acceptance Criteria items, structurally valid. Task `InProgress → Review` requires `verified: accepted`.
- TASK-0101: `status: Review`, structurally valid. `Review → Done` requires `human: approved`.
- ADR-0101: `status: Proposed`. `Proposed → Accepted` requires `verified: accepted; human: approved`, and `Proposed → Rejected` requires `human: rejected`.

Grading convention: a D-item counts as met when the probe's effects match (which statements ran, the outcomes, the statuses, the file changes). Trace formatting differences are not errors (CRITIC-E). Each error gets one tag and one cause.

---

## N06 — Execution: stale verification

Expected: `t1.accepted`. DELEGATE rewrites Description, so `verified: accepted` no longer holds. `TRANSITION t1 "Review"` fails, the fallback runs (state `Reverify`, STOP), and TASK-0100 stays InProgress with only its Description changed.

| Probe | D1 | D2 | D3 | D4 | D5 | Met |
|---|---|---|---|---|---|---|
| s1 | met: "0. validate -> VALID … outcome t1.accepted" | met: "Because `DELEGATE polish` changed the Description after the `VERIFY`, that precondition no longer holds" | met: "TRANSITION t1 "Review" -> failed: precondition "verified: accepted" no longer holds …; fallback" | met: "TRANSITION "Reverify" -> state = "Reverify"" / "STOP -> stop" | met: "Status: `InProgress` — unchanged … rewrote the `## Description` section" | 5/5 |
| s2 | met: "outcome t1.accepted (evidence: item 1 … item 2 …)" | met: "t1's data (the Description section) changed since VERIFY t1, by DELEGATE polish" | met: "failed: precondition "verified: accepted" no longer holds …; fallback" | met: "5. TRANSITION "Reverify" … 6. STOP -> stop" | met: "Final status: `InProgress` — unchanged … only its Description section" | 5/5 |
| h1 | met: "VERIFY t1 -> outcome t1.accepted" | met: "The DELEGATE work altered the Description … invalidated the precondition" | met: "TRANSITION t1 "Review" -> failed: precondition not satisfied; fallback" | met: "state = "Reverify"" / "STOP -> stop" | met: "status remains InProgress … Description section was rewritten" | 5/5 |
| h2 | met: "outcome t1.accepted (evidence: …)" | met: "entity data modified by DELEGATE" | met: "failed: precondition verified: accepted does not hold …; fallback" | met: "Process state: "Reverify"" | met: "Status remains InProgress … Description section rewritten" | 5/5 |
| h3 | met: "outcome t1.accepted" | met: "entity data changed since VERIFY via DELEGATE, not via TRANSITION" | met: "failed: …; fallback" | met: "state = "Reverify"" / "STOP -> stop" | met: "Final status: `InProgress` … Description section rewritten" | 5/5 |
| h4 | met: "VALID" / "outcome t1.accepted" | **not met**: acknowledges "delegated work that modified its Description" but says "`verified: accepted`, which held" | **not met (DANGER)**: "TRANSITION t1 "Review" -> status t1 = "Review"" | **not met**: "Process state: `none`", "The FALLBACK flow never executed" | **not met**: "Final status: "Review" … Status front matter field changed from "InProgress" to "Review"" | 1/5 |
| h5 | met: "VALID" / "outcome t1.accepted" | **not met**: no staleness check; the transition goes straight through | **not met (DANGER)**: "3. TRANSITION t1 "Review" -> status t1 = "Review"" | **not met**: "Process state: `none`" | **not met**: "Status field: changed from `InProgress` to `Review`" | 1/5 |

Errors:
- **h4, h5 — DANGER** (one root error; D2, D4 and D5 fail as consequences). Both probes performed the entity transition after the verification had gone stale. TASK-0100's status and its file were changed when they must not be. Cause: **model-error**. DSL.md › Entities › Preconditions, row `verified: accepted`, is explicit: "… **and** the entity's data has not changed since that `VERIFY` (other than by `TRANSITION <name>`)". ENTITY.md › TRANSITION repeats it: "After any other change, the entity must be verified again." Contributing factor: h4 confused "delegated work is *permitted* to edit Description while InProgress" (Task Definition › Permitted changes by delegated work) with "the precondition still holds" ("permitted change during InProgress status before transition").
- Minor, not scored: h5's trace omits the binding line (formatting only). h4's evidence repeats "both criteria satisfied" for each item, which is weak per-criterion evidence.

Divergence: Sonnet none. Haiku material (h1–h3: InProgress / Reverify; h4–h5: Review / none).

**PASS-S: YES (10/10). PASS-H: NO (17/25).**

---

## N07 — Execution: human approval about something else

Expected: `merge.approved`. `TRANSITION t1 "Done"` fails because the question does not contain TASK-0101. There is no FALLBACK, so execution ends and `EMIT summary` does not run. TASK-0101 stays Review with no file changes, and the process state is `none`.

| Probe | D1 | D2 | D3 | D4 | Met |
|---|---|---|---|---|---|
| s1 | met: "outcome merge.approved (human)" | met: "failed: precondition "human: approved" not met (the question … does not contain t1's identity TASK-0101 …); stop" | met: "`EMIT summary` is never reached" | met: "Final status of `TASK-0101`: `Review` … No entity file changed … Final process state: `none`" | 4/4 |
| s2 | met: "outcome merge.approved (human)" | met: "does **not** contain `TASK-0101` — does **not** hold" | met: "`EMIT summary` is never reached and does not run" | met: "Final status: `Review` … Files changed: none … `none`" | 4/4 |
| h1 | met: "outcome merge.approved (human)" | met: "failed: precondition `human: approved` not satisfied (HITL question does not contain entity identity); stop" | met: "The `EMIT summary` statement was never reached" | met: "Review (unchanged) … None … none" | 4/4 |
| h2 | met: "outcome merge.approved (human)" | met: "Condition 3 fails … does not contain the entity's identity "TASK-0101"" | met: the trace ends at "…; stop", and "execution stopped immediately" | met: "remains in status `Review` … None … `none`" | 4/4 |
| h3 | met: "outcome merge.approved (human)" | met: "the question "Merge the documentation branch?" does not mention TASK-0101" | met: the trace ends at "5. TRANSITION t1 "Done" -> failed: precondition not satisfied; stop" | met: "`Review` (unchanged) … Files Changed: None … `none`" | 4/4 |
| h4 | met: "outcome merge.approved (human)" | met: "which does not contain `TASK-0101`. Therefore the precondition does not hold" | met: "the transition fails, and execution ends" (no EMIT in the trace) | met: "`Review` (unchanged) … None … `none`" | 4/4 |
| h5 | met: "outcome merge.approved (human)" | met: "✗ (question … does not contain "TASK-0101")" | met: "since there is no FALLBACK, execution ends with `stop`" | met: "`Review` (unchanged) … None … `none`" | 4/4 |

Errors: none. Divergence: none.

**PASS-S: YES (8/8). PASS-H: YES (20/20).**

---

## N08 — Execution: nested loops with a WHEN at the end of each body

I verified the trace myself. Outer iteration 1: batch, item (rejected), inner loop again, item (accepted), BREAK, batch rejected, WHEN accepted false, WHEN rejected true, state Retry, outer loop again. Outer iteration 2: batch, item (accepted), BREAK, batch accepted, BREAK. Then EMIT report and end. That gives batch ×2 and item ×3, with final state Retry.

All seven probes produce the same 24-line trace, and it matches this derivation.

| Probe | D1 | D2 | D3 | D4 | D5 | Met |
|---|---|---|---|---|---|---|
| s1 | met: "VALID." | met: "4. WHEN item.accepted -> false: skip / 5. LOOP:inner -> loop again" | met: "12. WHEN batch.rejected -> true … 14. LOOP:outer -> loop again" | met: "batch runs **2** times … item runs **3** times", "23. EMIT report -> done" | met: "`"Retry"`" | 5/5 |
| s2 | met | met (same lines 4–5) | met: "the `WHEN batch.rejected` is the last statement of the outer loop body, so the loop restarts" | met: "2 times … 3 times", line 23 | met: "Final process state: `Retry`" | 5/5 |
| h1 | met | met (lines 4–5) | met (lines 12–14) | met: "**2 times** … **3 times**", "23. EMIT report -> done" | met: "**"Retry"**" | 5/5 |
| h2 | met | met | met | met: "(steps 1 and 15) … (steps 2, 6, and 16)" | met | 5/5 |
| h3 | met | met | met | met: "runs **2 times** … runs **3 times**" | met: "Final Process State: "Retry"" (after a visible self-correction) | 5/5 |
| h4 | met | met | met | met: "2 executions … 3 executions" | met | 5/5 |
| h5 | met | met | met | met | met: "`"Retry"`" | 5/5 |

Errors: none scored. Minor: h1's V8 note ("BREAK correctly ends the inner WHEN flow") is a wrong justification for a rule that does not apply. It has no effect.

Divergence: none.

**PASS-S: YES (10/10). PASS-H: YES (25/25).**

---

## N09 — Authoring: ADR decision with entities

Linter (lint.txt, confirmed with dslcheck): all seven are VALID.

| Probe | D1 | D2 | D3 | D4 | D5 | D6 | Met |
|---|---|---|---|---|---|---|---|
| s1 | met (VALID) | met: "a1:ADR = ADR-0101" / "VERIFY a1" before HITL | met: "HITL:decision[approved, rejected]("Accept ADR-0101?")", no AUTO | met: `[approved, rejected]` | met: "→ TRANSITION "Waiting"" / "→ STOP" | met: "WHEN decision.approved → TRANSITION a1 "Accepted"", "WHEN decision.rejected → TRANSITION a1 "Rejected"" | 6/6 |
| s2 | met | met | met: "Accept ADR-0101?" | met | met | met | 6/6 |
| h1 | met | met: "adr:ADR = ADR-0101" / "VERIFY adr" | met: "Accept ADR-0101?" | met | met | met: "→ TRANSITION adr "Accepted"" / "→ TRANSITION adr "Rejected"" | 6/6 |
| h2 | met | met | met: "Should ADR-0101 be accepted?" | met | met | met | 6/6 |
| h3 | met | met | met: "Accept ADR-0101?" | met | met | met | 6/6 |
| h4 | met | met | met: "Do you accept ADR-0101?" | met | met | met (the extra `→ FALLBACK → STOP` under Accepted behaves the same as no fallback) | 6/6 |
| h5 | met | met | met: "Accept ADR-0101?" | met | met | met | 6/6 |

Errors (no D-item fails because of these):
- **h5 — OTHER** (unrequested behaviour). h5 adds `VERIFY a1 → FALLBACK → TRANSITION "Waiting" → STOP` and the same `Waiting` fallback under both entity TRANSITIONs. The requirement assigns `Waiting` only to "no usable answer" from the human. For the same events (for example VERIFY undecidable, or VERIFY rejected followed by a human `approved`), h5 ends in process state `Waiting` while h1–h4 end in `none`. Cause: **underspecified**. DSL.md does not say whether an author may add FALLBACK flows the requirement does not ask for. Execution rule 9 ("MUST NOT invent … a requirement") speaks to execution, not authoring.
- Sonnet s1 also adds `→ FALLBACK → STOP` under both entity TRANSITIONs. This behaves the same as having no fallback (execution ends either way), so it is not material.

Divergence: Sonnet none. **Haiku: material (h5 vs h1–h4, final process state on unspecified failure paths).** Every D-item is met. PASS-H fails only because of this divergence. See Scenario issues.

**PASS-S: YES (12/12). PASS-H: NO (30/30 D-items; divergence).**

---

## N10 — Interpretation: validity of tricky snippets

Ground truth, checked with dslcheck: A INVALID V1 (`BREAK release`). B VALID. C INVALID V10. D VALID. E INVALID V12.

| Probe | D1 (A: V1) | D2 (B VALID) | D3 (C: V10) | D4 (D VALID) | D5 (E: V12) | Met |
|---|---|---|---|---|---|---|
| s1 | met: "**Broken rule:** V1 (line 5)" | met: "VALID … the `LOOP` is itself nested inside the same `FORK` branch" | met: "**Broken rule:** V10 (line 4)" | met: "VALID" | met: "**Broken rule:** V12 (line 4)" | 5/5 |
| s2 | met: "INVALID — V1" | met: "VALID" | met: "INVALID — V10" | met: "VALID" | met: "INVALID — V12" | 5/5 |
| h1 | met: "Breaks: **V1**" | met: "VALID" | met: "Breaks: **V10**" | met: "VALID" | met: "Breaks: **V12**" | 5/5 |
| h2 | met | met | met | met | met | 5/5 |
| h3 | met | met | met | met | met | 5/5 |
| h4 | met: "V1 (line 5)" | met | met: "V10 (line 4)" | met | met: "V12 (line 5)" (wrong line number, correct rule) | 5/5 |
| h5 | met | met | met: "**V10**" (the rule is garbled as "no `JOIN` … must exist", but the verdict and rule are correct) | met | met | 5/5 |

No probe lists an extra rule. None of them names the reason in D4 ("a HITL name may equal an EMIT argument"), but all give the correct verdict of VALID, which is what the item scores.

Errors: none scored. Minor: h4 cites the wrong line for E. h5 paraphrases V10 incorrectly.

Divergence: none.

**PASS-S: YES (10/10). PASS-H: YES (25/25).**

---

## S01 — Authoring: auto-resolvable merge decision (DSL only; Sonnet s1 only)

Linter: all six are VALID (lint.txt, confirmed).

| Probe | D1 | D2 | D3 | D4 | D5 | Met |
|---|---|---|---|---|---|---|
| s1 | met (VALID) | met: "DELEGATE implementation / VERIFY implementation" | met: "AUTO HITL:merge[merge, no-merge]("Merge this change?")" | met: "WHEN merge.merge → TRANSITION "Merged"", "WHEN merge.no-merge → TRANSITION "Rework"" | met: no uncertainty condition, no flow under AUTO | 5/5 |
| h1 | met | met | met: "AUTO HITL:merge[approved, declined]("Merge this change?")" | met | met | 5/5 |
| h2 | met | met | met: `[approved, declined]` | met | met | 5/5 |
| h3 | met | met | met | met | met | 5/5 |
| h4 | met | met | met: `[approved, rejected]` | met: "WHEN merge.rejected → TRANSITION "Rework"" | met | 5/5 |
| h5 | met | met | met | met | met: the `→ FALLBACK` is under the HITL, not a flow inside AUTO, and there is no uncertainty WHEN | 5/5 |

Errors (no D-item fails because of this):
- **h5 — OTHER** (unrequested behaviour). h5 adds `→ FALLBACK → TRANSITION "Blocked" → STOP`, and the probe itself says "(not specified in the requirement)". On an insufficient or unavailable human answer, h5 ends in state `Blocked` while h1–h4 end in `none`. Cause: **underspecified**, the same authoring gap as N09-h5.
- The different answer labels (`declined` / `rejected` / `no-merge`) are naming only and not material.

Divergence: Sonnet not applicable (single probe). **Haiku: material (h5 vs h1–h4 on the insufficient-answer path).** Every D-item is met.

**PASS-S: YES (s1 passes, 5/5). PASS-H: NO (25/25 D-items; divergence).**

---

## NEW issues

1. **Stale `verified: accepted` is still missed by Haiku (N06, 2 of 5).** The rule is stated clearly in DSL.md › Preconditions and in ENTITY.md, but it is only in the table row. The Task Definition's "Permitted changes by delegated work" section invites the reading "permitted edit, so the verification is still valid". Suggestion: add one sentence under **Entities › Preconditions**, or to the Task Definition: "A permitted data change still invalidates an earlier `verified:` outcome." Also consider a worked N06-style example in the Failures section.
2. **Authoring: unrequested FALLBACK flows (N09-h5, S01-h5).** The spec has no rule saying an author MUST NOT add fallback flows, or new process states, that the requirement does not ask for. This produces divergent programs. Suggestion: add an authoring rule: "Write only what the requirement states; do not add a FALLBACK or process state the requirement does not name. An unhandled failure ends execution."

## Scenario issues

- N09 and S01: all D-items are met in all Haiku probes. PASS-H = NO rests only on my judgment that h5's added fallbacks are a *material* divergence (a different final process state for the same events on paths the requirement leaves unspecified). If the lab treats divergence on unspecified failure paths as non-material, both flip to PASS-H = YES, and pass_h becomes 5/6.
- N10 D4's parenthetical reason is not independently checkable. I scored the verdict only.

---

| ID | PASS-S | PASS-H | sonnet D met | haiku D met | tags | top spec section |
|---|---|---|---|---|---|---|
| N06 | YES | NO | 10/10 | 17/25 | DANGER×2 (h4, h5) | DSL.md › Entities › Preconditions (`verified: accepted` row) |
| N07 | YES | YES | 8/8 | 20/20 | — | DSL.md › Entities › Preconditions (`human:` row) |
| N08 | YES | YES | 10/10 | 25/25 | — | DSL.md › WHEN / Execution rules 2, 5 |
| N09 | YES | NO | 12/12 | 30/30 | OTHER (h5, divergence) | DSL.md › FALLBACK / Execution rule 9 (authoring gap) |
| N10 | YES | YES | 10/10 | 25/25 | — | DSL.md › Validity rules |
| S01 | YES | NO | 5/5 | 25/25 | OTHER (h5, divergence) | DSL.md › FALLBACK / AUTO (authoring gap) |

```
PART SUMMARY
scenarios: 6
pass_s: 6/6   pass_h: 3/6
d_items_s: 55/55   d_items_h: 142/150
danger_s: 0   danger_h: 2
```
