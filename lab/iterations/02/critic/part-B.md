# Critic part B — iteration 02 (S06 S07 S08 S09 S10)

Spec: `dsl-lab/iterations/02/DSL.md`. No assigned D-item says "Linter VALID", so the linter was not used for grading. For reference, `lint.txt` flags the S09 program quoted by s1–s3 as INVALID (V6 at line 3 and V6 at line 5), which matches every probe's own verdict.

---

## S06 — WHEN no outcome matches (LOOP:build)

D-items: D1 each iteration is DELEGATE → VERIFY (rejected) → WHEN false, skipped (no error, no waiting) → body restarts. D2 EMIT is never executed; the loop repeats indefinitely.

| Probe | D1 | D2 |
|---|---|---|
| s1 | met: "`WHEN build.accepted -> false: skip`" … "`LOOP:build -> loop again`" (both iterations) | met: "on the information given — it is never executed at all" |
| s2 | met: "The flow (`→ BREAK`) is skipped; this is not an error, and execution does not wait" | met: "it is **never** executed at all" |
| s3 | met: "This is not an error and execution does not wait. Effect: `false: skip`" | met: "execution keeps restarting the body indefinitely" |
| h1 | met: "this condition is **false** … The `→ BREAK` statement is not executed … The loop repeats." | met: "**`EMIT build-report` is never executed.**" … "repeat indefinitely" |
| h2 | met: "The WHEN body is skipped … the next iteration starts at the first statement of the body" | met: "never executed … the loop continues indefinitely" |
| h3 | met: "The condition is **false**, so the flow (containing `BREAK`) is skipped" … "the first statement again" | met: "never executed. The loop continues indefinitely" |

Note on D1: s1, h1, h2 and h3 do not say "no error, no waiting" in so many words. They also claim neither, and each goes straight from the skipped WHEN to the body restart, so D1 is graded met.

Divergence: sonnet none; haiku none.

Errors (none change a D-item):
- h1, `SEMANTIC`, minor. Justifies the false WHEN with "According to Execution Rule 7: 'Before anything establishes it, every `WHEN` on it is false.'" Rule 7's "not yet established" clause does not apply, because `build` already holds `rejected`. The governing sentence is WHEN §: "The condition is true only if the latest outcome of `<subject>` is exactly `<outcome>`." Class: model-error.

Verdict: **PASS-S = PASS**, **PASS-H = PASS**.

---

## S07 — WAIT

D-items: D1 the DSL does not name the event; the runtime or process determines it. D2 `VERIFY data-migration` runs next. D3 No. D4 execution stays at WAIT; there is no timeout.

| Probe | D1 | D2 | D3 | D4 |
|---|---|---|---|---|
| s1 | met: "The DSL does not name the event. The surrounding process and the runtime determine it." | met | met: "No." | met: "remains suspended at that `WAIT` statement indefinitely. It does not time out" |
| s2 | met: "The specification does not determine this" + quote | met | met | met: "suspends indefinitely … no implicit `STOP`" |
| s3 | met: "does not determine what event `WAIT` is suspended on" | met | met | met |
| h1 | met (quote), plus speculation, see errors | met | met | met: "remain suspended at the `WAIT` statement indefinitely" |
| h2 | met (quote), plus speculation, see errors | met | met | met: "remains suspended at `WAIT` with no mechanism to time out" |
| h3 | met (quote), plus speculation, see errors | met | met | met |

Divergence:
- Sonnet: not material. s1 and s2 each add an explicitly labelled assumption that the event is some external signal related to the migration. s3 declines to adopt any reading. All three state D1 and all three rule out the DELEGATE result.
- Haiku: none. All three make the same speculative addition.

Errors:
- h2, `SEMANTIC`. "In practical terms, given the context, execution would wait for the delegated actor to deliver its result from the data-migration work." DELEGATE §: "The statement is done when the actor has delivered its result. The next statement starts only then." The delegated result is already delivered before `WAIT` is reached. Class: model-error.
- h1, `SEMANTIC`, hedged. "the context suggests the `WAIT` may be waiting for the actor to deliver a result from the `data-migration` delegation". Same spec sentence. Class: model-error.
- h3, `SEMANTIC`, hedged. "reasonable to infer the runtime would likely wait for the delegated work to complete and return a result". Same spec sentence. Class: model-error.

All three haiku probes also state the D1 rule itself and say the DSL does not specify the event, so D1 is graded met. The pattern is systematic, though (3/3 haiku). See NEW issue 1.

Verdict: **PASS-S = PASS**, **PASS-H = PASS** (D-items met; the errors are recorded above).

---

## S08 — Unsatisfiable REQUIRE without FALLBACK

D-items: D1 no FALLBACK → execution ends, as with STOP. D2 DELEGATE is not executed. D3 EMIT is not executed. D4 the agent must not fabricate or assume the credentials, and must not continue in a degraded mode.

| Probe | D1 | D2 | D3 | D4 |
|---|---|---|---|---|
| s1 | met: "execution **ends immediately, as with `STOP`**" | met: "No." | met: "No" | met: "Not assume, fabricate, or substitute … not skip the `REQUIRE` or continue in a degraded mode" |
| s2 | met: "**execution ends, as with `STOP`.**" | met | met | met: "Not assume, fabricate, or substitute … not continue in a degraded mode" |
| s3 | met: "**execution ends, as with `STOP`.**" | met | met | met: quotes the MUST NOT sentence |
| h1 | met: "execution terminates immediately" + table quote | met: "**No.**" | met: "**No.**" | met: "Key principle … MUST NOT assume, fabricate, or substitute … degraded mode." |
| h2 | met: "execution **ends immediately**, as if `STOP` were executed" | met | met | met: "**NOT assume, fabricate, or substitute** … **NOT skip** … degraded mode" |
| h3 | met: "Execution ends immediately … as if `STOP` were called" | met | met | met: quotes the MUST NOT sentence |

Divergence:
- Sonnet: not material. The traces differ in notation only: s1 and s3 write `waiting` then `stop`, while s2 writes `stop` directly.
- Haiku: none.

Errors (minor, none change a D-item):
- h1, `SEMANTIC`. "Execution ends normally at the `REQUIRE` statement". REQUIRE §: "Execution ends, as with `STOP`." A normal end is defined only by rule 10: "When the last top-level statement is done, execution ends normally." Class: model-error.
- s1, `SEMANTIC`, trace only. Adds "3. (end of program) -> end" after "REQUIRE staging-credentials -> stop". STOP §: "Ends the entire execution immediately." The `end` effect belongs to rule 10's normal end. Class: spec-gap (the trace effects list does not say whether `end` follows a `stop`).

Verdict: **PASS-S = PASS**, **PASS-H = PASS**.

---

## S09 — Undeclared outcome names

D-items: D1 INVALID: V6 for `implementation.passed` and V6 for `tests.failed`. D2 the program is not executed at all; the agent reports the violations.

| Probe | D1 | D2 |
|---|---|---|
| s1 | met: "**INVALID, under rule V6 — twice.**" (both WHENs analysed) | met: "Nothing — because the program is INVALID … reports rule V6 for each faulty `WHEN`, and does not execute" |
| s2 | met: "INVALID solely (but doubly) under **V6**" | met: "**never reaches the point of running `VERIFY implementation` at all** … report the broken rule (V6, cited twice)" |
| s3 | met: "fails rule **V6** twice, once for each `WHEN`" | met: "refuse to execute, and report the broken rule(s) — in this case **V6**" |
| h1 | met: "violates validity rule **V6** twice" | met: "**does not execute the program at all** … reports these violations" |
| h2 | met: "violates rule V6 twice" | met: "**The agent MUST NOT execute this program.**" … "must report violations of rules **V6**" |
| h3 | met: "Rule V6 (violated twice)" | met: "must reject the program entirely and report rules V6 (violated twice)" |

Divergence:
- Sonnet: none. All three add a clearly labelled hypothetical trace (no transition runs, normal end), and the three agree.
- Haiku: not material. The primary answers agree, but the labelled hypotheticals differ. h2 "fixes" `passed` → `rejected` and ends in state "Review". h3 says it changes the conditions and then evaluates the original `passed`, so no transition runs. h1 gives no hypothetical.

Errors (outside the D-items):
- h2, `OTHER`. The hypothetical rewrites the program ("change `WHEN implementation.passed` to `WHEN implementation.rejected`") and traces the result. It is labelled hypothetical and is not presented as agent behaviour. Executing a program §: "Never skip, reorder, merge, or add statements." Validity rules: "It MUST be rejected as a whole." Class: model-error.
- h3, `OTHER`. The hypothetical contradicts itself: it proposes "changing the conditions to `implementation.rejected`" and then evaluates "`WHEN implementation.passed` would be false". No spec sentence is involved. Class: model-error.

Verdict: **PASS-S = PASS**, **PASS-H = PASS**.

---

## S10 — Scope of nested lines under →

D-items: D1 the flow is DELEGATE correction, VERIFY correction, TRANSITION "Rework", sequential in that order. D2 EMIT is outside the WHEN and runs afterwards. D3 (Q5) VERIFY review runs, the WHEN is skipped, then EMIT review-report runs.

| Probe | D1 | D2 | D3 |
|---|---|---|---|
| s1 | met: "exactly three statements … Sequential … 1. DELEGATE 2. VERIFY 3. TRANSITION" | met: "It is **not** part of the WHEN flow … It **is** executed" | met: "1. `VERIFY review` … 2. `WHEN review.rejected` → false: skip 3. `EMIT review-report`" |
| s2 | met | met: "**not** part … It **is** executed" | met: "1. `VERIFY review` … 2. … false: skip … 3. `EMIT review-report` → runs" |
| s3 | met | met | met: "1. `VERIFY review` … 2. … evaluated false, skipped 3. `EMIT review-report`" |
| h1 | met: "**Sequential.** … 1. DELEGATE 2. VERIFY 3. TRANSITION" | met: "Not part of the WHEN flow … **Yes.**" | **NOT met**: "Only **`EMIT review-report`** would execute." (leaves out `VERIFY review`) |
| h2 | met: "Sequential … DELEGATE, VERIFY, TRANSITION" | met | met: "`VERIFY review` … `EMIT review-report`", WHEN "skipped" |
| h3 | met | met | met: "1. `VERIFY review` 2. `EMIT review-report`", WHEN "skipped entirely" |

Divergence:
- Sonnet: none.
- Haiku: **material** on Q5. h1 answers "Only EMIT review-report", while h2 and h3 list `VERIFY review` and `EMIT review-report`.

Errors:
- h1, `SEMANTIC`. "Only **`EMIT review-report`** would execute." `VERIFY review` is the first top-level statement and runs in both cases. Execution rule 1: "Statements run one at a time, in the order written." Syntax › The arrow, example: "`EMIT review-report` is outside the `WHEN` and runs afterwards in every case." Class: model-error.
- h1, `OTHER`, minor. Cites a non-existent "rule 59 in the Quick reference" (a line number). No effect on the result. Class: model-error.
- h3, `SEMANTIC`, minor. For Q5 it cites "Rule 7: 'Before anything establishes it, every `WHEN` on it is false'", but `review` has been established (as `accepted`). The governing sentence is WHEN §: "true only if the latest outcome … is exactly `<outcome>`". The conclusion is correct. Class: model-error.

Verdict: **PASS-S = PASS**, **PASS-H = FAIL** (h1 misses D3; material haiku divergence).

---

## NEW issues

1. **WAIT after DELEGATE (S07).** All 3 haiku probes guessed that `WAIT` waits for the preceding DELEGATE's result. The DELEGATE § already rules this out, so these are model-errors. Still, one sentence in WAIT § would likely remove the pattern, for example: "`WAIT` never waits for a preceding `DELEGATE`; that statement is already done."
2. **Trace effect for a failed REQUIRE with no FALLBACK (S08).** s1, s2 and s3 all note that the effects list has no entry for this case and improvise `stop`. They also differ on whether a `waiting` line comes first, and s1 adds an `end` line after `stop`. The spec should say (a) which effect to use and (b) whether `end` follows `stop`. Class: spec-gap.
3. **Rule 7 misapplied (S06-h1, S10-h3).** Haiku probes cite the "not yet established" clause for a subject that already holds the other outcome. The conclusions are correct, but Quick reference rule 7 could add: "An established outcome other than `<outcome>` also makes the `WHEN` false." Class: misleading-wording, low priority.
4. **Initial process state (S09-s1, S10-s1).** Sonnet probes note that no initial or default state is defined before the first `TRANSITION`. This does not affect any D-item. Class: spec-gap, low priority.

## Scenario issues

- S06 D1: the parenthetical "(no error, no waiting)" is ambiguous. Only s2 and s3 state it explicitly, and I graded it as "not claimed otherwise". Clarify whether an explicit statement is required.
- S09 Q2: "negative" is not a DSL term. s1, s2 and s3 each spend an assumption mapping it to `rejected`. "establishes `implementation.rejected`" would be cleaner.
- S10 D3: Q5 asks "which statements would execute". Whether `VERIFY review` (which runs before the branch point) must be listed is the only reason h1 fails. The D-item says so explicitly, so I kept it, but the question wording could name it.

---

## Summary table

| ID | PASS-S | PASS-H | sonnet D met | haiku D met | tags | top spec section |
|---|---|---|---|---|---|---|
| S06 | PASS | PASS | 6/6 | 6/6 | SEMANTIC (h1, minor) | Control › LOOP (example); WHEN table |
| S07 | PASS | PASS | 12/12 | 12/12 | SEMANTIC ×3 (h1, h2, h3) | Control › WAIT; Agentic › DELEGATE |
| S08 | PASS | PASS | 12/12 | 12/12 | SEMANTIC (h1, s1; minor) | Agentic › REQUIRE table |
| S09 | PASS | PASS | 6/6 | 6/6 | OTHER (h2, h3; hypotheticals) | Validity rules V6; VERIFY |
| S10 | PASS | FAIL | 9/9 | 8/9 | SEMANTIC (h1 D3; h3 minor), OTHER (h1 minor) | Syntax › The arrow (example of nesting); Execution rule 1 |

```
PART SUMMARY
scenarios: 5
pass_s: 5/5   pass_h: 4/5
d_items_s: 45/45   d_items_h: 44/45
danger_s: 0   danger_h: 0
```
