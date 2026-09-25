# Critic report — iteration 01, part E (S11, S13)

## S11

### Verdict
**FAIL.** All three probes meet D1–D3. The pass rule also requires the same answer for U1–U3, and the probes give three different answers for U2 and U3.

### D-item table

| Probe | D1 BREAK exits `review`, not whole execution | D2 no further iteration; `TRANSITION "Reviewed"` not run | D3 `EMIT review-summary` runs after loop exit |
|---|---|---|---|
| p1 | met: "`LOOP:review` is exited now … `BREAK` does not terminate the entire execution" | met: "JOIN and TRANSITION "Reviewed" … are simply skipped" | met: "It does execute, exactly once" |
| p2 | met: "this affects `LOOP:review` only, not the whole program" | met: "`TRANSITION "Reviewed"` does not execute … no further iteration" (under both of its readings) | met: "Executes exactly once, under either interpretation" |
| p3 | met: "The current loop is `LOOP:review`, so this loop is exited" | met: "Never executes … there is no further iteration" | met: "`EMIT review-summary` executes" |

### Divergence

| Item | p1 | p2 (primary reading) | p3 | Material? |
|---|---|---|---|---|
| U1 BREAK inside a FORK branch permitted | permitted (assumed without discussion) | permitted | permitted | No. All three agree, but none cites text that settles it. |
| U2a docs-review branch | **not cancelled**. Keeps running as an orphan; its result has no effect | **awaited to completion**. `VERIFY docs-review` runs | **abandoned** together with the loop scope | **Yes: three different answers** |
| U2b `JOIN` | never reached or executed | **reached and blocks** until docs-review completes, then the loop exits | never reached or executed | **Yes** |
| When BREAK takes effect | immediately | **deferred** until the loop's sequential flow resumes after `JOIN` | immediately | **Yes** |
| U3 EMIT vs docs-review completion | EMIT can run while docs-review is still in flight | EMIT runs strictly **after** docs-review completes | EMIT runs after docs-review is abandoned (it never completes) | **Yes** |
| Termination | normal end after EMIT | normal end after EMIT | normal end after EMIT | No |

p2 also traces p1/p3's immediate-exit reading as "Interpretation 2", which shows the probe itself could not choose between the two readings.

### Errors

| Probe | What | DSL.md section (quote) | Class |
|---|---|---|---|
| p1/p2/p3 | Diverge on the fate of the sibling docs-review branch (orphan, awaited or abandoned) | `### FORK`: "Each `→` starts an independent flow." / `### BREAK`: "Exits the current `LOOP`." No text covers what happens to live sibling flows when a branch leaves the enclosing scope. | spec-gap |
| p2 vs p1/p3 | JOIN blocks and BREAK is deferred (p2), or JOIN is skipped and BREAK is immediate (p1/p3) | `### JOIN`: "Execution continues only after all required forked flows have completed." (unconditional) vs `### BREAK`: "Exits the current `LOOP`." (no timing given). The spec does not say which takes precedence. | spec-gap |
| p1/p2/p3 | Diverge on whether EMIT runs before or after docs-review completes (U3) | Follows from the two rows above. `## Flow`: "Statements execute in declaration order unless an explicit control construct changes the flow." gives no ordering between concurrent flows. | spec-gap |

No model-errors: each probe's reading is defensible from the text.

### New issues (not listed under the scenario's Expected)
1. **"required forked flows" is undefined** (p1 assumption 5; p2 relies on it). In `### JOIN` ("all **required** forked flows"), "required" suggests some branches may be non-required, but nothing defines which. Under p2's reading this word decides whether JOIN has to wait for docs-review. Class: spec-gap.
2. **Where control resumes after BREAK** (p3 assumption 3). `### BREAK` says only "Exits the current `LOOP`". It never says that execution continues with the statement after the loop. All probes infer this from "does not terminate the entire execution" plus `## Flow`. They converge, but the rule is implicit. Class: spec-gap (minor).
3. **How "current LOOP" resolves across a FORK boundary** (p1 assumption 1). The spec does not say whether a branch counts as being inside the enclosing loop for the purpose of `BREAK`. This is harmless here because only one loop exists. It would matter for nested loops, or if forked flows are treated as separate execution contexts. Class: spec-gap.
4. **No cancellation primitive exists at all** (p2 §3, p3 assumption 2). Nothing in the spec can stop an in-flight `DELEGATE`, so the "abandon" reading (p3) has no textual basis. The "orphan" reading (p1) leaves an unmanaged flow running. Class: spec-gap.

### Scenario issues
- D1–D3 are correctly determined. D2 and D3 also hold under p2's deferred-BREAK reading, so they do not depend on U2.
- U1 converged (all probes say BREAK is permitted), but only by default. `### BREAK` "may only exit a loop scope" can be read either way for a branch. The item stays underdetermined, and the scenario is right to list it as U.
- The prediction "Expected to diverge on the baseline spec" was correct.

---

## S13

### Verdict
**PASS.** All probes meet D1–D4 and give the same answer to Q1: the line is not valid under the grammar as given, and the spec never defines any syntax for AUTO. See the scenario issues below: this consistent answer is firmer than the spec actually supports.

### D-item table

| Probe | D1 uncertain → no auto-resolution, no guessing, no confidence score | D2 HITL put to a human; execution waits | D3 "Declined" → `TRANSITION "Deferred"`, not "Merged" | D4 VERIFY `accepted` alone does not authorize merge |
|---|---|---|---|---|
| p1 | met: cites "applicable criteria are … contradictory" and "multiple materially different decisions"; "a confidence score alone does not establish certainty" | met: "must actually be put to a human"; "execution does not proceed past this point until the human responds" | met: Steps 6–8 | met: "`accepted` here reflects only the criterion that was checked, not a judgment on the breaking change" |
| p2 | met: "`AUTO` cannot resolve the decision automatically … does not authorize the agent to invent or guess" | met: "execution effectively pauses at this boundary until a response is available" | met: Steps 6–7 | met: "it is explicitly not itself a decision to merge" |
| p3 | met: "the decision is uncertain and automatic resolution is not permitted"; cites the confidence-score line | met: "Execution suspends at this boundary, pending the human's response" | met: Steps 6–8 | met: "`accepted` here does not by itself resolve whether the breaking change is acceptable to merge" |

### Divergence

| Item | p1 | p2 | p3 | Material? |
|---|---|---|---|---|
| Q1 / U1 validity of `AUTO HITL(...)` | invalid. The argument is neither an Identifier nor a String, and the spec gives no AUTO syntax | invalid, same grounds. Notes AUTO is the only keyword with no syntax block | invalid, same grounds. Adds that AUTO "appears alone" in the spec | No. The answer and the reasoning are the same |
| Treatment for the trace | assumes the intended meaning: "HITL eligible for AUTO" | same | same | No |
| U2 binding of "Declined" to `merge.declined` | assumed direct mapping, flagged | assumed, flagged; compared to how VERIFY establishes outcomes | assumed, flagged | No. All three flag it and resolve it the same way |
| HITL suspension | assumed and flagged (only `WAIT` suspends explicitly) | assumed and flagged | stated as fact | No. The outcome is the same |
| Termination | ends in `Deferred` | same | same | No |

### Errors

| Probe | What | DSL.md section (quote) | Class |
|---|---|---|---|
| — | No D-item errors and no divergence. | — | — |

### New issues (not listed under the scenario's Expected)
1. **HITL is not given suspension semantics.** p1, p2 and p3 all had to assume it. `### HITL` says only "The human response may determine the subsequent flow." `### WAIT` is the only construct that "Suspends execution until an external event or response is available." It is unclear whether HITL implicitly waits or needs an explicit `WAIT` after it. Class: spec-gap.
2. **The Statement grammar reads as closed but is not.** All probes call `AUTO HITL(...)` invalid because `## Statement` is `<keyword> <argument>` and the only argument forms are `## Identifier` and `## String`. But the spec's own forms `HITL("<message>")`, `LOOP:<name>`, `WHEN <condition>` with `→` flows, and the bare `JOIN`/`BREAK`/`STOP` do not fit that grammar either. The Identifier and String sections say "may be used", which does not make them the only allowed forms. The grammar invites a strict reading the spec itself does not follow. Class: misleading-wording.
3. **How DELEGATE completion is signalled** (p1 assumption 2). The spec does not say whether `VERIFY` waits for delegated work to finish. Class: spec-gap.
4. **Where the HITL outcome identifier `merge` comes from.** Nothing in the program or in `### HITL` names the decision `merge`. The probes infer it from the WHEN lines. This is the scenario's U2 (F-03); it is repeated here because all probes flagged it independently.

### Scenario issues
- **U1 converged on "invalid" rather than "undetermined".** The scenario expects "validity … cannot be determined". The probes say "not valid" and add that the spec leaves AUTO syntax undefined. That is consistent, so the pass rule is met. But the verdict rests on reading `## Statement`/`## Identifier`/`## String` as a closed grammar, which the spec does not support (see new issue 2). Treat this as a latent problem: a spec edit that defines AUTO syntax should also say whether `## Statement` is normative and exhaustive. Otherwise later probes may split between "invalid" and "undetermined".
- D1 is well determined by `### AUTO`: "applicable criteria are missing, ambiguous, or contradictory" and "multiple materially different decisions remain reasonably compatible". Note that the stated criterion ("merge when verification accepts") is literally satisfied. Uncertainty comes only from the extra evidence, so D1 depends on AUTO's "available information" covering the changelog and the maintainers' notes. All probes read it that way.

---

## Summary

| Scenario | Verdict | # probes fully correct | Top section(s) implicated |
|---|---|---|---|
| S11 | FAIL | 3/3 on D-items; the probes do not converge on U2/U3 | `### FORK`, `### JOIN` ("all required forked flows"), `### BREAK` ("Exits the current `LOOP`") |
| S13 | PASS | 3/3 | `### AUTO` (no syntax block), `## Statement`/`## Identifier`/`## String` (grammar read as closed), `### HITL` (no suspension semantics) |
