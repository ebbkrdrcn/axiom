# Critic part D — iteration 02 (S16–S21)

Spec: `dsl-lab/iterations/02/DSL.md`. The linter (`lint.txt`) is used only for S17 D1, the one D-item that says "Linter VALID". Quoted INVALID blocks in S19 are the task program the probe quotes. They are not programs the probe wrote.

---

## S16 — Execution: test loop (baseline)

D-items: D1 iteration 1 (accepted-WHEN skipped; Debugging; DELEGATE diagnosis; loop again). D2 iteration 2 (Review; BREAK; rejected-WHEN not evaluated). D3 EMIT source-code once; final state "Review".

| Probe | D1 | D2 | D3 |
|---|---|---|---|
| s1 | met: "4. WHEN tests.accepted -> false: skip … 6. TRANSITION \"Debugging\" … 7. DELEGATE diagnosis -> done 8. LOOP:tdd -> loop again" | met: "14. BREAK -> break … `WHEN tests.rejected` … is **not** evaluated at all" | met: "15. EMIT source-code -> done", "Final state **`Review`**" |
| s2 | met: identical trace steps 4–8 | met: "the second `WHEN tests.rejected` — is **not executed at all** (not even evaluated/skipped)" | met: step 15 once; "Final state `Review`" |
| s3 | met: identical trace steps 4–8 | met: "In iteration 2, `WHEN tests.rejected` is never evaluated" | met: step 15 once; "`Review`" |
| h1 | met: trace steps 4–8 | met: "13. TRANSITION \"Review\" … 14. BREAK -> break 15. EMIT source-code" (no rejected-WHEN line); "The remaining statements in the loop body are not executed" | met: "Final State `Review`" |
| h2 | met: trace steps 4–8 | met: trace goes 14 BREAK → 15 EMIT with no rejected-WHEN line | met: "Final State \"Review\"" |
| h3 | met: trace steps 4–8 | met: "`BREAK` exits the loop immediately", no rejected-WHEN line | met: "**State: `\"Review\"`**" |

Divergence: sonnet none. Haiku none (all six traces are the same, line for line).

Errors (these do not affect the D-items):
- h1: "set by the most recent (and only executed) TRANSITION statement". That is wrong, because `TRANSITION "Debugging"` also ran (step 6). Tag `OTHER`. Spec: TRANSITION, "Each `TRANSITION` replaces it; the most recently executed one wins." Classification: model-error. h3 makes a similar but qualified claim, "(and only) … after the second loop iteration", which is loose wording and not an error.

Verdict: **PASS-S yes. PASS-H yes.**

New issues: all three sonnet probes note that the trace convention for first entry into a `LOOP` (no line for it, only `LOOP:<name> -> loop again` on a repeat) appears only in the Complete example and is not stated as a rule. This is a spec-gap in "Executing a program" (trace format). No probe diverged over it.

---

## S17 — Authoring: pass/fail wording

D-items: D1 Linter VALID. D2 DELEGATE x then VERIFY x (same identifier). D3 `WHEN x.accepted → TRANSITION "Review"`; `WHEN x.rejected → TRANSITION "Debugging"` then `DELEGATE diagnosis`; no passed/failed.

| Probe | D1 | D2 | D3 |
|---|---|---|---|
| s1 | met: lint "S17-s1.md block1: VALID" | met: "DELEGATE test-suite / VERIFY test-suite" | met: accepted→Review; rejected→"Debugging" then diagnosis |
| s2 | met: VALID | met: "DELEGATE tests / VERIFY tests" | met |
| s3 | met: VALID | met: "DELEGATE tests / VERIFY tests" | met |
| h1 | met: VALID | met: `test-suite` | met |
| h2 | met: VALID | met: `test-suite` | met |
| h3 | met: VALID | met: `tests` | met |

Divergence: the identifier is `test-suite` in some probes and `tests` in others (s1/h1/h2 vs s2/s3/h3). This is not material. Otherwise sonnet and haiku have no divergence.

Errors (these do not affect the D-items):
- s1, assumption 1: "The spec requires `DELEGATE` and `VERIFY` to name the same subject for `VERIFY`'s outcome to attach to the thing delegated". The spec states no such rule. Tag `INVENT`, meaning a rule is invented, which is harmless here. Spec: DELEGATE and VERIFY sections contain no binding rule. Classification: spec-gap, because s2 explicitly notes "The spec does not state a rule binding a `VERIFY`'s argument to a preceding `DELEGATE`'s argument by name".
- h3, assumption 5: "execution would continue if there were further statements" is framed as an assumption. It is confused but harmless. Tag `OTHER`, model-error.

Verdict: **PASS-S yes. PASS-H yes.**

New issues: the spec never states that `VERIFY x` evaluates the result of `DELEGATE x`, meaning that the identifiers link them. The link appears only in examples. Spec-gap in DELEGATE/VERIFY.

---

## S18 — Execution: FORK without JOIN; DELEGATE completion

D-items: D1 (Q1) No: a DELEGATE is done only when the actor delivers. D2 (Q2) immediately after the FORK starts its branches (no JOIN), while they run. D3 (Q3) No.

| Probe | D1 | D2 | D3 |
|---|---|---|---|
| s1 | met: "**No.** … `DELEGATE design` is done only when the design actor has delivered its result" | met: "`EMIT release` runs immediately after `FORK` starts the branches — it does not wait" | met: "**No, it is not guaranteed.**" |
| s2 | met: "**No.** … means the design actor has delivered its result" | met: "Immediately after the `FORK` starts the branches" | met: "**No — it is not guaranteed**" |
| s3 | met: "**No.** … until the design actor has delivered its result" | met: "runs immediately after `FORK` starts the two branches, concurrently with them" | met: "**No — it is not guaranteed**" |
| h1 | met: "**NO** … the actor must deliver the result" | met: "Immediately after the FORK starts, while both branches are still running concurrently" | met: "**NO**" |
| h2 | met: "cannot start until `DELEGATE design` delivers its result" | met: "executes immediately after the `FORK` starts the concurrent branches, while the branches are still running" | met: "**No. It is not guaranteed.**" |
| h3 | met: "Wait for the design actor to deliver the result" | met: "executed immediately after the `FORK` starts" | met: "**No**" |

Divergence: s1 says docs will "in practice" not exist, while s2 and s3 say that given the timings docs "will definitely not yet exist". All three answer "not guaranteed", so this is not material. Haiku has no divergence.

Errors: none.

Verdict: **PASS-S yes. PASS-H yes.**

New issues: none. Note that h1, h2 and h3 justify Q1 through Execution rule 1 and not through the DELEGATE section's "done when the actor has delivered its result". The conclusion is the same.

---

## S19 — Execution: FALLBACK flow that does not stop

D-items: D1 INVALID (V8). D2 nothing executed; agent reports V8.

| Probe | D1 | D2 |
|---|---|---|
| s1 | met: "**The program is INVALID — it breaks rule V8.**" | met: "Program rejected as a whole. No statement is executed." |
| s2 | met: "**Broken rule: V8**" | met: "no statement in the program is ever run" |
| s3 | met: "**Result: the program is INVALID — it violates V8.**" | met: "No statement in the program runs"; "Reported broken rule – **V8**" |
| h1 | met: "**INVALID** … Violation: Rule V8" | met: "No statements are executed, including `TRANSITION \"Deploying\"`" |
| h2 | met: "**The program is INVALID.** It violates **Rule V8**." | met: "Execution never begins." |
| h3 | met: "**V8**: The last item of the fallback flow is not `STOP` or `BREAK`." | met: "**No execution occurs.**" |

Divergence: sonnet none. Haiku none. h1 and h3 add a hypothetical corrected program; that is extra, not a divergence.

Errors: none.

Verdict: **PASS-S yes. PASS-H yes.**

New issues: all three sonnet probes independently flag that the HITL "unavailable" classification ("No response, and the runtime has stopped waiting") has no stated condition for when the runtime stops waiting. `WAIT` explicitly has "no timeout", but `HITL` says nothing either way. This is a spec-gap in HITL, in the "Usable, insufficient, unavailable" table. It did not affect this scenario.

---

## S20 — Interpretation: BREAK in nested loops

D-items: D1 only `LOOP:fix`; next `TRANSITION "Fixed"`. D2 No: BREAK takes no name; the loop name is only a label. D3 WHEN skipped; the body of `LOOP:release` restarts with `LOOP:fix` (`DELEGATE fix`).

| Probe | D1 | D2 | D3 |
|---|---|---|---|
| s1 | met: "The innermost loop enclosing this `BREAK` is `LOOP:fix` … `TRANSITION \"Fixed\"`" | met: "`<name>` is only a label. No statement refers to it; `BREAK` takes no name." | met: "`LOOP:release` starts its body again from the top — i.e., `LOOP:fix` (and within it, `DELEGATE fix`)" |
| s2 | met: "exits **`LOOP:fix`** … continues with `TRANSITION \"Fixed\"`" | met: "No. … explicitly documented to take no name" | met: "the next thing to execute is `LOOP:fix`'s first statement again, i.e. `DELEGATE fix`" |
| s3 | met: "The `BREAK` exits `LOOP:fix` only … `TRANSITION \"Fixed\"`" | met: "No. … `BREAK` takes no name" | met: "back to `LOOP:release`'s first statement, `LOOP:fix` (which begins again with `DELEGATE fix`)" |
| h1 | met: "exits the **`LOOP:fix`** … next … **`TRANSITION \"Fixed\"`**" | met: "No … `BREAK` takes no name" | met: "loops back to the beginning of `LOOP:release` … starts with `LOOP:fix`" |
| h2 | met: "exits **`LOOP:fix`** … next … **`TRANSITION \"Fixed\"`**" | met: "No … `BREAK` takes no name" | **not met**: "**Answer:** **`EMIT release`** executes next. … The next statement is `EMIT release`, which executes" |
| h3 | met: "exits the **innermost loop, `LOOP:fix`** … Next statement: `TRANSITION \"Fixed\"`" | met: "No … `BREAK` takes no name" | met: "loops back to the start of `LOOP:release` and executes `LOOP:fix` again" |

Divergence: sonnet none. The Q2 workarounds differ (outer `WHEN fix.accepted → BREAK`, or `STOP`), but these are extras. **Haiku: material divergence on Q3.** h1 and h3 have the loop restart, and h2 has `EMIT release` running next.

Errors:
- h2, Q3: after the false `WHEN release-candidate.accepted`, which is the last statement of `LOOP:release`'s body, h2 continues to the next line of text, `EMIT release`. That line is outside the loop, so h2 treats the end of the body as leaving the loop. Tag `SCOPE`. Spec: Execution in ten rules, rule 5: "At the end of a loop body, the body starts again from its first statement."; LOOP table: "The last statement of the body is done | The next iteration starts at the first statement of the body."; LOOP: "only `BREAK` or `STOP` ends it" (Quick reference). Classification: model-error. A possible contributor is the WHEN wording "Skip the flow and continue after the `WHEN`" (rule 2: "False → skip it" / "continue after the `WHEN`"), which h2 quotes and reads as "the next line in the text" and not as "the next statement in the same scope". This wording does not override the LOOP rules, which are explicit.
- h1: cites "BREAK section (line 88)" for "`<name>` is only a label". The quote is actually in the LOOP section. This is a wrong citation, not a wrong rule. Tag `OTHER`, model-error, and it has no effect.

Verdict: **PASS-S yes. PASS-H no** (h2 D3 not met, and the haiku divergence).

New issues: s1, s2 and s3 note that `BREAK release` breaks the grammar (`( "JOIN" | "BREAK" | "WAIT" | "STOP" ) , NL`), but no validity rule V1–V10 covers a line that does not match any grammar production. "Validate first … Report each broken rule by its number" therefore has no number to report for a malformed statement. This is a spec-gap in the Validity rules and in "Executing a program", step 1.

---

## S21 — Execution: WHEN evaluated before its outcome exists

D-items: D1 program VALID. D2 WHEN checked once before VERIFY (no outcome → false), never re-checked; "Review" never executed. D3 EMIT test-report runs; final state "Testing".

| Probe | D1 | D2 | D3 |
|---|---|---|---|
| s1 | met: "The program is **valid** and may be executed." | met: "2. WHEN tests.accepted -> false: skip"; "never re-checked"; "**No.**" | met: "5. EMIT test-report -> done"; "**Final state: `\"Testing\"`**" |
| s2 | met: "**The program is valid** and may be executed." | met: step 2 false: skip; "is explicitly 'not a standing trigger'"; "**No.**" | met: step 5; "Final state `Testing`" |
| s3 | met: "The program is well-formed. It may be executed." | met: step 2 false: skip; "it is *never* revisited"; "**No.**" | met: step 5; "`Testing`" |
| h1 | **not met**: no validity statement. The probe goes straight to "Step-by-step Execution" | met: "2. `WHEN tests.accepted` → false: skip"; "the `WHEN` is not re-evaluated"; "**No.**" | met: "5. `EMIT test-report` → done"; "**\"Testing\"**" |
| h2 | **not met**: no validity statement; the analysis has only a trace and a "Why" section | met: "Step 2 … `false: skip`"; "never re-checked"; "**No.**" | met: step 5 done; "Final State \"Testing\"" |
| h3 | met: "The program is valid (all rules V1–V10 satisfied)." | met: step 2 false: skip; "The `WHEN` is never re-checked later"; "**No.**" | met: step 5; "`\"Testing\"`" |

Divergence: sonnet none. **Haiku: material divergence on the validation step.** h3 validates and states VALID, while h1 and h2 skip validation entirely. The execution result is the same in all three.

Errors:
- h1 and h2: validation is skipped and validity is never stated, although the program is executed. Tag `OTHER`. Spec: Executing a program, step 1: "**Validate first.** Check rules V1–V10. If any is broken, do not execute." Classification: model-error. Because the program is in fact valid, the execution result is unaffected.
- h1: attributes "The outcome is established later. Nothing happens. A `WHEN` is not a standing trigger…" to the "Outcomes section". The quote is from the WHEN table. This is a wrong citation. Tag `OTHER`, model-error, and it has no effect.

Verdict: **PASS-S yes. PASS-H no** (h1 and h2 D1 not met).

Scenario issues: the S21 task asks only for "the step-by-step execution and the final state" and does not ask for a validity verdict, so D1 is graded strictly as "states VALID". h1 and h2 treat the program as valid by executing it, but never say so. If the scenario author meant D1 to be implied, it should say so. Otherwise, the task text should ask for validation explicitly. Under a lenient reading, S21 would be PASS-H, and haiku would have 50/51 D-items.

---

## Summary table

| ID | PASS-S | PASS-H | sonnet D met | haiku D met | tags | top spec section |
|---|---|---|---|---|---|---|
| S16 | yes | yes | 9/9 | 9/9 | OTHER (h1, not a D-item) | BREAK ("remaining statements … not executed, including later `WHEN`s") |
| S17 | yes | yes | 9/9 | 9/9 | INVENT (s1 assumption, not a D-item), OTHER (h3, not a D-item) | VERIFY / V6 (only `accepted`/`rejected`) |
| S18 | yes | yes | 9/9 | 9/9 | — | FORK ("No `JOIN` follows → continue immediately"); DELEGATE |
| S19 | yes | yes | 6/6 | 6/6 | — | FALLBACK / V8; Validity rules ("rejected as a whole") |
| S20 | yes | no | 9/9 | 8/9 | SCOPE (h2), OTHER (h1 citation) | Execution rule 5 / LOOP table (loop body restarts) |
| S21 | yes | no | 9/9 | 7/9 | OTHER (h1, h2 skipped validation; h1 citation) | Executing a program, step 1 ("Validate first") |

```
PART SUMMARY
scenarios: 6
pass_s: 6/6   pass_h: 4/6
d_items_s: 51/51   d_items_h: 48/51
danger_s: 0   danger_h: 0
```
