# Critic report — iteration 01, part B (S06–S10)

## S06

**Verdict: PASS**

### D-item table

| Probe | D1 iter 1 trace, WHEN not satisfied, flow skipped | D2 iteration 2 identical | D3 unmatched WHEN: no error/stop/wait/escalation | D4 EMIT never runs, loop continues indefinitely |
|---|---|---|---|---|
| p1 | met: "this condition is **not satisfied**. Per **WHEN**, the flow following `→` (`BREAK`) is therefore **not executed**" | met: "The loop body runs again, identically to iteration 1" | met: "execution simply proceeds with no additional effect, falling through to the next statement" | met: "`EMIT build-report` would **never be executed**" |
| p2 | met: "this `WHEN`'s flow (`BREAK`) is not executed" | met: iteration 2 steps 1–5 are the same as iteration 1 | met: "nothing happens beyond the (non-)evaluation of the condition" | met: "the loop keeps iterating indefinitely and `EMIT build-report` is never executed at all" |
| p3 | met: "`BREAK` is **not executed**" | met: "executed again from the top, identically to iteration 1" | met: "falls through ... rather than any other behavior (e.g., an implicit error or implicit exit)" | met: "the loop ... never terminates. Consequently ... `EMIT build-report` is never executed" |

### Divergence
None. All three probes agree on the loop body, that `EMIT` sits outside the loop, that an unmatched WHEN falls through, that the loop re-enters at the top, and that the loop never terminates. All three label the same two points as assumptions: that the loop goes back to the top at the end of the body, and that an unmatched WHEN falls through. They agree on U1 (the spec does not state the no-match behavior).

### Errors
| Probe | What | Section | Class |
|---|---|---|---|
| — | none | — | — |

### New issues
- **LOOP re-entry is not stated.** All three probes infer it. The LOOP section says only "The loop continues until `BREAK`, `STOP`, or another explicit control flow terminates it." Nothing says that reaching the end of the body returns control to the first statement. (spec-gap, LOOP)
- **The phrase "another explicit control flow terminates it" is undefined.** p1 notes it. No construct other than BREAK or STOP is named as a loop terminator. (spec-gap, LOOP)
- **A repeated `DELEGATE` has no defined meaning.** p2 and p3 point out that the spec does not say whether a `DELEGATE build` in a later iteration is a new assignment or a retry of the same work. It does not change control flow, so it is minor. (spec-gap, DELEGATE)

### Scenario issues
- D3 is correctly an inference. The spec never says outright that an unmatched WHEN is a no-op; F-05 already covers this.
- D4 relies on the unstated re-entry rule above, so strictly it rests on the same kind of inference as D3. The expected section could cite that dependency.

---

## S07

**Verdict: PASS**

### D-item table

| Probe | D1 (Q2) `VERIFY data-migration` runs next | D2 (Q3) reaching VERIFY does not mean success |
|---|---|---|
| p1 | met: "`VERIFY data-migration` executes immediately after `WAIT` ends" | met: "No." Cites WAIT "does not imply success or failure", DELEGATE, and VERIFY |
| p2 | met: "the next statement in sequence is: `VERIFY data-migration`" | met: "No." Cites WAIT, DELEGATE, and VERIFY |
| p3 | met: "`VERIFY data-migration` executes immediately after `WAIT` ends" | met: "No." Cites DELEGATE, WAIT, and VERIFY |

### Divergence
- **Q1 (U1), consistent.** All three say the spec does not tie a bare `WAIT` to any event. All three name "the result of the delegated data-migration" only as an explicit assumption drawn from declaration order.
- **Q4 (U2), consistent.** All three say no timeout or fallback is defined and execution stays suspended indefinitely. All three note that FALLBACK is shown only with HITL.
- p2 also reasons by analogy to REQUIRE ("must not proceed as if..."). That is extra commentary, not divergence.

### Errors
| Probe | What | Section | Class |
|---|---|---|---|
| — | none | — | — |

### New issues
- **FALLBACK is only ever shown with HITL.** Its definition is generic: "Defines the flow to use when an expected response is unavailable or insufficient". But it appears only as `HITL(...) → FALLBACK`. All three probes asked whether it could attach to `WAIT` and concluded it cannot. The spec does not say whether FALLBACK is HITL-only or general. (underspecified-syntax, FALLBACK: "`FALLBACK` is associated with response handling.")
- **WAIT says "the required event" but never says what makes an event required.** Its text is "After the required event or response becomes available". This is the root of U1. (spec-gap, WAIT)

### Scenario issues
- U2 is arguably determined, not underdetermined. "Suspends execution until an external event or response is available" literally gives indefinite suspension when nothing else is defined. All three probes reached that reading. What is actually underdetermined is whether a timeout or fallback *can* be expressed at all. Suggestion: move "remains suspended" into the D-items and keep "no way to express a timeout or fallback" as the U-item.

---

## S08

**Verdict: PASS** (with a minor Q4 nuance, noted below)

### D-item table

| Probe | D1 must not proceed as if satisfied, no fabrication | D2 DELEGATE not executed | D3 EMIT not executed |
|---|---|---|---|
| p1 | met: "must **not** fabricate, substitute, or otherwise treat `staging-credentials` as available" | met: "**No.** ... `DELEGATE deployment` must not run" | met: "**No.**" |
| p2 | met: "must not invent, guess, or substitute a resolution for the missing requirement" | met: "**No.**" | met: "**No**" |
| p3 | met: "must **not** fabricate, guess, or silently substitute a result" | met: "**not executed**" | met: "**not executed**" |

### Divergence
- **Q4 core answer, consistent.** All three: halt/block forward progress at `REQUIRE`. Do not run `DELEGATE` or `EMIT`. Do not automatically invoke `HITL` or `STOP`. Whether this means terminating, suspending, or escalating is not determined (U1).
- **Minor difference in labeled assumptions.** Each probe marks its view as an assumption, so this is not counted as a material divergence:
  - p3 says the agent should "halt and surface the unmet requirement outside the DSL (… a human notification via some out-of-DSL channel …)". That leans toward an error/escalation reading.
  - p1 says to surface it "**only if** such a construct is authored elsewhere … within this fragment alone, the only DSL-sanctioned action is to not proceed".
  - p2 says this is "not decidable from this specification alone".
- p3 reads the halt as "blocked, pending some resolution", which leans toward suspension. p1 and p2 leave it open.

This is the U1 gap showing through. If the spec defined REQUIRE failure handling, all three would converge on one concrete agent action.

### Errors
| Probe | What | Section | Class |
|---|---|---|---|
| p1/p2/p3 | Q4 concrete action differs slightly (report out-of-band / only if authored / undecidable) | REQUIRE: "If a required condition cannot be satisfied, execution must not proceed as if the requirement were satisfied." | spec-gap |

### New issues
- **REQUIRE establishes no outcome a WHEN can test.** p1 and p3 note that, unlike VERIFY, REQUIRE produces nothing like `staging-credentials.unavailable`. So an author cannot write failure handling for REQUIRE inside the DSL at all. (spec-gap, REQUIRE and VERIFY: "Verification may establish outcomes that can be used by `WHEN`.")
- **The prohibition is weaker than it looks.** "Must not proceed *as if* the requirement were satisfied" logically allows proceeding in some other way, for example in a degraded mode. The preceding sentence ("must be satisfied before execution continues") is stricter. All probes took the strict reading, but the qualifier invites the loose one. (misleading-wording, REQUIRE)
- The same FALLBACK-scope question raised under S07 comes up again here: p2 and p3 say FALLBACK is "explicitly scoped only to `HITL`". (underspecified-syntax, FALLBACK)

### Scenario issues
- None. D1–D3 are determined by the REQUIRE text. U1 is genuinely open, although "must be satisfied before execution continues" leans slightly toward a suspension (block-until-satisfied) reading.

---

## S09

**Verdict: FAIL**

### D-item table

| Probe | D1 VERIFY "may establish outcomes"; no outcome vocabulary listed |
|---|---|
| p1 | met: "does not define a fixed, closed vocabulary of outcome names … 'Verification may establish outcomes that can be used by `WHEN`.'" |
| p2 | met: "does not enumerate a fixed vocabulary of outcome names" |
| p3 | met: "does not define a fixed, closed vocabulary of outcome names" |

### Divergence

| Question | p1 | p2 | p3 | Material? |
|---|---|---|---|---|
| Q1 (U1) | Undefined. The example uses `.accepted`/`.rejected`; other names are syntactically legal | Same; vocabulary is "process-defined" | Same; accepted/rejected is "illustrative rather than exhaustive" | no |
| Q2 (U2) | Syntactically valid, but "the safest reading is that `implementation.passed` is *not shown to be established* by the preceding `VERIFY`". Leans toward an undefined condition | "valid in form and in its apparent reference to the preceding `VERIFY`". Assumes it is a synonym for accepted | "valid *only if* the surrounding process" defines it. Assumes it is a synonym for accepted | **yes**: p1 treats it as ungrounded; p2 and p3 treat it as the positive outcome |
| Q3 (U3) | Syntactically valid; `tests` comes from an unshown part of the process ("orphaned" locally) | Same; most likely a separate unshown `VERIFY tests` | Same, and also says it "may equally indicate a mismatch" (a typo for `implementation.failed`) | minor: p3 raises the possibility that it is an authoring error |
| Q4 (U4) | "**None** of the two shown `TRANSITION` statements is executed" | "**neither `TRANSITION` … is executed**", though Debugging would fire if `tests` failed elsewhere | "neither … is **guaranteed** to execute". Debugging's condition is undetermined | **yes**: p1 gives a definite "none"; p3 says Debugging is indeterminate |

The pass rule requires identical answers to Q1–Q4. Q2 and Q4 diverge, so the verdict is FAIL. The scenario expected this outcome on the baseline spec.

### Errors
| Probe | What | Section | Class |
|---|---|---|---|
| p1 vs p2/p3 | Q2: is `implementation.passed` an outcome of `VERIFY implementation`? | VERIFY: "Verification may establish outcomes that can be used by `WHEN`." The example uses `.accepted`/`.rejected`; the WHEN example uses `.passed`/`.failed` | spec-gap |
| p1 vs p3 | Q4: whether `TRANSITION "Debugging"` can fire, since `tests.failed` is established by nothing shown | WHEN example: `WHEN tests.passed → TRANSITION "Review"`. It is shown with no statement establishing `tests`, which suggests conditions may reference outcomes established elsewhere | misleading-wording |
| p1 | In Q4, reasons by analogy with REQUIRE ("execution must not proceed as if…") to justify a WHEN fall-through. REQUIRE does not govern WHEN. The answer is unaffected | REQUIRE / WHEN | model-error |

### New issues
- **The `x.y` condition form has no grammar.** All three call `implementation.passed` "a valid Identifier", but the Identifier section (`<identifier>`) never defines the `<result>.<outcome>` form. WHEN's `<condition>` is not defined in Syntax either. (underspecified-syntax, Syntax/Identifier and Conditional Flow: "WHEN <condition>")
- **Two sentences pull against each other.** p3 cites "Multiple `WHEN` constructs may describe different outcomes of the same process state" as implying that sibling WHENs should share a subject. p2 cites the same sentence as licensing conditions on state established elsewhere. (misleading-wording, WHEN)

### Scenario issues
- Q4 is partly determined. Under every reading the probes gave, a negative verification does not satisfy `implementation.passed`, so `TRANSITION "Review"` does not run. That part could become a D-item. Only the Debugging branch is truly underdetermined (U3).

---

## S10

**Verdict: PASS**

### D-item table

| Probe | D1 sequential: DELEGATE correction → VERIFY correction → TRANSITION "Rework" | D2 EMIT outside WHEN, runs after the WHEN flow | D3 accepted: VERIFY review → EMIT review-report |
|---|---|---|---|
| p1 | met: "Sequentially, in declaration order: 1. `DELEGATE correction` 2. `VERIFY correction` 3. `TRANSITION "Rework"`" | met: "**not** indented under `WHEN` … which therefore executes" | met: WHEN flow skipped; "`EMIT review-report` — executes" |
| p2 | met: same order, "Sequential" | met: "Part of the flow: no … Executed: yes" | met: "Only: 1. `VERIFY review` 2. `EMIT review-report`" |
| p3 | met: same order, "Sequentially" | met: full order ends with "5. `EMIT review-report`" | met: "Only: 1. `VERIFY review` 2. `EMIT review-report`" |

### Divergence
None material. All three put `VERIFY correction` in the WHEN flow, read multiple `→` under WHEN as one sequential flow (concurrency belongs only to FORK), treat the unmatched WHEN in Q5 as a fall-through, and give the same execution order. All three flag the same assumption: the two-`→` WHEN form appears only in the Syntax box, and `→` means something different under FORK.

### Errors
| Probe | What | Section | Class |
|---|---|---|---|
| — | none | — | — |

### New issues
- **The Scope rule does not cover this nesting.** It reads "Indented statements belong to the preceding scoped construct". `DELEGATE` is not a scoped construct, yet p1 says `VERIFY correction` belongs to "the preceding scoped construct — here, that is the `DELEGATE correction` step", and p3 speaks of "that statement's own nested scope". Only Forked Flow defines "Indented statements following a branch belong to that branch". Nothing defines nesting under a WHEN `→` item. This is F-04 plus a wording problem: the probes had to treat a non-scoped operation as a scope. (underspecified-syntax, Syntax/Scope)
- **`→` is overloaded.** Under FORK it means "Each `→` starts an independent flow"; under WHEN it means sequential items of "the flow". All three probes had to argue their way to the WHEN reading. (misleading-wording, FORK vs WHEN/Conditional Flow)
- **Fall-through after a WHEN is never stated.** p3 notes that the spec does not say explicitly that execution continues past a WHEN, whether or not its flow ran. This is related to F-05. (spec-gap, WHEN/Flow)

### Scenario issues
- None. The D-items follow from WHEN, Conditional Flow, and Flow. U1 is correctly marked as underdetermined, and the probes converged on the canonical reading anyway.

---

## Summary

| Scenario | Verdict | # probes fully correct | Top section(s) implicated |
|---|---|---|---|
| S06 | PASS | 3/3 | LOOP (re-entry unstated), WHEN (no-match unstated) |
| S07 | PASS | 3/3 | WAIT (no event binding, no timeout), FALLBACK (scope HITL-only?) |
| S08 | PASS | 3/3 | REQUIRE ("must not proceed as if…"; no failure outcome or handling), FALLBACK |
| S09 | FAIL | 3/3 on D1; convergence fails (Q2, Q4) | VERIFY (outcome vocabulary), WHEN example (`tests.*` unestablished), Syntax/Identifier (`x.y` form) |
| S10 | PASS | 3/3 | Syntax/Scope (nesting under a non-scoped `→` item), FORK vs Conditional Flow (`→` overload) |
