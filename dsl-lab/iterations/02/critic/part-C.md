# Critic part C (iteration 02): S11 to S15

Spec: `dsl-lab/iterations/02/DSL.md`. Linter: `dsl-lab/iterations/02/lint.txt`. None of the D-items in S11 to S15 is a "Linter VALID" item. The linter's INVALID entries for S11 are the probes quoting the task program. The corrected programs the probes suggest are all VALID (S11-h1 b2, S11-h3 b1, S11-s1 b2, S11-s2 b2). These are informational only.

---

## S11: BREAK inside FORK inside LOOP

| Probe | D1 INVALID (V3) | D2 nothing executed, V3 reported |
|---|---|---|
| s1 | met: "**Broken rule: V3** … the `LOOP` it would leave (`LOOP:review`) is outside that branch" | met: "no step-by-step execution trace can be produced for this program" |
| s2 | met: "**Result: the program is INVALID.** ### Broken rule: V3" | met: "the agent MUST NOT execute it, not even in part … The injected events … are never reached" |
| s3 | met: "The program is **INVALID** — broken rule: **V3**." | met: "an INVALID program **MUST NOT be executed** … No step-by-step trace can therefore be produced" |
| h1 | met: "**This program is INVALID and cannot be executed.** ### Violation Detected: Rule V3" | met: "execution MUST NOT proceed. The program must be rejected as a whole." |
| h2 | met: "**The program is INVALID.** It violates validity rule V3" | met: "No execution trace can be produced for an INVALID program." |
| h3 | met: "The program is **INVALID** according to rule **V3**." | met: "**the program MUST NOT be executed**. No step-by-step trace can be produced." |

Divergence. Sonnet: none. Haiku: none. The suggested fixes differ slightly: s2 puts `WHEN … → BREAK` after `TRANSITION "Reviewed"`, and the other probes put it before. That is outside the task and is not material.

Errors: none.

Verdict: **PASS-S yes, PASS-H yes.**

---

## S12: decision HITL with FALLBACK, four runs

| Probe | D1 A → Published | D2 B → Blocked, STOP | D3 C → Blocked | D4 D → notes.rejected → Rework |
|---|---|---|---|---|
| s1 | met: "WHEN notes.rejected -> false: skip … **Final state: `Published`**" | met: "fallback / TRANSITION "Blocked" / STOP -> stop"; "the two `WHEN` statements are never reached" | met: "insufficient … **Final state: `Blocked`**" | met: "usable, establishing `notes.rejected` … **Final state: `Rework`**" (with a hedge; see note) |
| s2 | met: "Final state: `Published`" | met: "both `WHEN` statements are never reached — `STOP` ends execution first" | met: "insufficient … `Blocked`" | met: "usable → `notes.rejected` … Fallback run? no … `Rework`" |
| s3 | met: "Final state: `Published`" | met: "Neither `WHEN notes.approved` nor `WHEN notes.rejected` ever runs or is even reached" | met: "insufficient … `Blocked`" | met: "a **usable** response selecting `rejected` … `Rework`" |
| h1 | met: "Final state: `Published`" | met: trace ends "5. STOP -> stop"; "Final state: `Blocked`" | met: "classified as **insufficient** … `Blocked`" | **not met**: "classified as **insufficient**. The `FALLBACK` flow executes … **Final state:** `Blocked`" |
| h2 | met: "Final state: `Published`" | met: "Neither `WHEN` statement runs because `STOP` ends execution immediately." | met: "`Blocked`" | **not met**: "Insufficient (ambiguous) \| Blocked" |
| h3 | met: "Final state: `Published`" | met, with a flaw: the trace adds "6. (end of program) -> end" after "5. STOP -> stop" | met, with the same flaw: "6. (end of program) -> end" | **not met**: "classified as insufficient. The `HITL` has a `FALLBACK`, so the fallback flow runs … `Blocked`" |

Divergence. Sonnet: none. All three choose usable, `rejected` and `Rework`. s1 and s2 flag the insufficient reading as an alternative, but neither adopts it. Haiku: none. All three are consistent, and all three are wrong on Run D. Their reasons differ: "off-topic" (h1, h3) and "ambiguous" (h2).

Errors:
1. **h1, h2, h3, Run D. Tag `SEMANTIC`.** They classify "Not like this, rewrite the intro." as insufficient, run the FALLBACK and end in `Blocked` instead of `Rework`. h2 also argues "it does not explicitly say 'rejected'".
   - Spec: HITL › Usable, insufficient, unavailable: "Clearly selects exactly one listed answer (in any wording) | usable". The spec also says: "Selects none of the listed answers, is ambiguous between answers, or is off-topic (for example "I haven't looked yet") | insufficient".
   - Classification: **spec-gap**. The spec gives an example only for insufficient ("I haven't looked yet"). It gives none for a paraphrased answer that carries extra feedback. All three sonnet probes independently note that the spec "does not explicitly resolve how to treat a rejection that is bundled with additional free-text feedback". h2's "does not explicitly say 'rejected'" contradicts "in any wording" outright, so it is partly a model error.
   - This is not DANGER. The fallback is over-applied, not skipped, and the agent does not make the decision itself.
2. **h3, Runs B and C. Tag `SEMANTIC`, minor, not a D-item failure.** The trace adds "(end of program) -> end" after "STOP -> stop".
   - Spec: STOP: "Ends the entire execution immediately." Rule 10 says normal end happens only "When the last top-level statement is done". The Executing a program effect list gives `stop` and `end` as separate effects.
   - Classification: **model-error**.

Verdict: **PASS-S yes, PASS-H no.** D4 fails in 3 of 3 haiku probes.

---

## S13: AUTO uncertain

| Probe | D1 VALID | D2 uncertain → human asked | D3 Declined → Deferred |
|---|---|---|---|
| s1 | met: "**Yes, the program is valid.**" | met: "`AUTO` **cannot** resolve `HITL:merge` automatically … Execution therefore waits at the `HITL` for a human response." | met: "outcome merge.declined … **Final state: `Deferred`.**" |
| s2 | met: "The program is **valid**." | met: "the agent **cannot reliably determine** the single correct answer … the human is asked" | met: "**Final state:** `Deferred`" |
| s3 | met: "the program is **VALID**." | met: "this is not a case the agent may resolve under `AUTO` … the human must be asked" | met: "**`Deferred`**" |
| h1 | met: "The program is **VALID**." | met: "Since the decision is uncertain, the human is asked (not answered automatically)." | met: "**Process state:** `"Deferred"`" |
| h2 | met: "**Yes, the program is valid.**" | met: "**the agent cannot answer automatically**. The human is asked." | met: "**"Deferred"**" |
| h3 | met: "**Answer: YES, the program is valid.**" | met: "Uncertainty exists. Therefore, the human is asked." | met: "**Final state: `Deferred`**" |

Divergence. Sonnet: none. Haiku: none. h3 numbers the trace irregularly: step 3 appears twice, and the steps are split across two blocks. That is a cosmetic issue, not a material one.

Errors:
1. **h3. Tag `OTHER`, cosmetic.** It cites "Per the `AUTO` specification (Semantic Principles)" for the certainty rule. That rule is in the AUTO section, not in Semantic Principles. Its trace numbering also repeats "3.".
   - Spec: Executing a program: "write one line per executed step: `<n>. <statement as written> -> <effect>`".
   - Classification: **model-error**. This is not a D-item failure.

Verdict: **PASS-S yes, PASS-H yes.**

---

## S14: FORK branch rejected; two WHENs match

| Probe | D1 concurrent, DELEGATE→VERIFY, rejected branch completes, JOIN waits for both | D2 both WHENs run in order: Ready, then Debugging | D3 final Debugging |
|---|---|---|---|
| s1 | met: "`FORK` starts both branches concurrently"; "a rejected outcome does not abort … the branch"; "`JOIN` … actually waits on it" | met: steps 7 to 10, "Ready" then "Debugging" | met: "**`Debugging`**" |
| s2 | met: "starts both branches concurrently"; "The branch continues normally"; "`JOIN` waits until *every* branch … is complete" | met: steps 7 to 10 | met: "**`Debugging`**" |
| s3 | met: "`FORK` branches run concurrently"; "`JOIN` only requires that both branches be complete" | met: "both flows run, top to bottom, in the order written" | met: "**`Debugging`**" |
| h1 | met: "FORK starts both branches concurrently"; "5. JOIN -> waiting … 7. JOIN -> joined"; "All branches are now complete" | met: steps 8 to 11 | met: "**State: "Debugging"**" |
| h2 | met: "Both branches … start concurrently"; "Branch 2 completes … establishes … rejected"; "`JOIN` waits for all branches to complete" | met: steps 7 to 10 | met: "`Debugging`" |
| h3 | met: "two concurrent branches"; "both branches eventually complete. The JOIN waits for both to finish" | met: steps 7 to 10 | met: "**Debugging**" |

Divergence. Sonnet: none. Haiku: h1 adds an explicit `JOIN -> waiting` line, which h2 and h3 omit. Both forms are allowed effects, so this is not material.

Errors: none.

Verdict: **PASS-S yes, PASS-H yes.**

---

## S15: STOP inside a FORK branch

| Probe | D1 STOP ends everything, including the docs branch | D2 EMIT docs no; JOIN never completes; EMIT build no |
|---|---|---|
| s1 | met: "the docs branch is aborted exactly where the events said it was" | met: "**Is `EMIT docs` executed?** No … **Is `JOIN` completed?** No … **Is `EMIT build` executed?** No." |
| s2 | met: "ends the entire execution immediately, including the still-running docs branch" | met: No / No / No |
| s3 | met: "no statement anywhere, including `EMIT docs` in the still-running docs branch, is allowed to run" | met: No / No ("never reached/never completed") / No |
| h1 | met: "STOP terminates the entire execution immediately, including all running branches." | met: **No** / **No** / **No** |
| h2 | met: "The `STOP` statement (step 6) terminates the entire execution immediately." | met: **NO** / **NO** / **NO** |
| h3 | met: "immediately terminates the entire execution, including all other running branches in the `FORK`" | met: **NO** / **NO** / **NO** |

Divergence. Sonnet: none. Haiku: none. h1 puts `DELEGATE docs` after the STOP and omits it from the trace, which conflicts with the given event that the docs branch "has executed `DELEGATE docs`". This does not change the D-items.

Errors:
1. **All six probes. Tag `SEMANTIC`, minor, not a D-item failure.** They say `JOIN` is "never reached". Examples: h1 "Execution terminates before the JOIN statement is ever reached"; s2 "`JOIN` is never even reached". But when a `JOIN` follows a `FORK`, the parent flow goes straight to the `JOIN` and waits there. The JOIN is pending, not unreached, which is the case the spec names.
   - Spec: STOP: "A pending `JOIN` never completes."
   - Spec: FORK: "No `JOIN` follows | Execution continues immediately after the `FORK` while the branches run". The spec states this only for the no-JOIN case.
   - Classification: **spec-gap**. The spec never says that the parent flow reaches a following `JOIN` immediately. The Complete example trace also lists `JOIN -> joined` after the branch steps, which suggests that JOIN is reached later.
2. **h1. Tag `INVENT`, minor.** Its trace leaves out `DELEGATE docs`, and it states "Although DELEGATE docs has completed", yet it traces the STOP without that step. The trace is incomplete but not wrong about outcomes.
   - Spec: Executing a program: "write one line per executed step".
   - Classification: **model-error**. On reflection this is an omission, not an invention, so it would be better tagged `OTHER`.

Verdict: **PASS-S yes, PASS-H yes.**

---

## NEW issues

- **HITL classification of paraphrased answers with extra feedback (S12 D4).** Haiku consistently treats "Not like this, rewrite the intro." as insufficient. Sonnet chooses usable but flags the spec as underdetermined. The usable/insufficient table needs a positive example of a paraphrased answer, for instance "Not like this, rewrite the intro" → `rejected`. It also needs a sentence saying that extra remarks alongside a clear choice do not make a response insufficient.
- **A `JOIN` directly after a `FORK` is reached immediately and is pending (S15).** The FORK table covers only "No `JOIN` follows". Add a row: "`JOIN` follows | The parent flow reaches the `JOIN` at once and waits there." The trace convention (where to place `JOIN -> waiting`) is also unspecified; see S14-h1 versus the others.
- **The trace effect after STOP (S12-h3).** State that `stop` is the last trace line and that no `end` line follows it.

## Scenario issues

- S15 D2 says "JOIN: never completes". That is consistent with the spec. The scenario could also check whether the probe wrongly says JOIN is "never reached". Every probe says so, and it is technically inaccurate, but the current D-item does not penalise it.
- None otherwise.

---

## Summary table

ID | PASS-S | PASS-H | sonnet D met | haiku D met | tags | top spec section
---|---|---|---|---|---|---
S11 | yes | yes | 6/6 | 6/6 | — | Validity rules V3; FORK ("`BREAK` in a branch → INVALID (rule V3)")
S12 | yes | no | 12/12 | 9/12 | SEMANTIC (h1,h2,h3 D4); SEMANTIC minor (h3 end after stop) | HITL › Usable, insufficient, unavailable ("in any wording")
S13 | yes | yes | 9/9 | 9/9 | OTHER minor (h3) | AUTO ("criteria … do not cover the case")
S14 | yes | yes | 9/9 | 9/9 | — | WHEN (consecutive WHENs independent); TRANSITION (latest wins)
S15 | yes | yes | 6/6 | 6/6 | SEMANTIC minor (all: "JOIN never reached"); INVENT/OTHER minor (h1) | STOP ("A pending `JOIN` never completes"); FORK table

```
PART SUMMARY
scenarios: 5
pass_s: 5/5   pass_h: 4/5
d_items_s: 42/42   d_items_h: 39/42
danger_s: 0   danger_h: 0
```
