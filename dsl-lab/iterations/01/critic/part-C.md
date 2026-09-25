# Critic report — iteration 01, part C (S12, S14, S15)

## S12 — HITL no response / insufficient response → FALLBACK

### Verdict
**PASS** — all 3 probes meet D1–D4.

### D-item table

| Probe | D1 Run A normal flow, no FALLBACK | D2 Run B → Blocked, STOP, no Published/EMIT, no invented approval | D3 Run C insufficient → same fallback | D4 FALLBACK `→` lines sequential |
|---|---|---|---|---|
| p1 | met — "`FALLBACK` is **not** entered" → `TRANSITION "Published"` → `EMIT release-notes` | met — "`TRANSITION "Published"` and `EMIT release-notes` are **never executed**"; "not treated as an approval or rejection" | met — "an **insufficient** response … cannot be used to continue the normal flow" | met — Assumption 4: "one ordered flow … not as two parallel branches" |
| p2 | met — "`FALLBACK` is **not** entered"; steps 4–6 Published, EMIT, end | met — 4a Blocked, 4b STOP, step 5 "**Never executed**"; "not the agent inventing a replacement approval decision" | met — "this is the insufficient-response case" | met — Assumption 1: "read as one flow executed in order" |
| p3 | met — "`FALLBACK` is therefore **not** invoked"; Published → EMIT | met — Blocked → STOP; Published/EMIT "**Not executed**"; "agent may not substitute its own judgment" | met — "This is an **insufficient** response" | met — Assumption 3: "the `WHEN` convention applies … executed in order" |

### Divergence
- D1–D4: no divergence; identical traces and final states (A: Published + emitted; B/C: Blocked, stopped).
- U1 (when "never responds" becomes "unavailable"): all 3 say the same thing. The spec has no timeout, and some runtime mechanism outside the DSL decides. p1 and p2 say HITL "suspends" execution. p3 says only "reaches a point requiring human input". That is a wording difference, not a divergence.
- U2 (approve vs. reject branching): p1 says outright that a rejection response has no defined path. p2 and p3 do not discuss rejection. No probe disagrees with another.
- Structural choices: all 3 read the two `→` lines under FALLBACK by analogy to WHEN and not to FORK. All 3 read an unmatched (usable) response as continuing to the next top-level statement. No material disagreement.

### Errors
None.

### New issues
1. **Multi-`→` form under FALLBACK is not defined.** The spec shows only `→ FALLBACK` / `→ <flow>` (one arrow). All 3 probes had to argue by analogy that two `→` lines under FALLBACK are sequential, because the same form means concurrent under FORK. Section: *FALLBACK* ("`→ FALLBACK` / `→ <flow>`"), plus *Conditional Flow* vs. *Forked Flow*. Class: `underspecified-syntax`. More generally, `→` is overloaded: it is a sequential statement list in WHEN, a concurrent branch in FORK, and an attachment marker in `HITL → FALLBACK`.
2. **DELEGATE blocking/completion before the next statement is undefined.** p1, p2 and p3 all note that nothing says the release notes exist when HITL asks for approval. Section: *DELEGATE* ("defines responsibility, not execution mechanics"). Class: `spec-gap`.
3. **Normal termination at end of program is undefined** (p2 Assumption 4). Section: *STOP* / *Flow*. Class: `spec-gap`. This is minor.
4. **"Usable" vs. "insufficient" response has no criterion.** All 3 probes assume that a non-decision reply counts as insufficient. Section: *FALLBACK* ("unavailable or insufficient"; "cannot be used to continue the normal flow"). Class: `spec-gap`. The scenario (D3) relies on this reading.
5. **Continuation after a usable response is only implied.** p1 flags it: "this continuation-to-surrounding-flow behavior is inferred rather than stated outright". Section: *HITL* ("The human response may determine the subsequent flow"). Class: `spec-gap` (related to U2/F-03).

### Scenario issues
- D4 is cited to *Flow*, but the program shape (two `→` lines under FALLBACK) is not in the spec's grammar. All 3 probes treat it as an assumption. It is better described as a strongly converging inference than as spec-determined. Consider moving it to "most likely reading" or adding a U-item for the `→` overloading.
- D3 depends on classifying "I haven't had time to look yet." as *insufficient*. The spec gives no criterion, but it is the natural reading and it converged, so it is acceptable as D.

---

## S14 — FORK branch fails; JOIN; multiple WHEN matches

### Verdict
**PASS**. All 3 probes meet D1–D2 and agree on D3/D4 (both WHENs fire in order; final state "Debugging"). Convergence here depends on inference, not on the spec's text (see Scenario issues).

### D-item table

| Probe | D1 concurrent branches; DELEGATE before VERIFY in each | D2 rejected VERIFY is an outcome, branch completes; JOIN waits for both | D3 WHENs in declaration order, both fire | D4 final "Debugging" |
|---|---|---|---|---|
| p1 | met — "Within each branch, statements still execute in declaration order … `FORK` only makes the *branches* concurrent" | met — "Branch B now completes"; "`JOIN` must wait until the later-finishing branch" | met — Step 7a Ready, Step 8a Debugging | met |
| p2 | met — Steps 2–5, DELEGATE A/B then VERIFY A/B, "order relative to Step 2 is not determined" | met — "This branch completes second"; "`JOIN` blocks until *both* branches" | met — "Both `WHEN` blocks fire" | met |
| p3 | met — "Within each branch, statements execute in declaration order (DELEGATE before VERIFY)" | met — VERIFY integration-tests "completes"; "Execution therefore blocks until … t2" | met — Steps 7, 8 | met |

### Divergence
- D1–D4: none.
- U1 (all satisfied WHENs vs. first match): all 3 choose "all execute, in declaration order" and flag it as an assumption. They converge.
- U2 ("required" flows; does a rejected branch count as completed): all 3 treat both branches as required and the rejected branch as completed. Only p3 explicitly flags "required" as undefined.
- Other structural choices: all 3 use last-write-wins TRANSITION semantics and treat reaching the end of the program as normal termination. No material disagreement.

### Errors
None.

### New issues
1. **Conflicting TRANSITIONs / single-valued state is not defined.** All 3 probes flag this: nothing says a second TRANSITION in the same pass overwrites the first, or whether it is a conflict. Section: *TRANSITION* ("Changes the current process state"). Class: `spec-gap`. The expected section does not mention this, but D4 depends on it.
2. **Visibility of branch-established outcomes after JOIN.** All probes assume that `unit-tests.accepted` set inside a forked branch is readable by top-level WHENs after JOIN. The spec does not state how outcomes are scoped across FORK/JOIN. Section: *VERIFY* ("Verification may establish outcomes that can be used by `WHEN`"), *FORK*. Class: `spec-gap`.
3. **The WHEN example invites an exclusivity reading.** "Multiple `WHEN` constructs may describe different outcomes of the same process state", together with the mutually exclusive `tests.passed`/`tests.failed` example, suggests an if/elif grouping. p1 and p3 explicitly discuss and reject that reading. Section: *WHEN*. Class: `misleading-wording` (feeds F-06).
4. Normal termination at end of program (p2 Assumption 4): *STOP*/*Flow*, `spec-gap`. Minor.

### Scenario issues
- D3/D4 are labelled "most likely reading (by inference only — F-06)". The probes converged, but every probe marks the reading as an assumption. D4 also depends on the new TRANSITION-overwrite assumption (New issue 1), which the scenario does not list. Suggest adding U3: "TRANSITION overwrite / conflicting state changes."
- D2's claim that "the integration branch completes" relies on U2 (F-12), because the spec never defines completion for a branch whose VERIFY rejected. The convergence is strong, but D2 is partly inference.

---

## S15 — STOP inside a FORK branch

### Verdict
**PASS**. All 3 probes meet D1–D2. The hedging about alternative readings shows minor divergence, but it does not affect the D-items.

### D-item table

| Probe | D1 STOP terminates entire execution incl. concurrent branches | D2 EMIT docs no; JOIN not completed; EMIT build no |
|---|---|---|
| p1 | met — "`STOP` here terminates the whole program's execution, not merely Branch A's flow" | met — No / No / No |
| p2 | met — "`STOP` terminates … Flow B, the sibling flow … the top-level flow" | met — No / No / No |
| p3 | met — "ends the **whole running process**, including any other concurrently executing forked flows" | met — No / No / No |

### Divergence
- D1/D2: none. All 3 get global STOP from the contrast with BREAK ("Use `STOP` to terminate the entire execution"), and all 3 flag it as an inference (U1/F-15).
- **Whether the parent flow reaches JOIN.** p2 says the parent flow "never reached/executed" JOIN. p1 says STOP happens "before the runtime would reach evaluating `JOIN`'s wait condition". p3 says "never proceeds to a live, completed `JOIN`". The spec's *FORK* section ("Use `JOIN` when execution must wait for the concurrent flows") implies the parent flow sits at JOIN while the branches run. The probes disagree mildly on this, but it does not matter here because the D-item only requires "JOIN does not complete". Class: `spec-gap`. The spec never says whether the parent flow continues to the next statement right after FORK.
- **Branch-local alternative reading.** p1 claims "Under either reading, `JOIN` does not complete and `EMIT build` is not executed". p3 says that under the branch-local reading, "Branch B could still complete `EMIT docs` and the program could proceed to a completed `JOIN` and `EMIT build`". These are opposite conclusions about the alternative reading. Neither affects the main answer.

### Errors

| Probe | What | Section | Class |
|---|---|---|---|
| p1 | Hedge: claims JOIN and EMIT build fail "under either reading" because "nothing … ever gets Branch B past `DELEGATE docs`". Under a branch-local STOP, nothing stops Branch B from continuing. This is a reasoning slip in the assumptions section only; the main answer is unaffected. | *FORK* ("Each `→` starts an independent flow") | `model-error` |

### New issues
1. **JOIN semantics for a branch that ends via STOP.** p1 and p3 flag that the spec does not say whether a STOP-terminated or preempted branch counts as "completed" for JOIN. Section: *JOIN* ("all required forked flows have completed"). Class: `spec-gap` (related to F-12).
2. **Fate of in-flight delegated work on STOP.** p1 and p2 flag that the spec does not say whether the dispatched `DELEGATE docs` work is cancelled or abandoned. Section: *STOP*, *DELEGATE*. Class: `spec-gap`. This may be intentionally outside the DSL, but the spec could say so.
3. **Where STOP's scope is defined.** The *STOP* section itself says only "Terminates execution" and "No subsequent statement is executed after `STOP`". The "entire execution" scope appears only in the *BREAK* section ("Use `STOP` to terminate the entire execution"). All probes had to reach it by contrast. Class: `spec-gap` (this is F-15). "Subsequent" is also ambiguous under concurrency: it could mean later in the same branch or later in wall-clock time.

### Scenario issues
- D1 is cited as determined via the BREAK section wording. That is defensible, and all probes converged. However, every probe calls it an inference and not an explicit rule, so D1 is borderline between D and U. The existing U1 covers this.

---

## Summary

| Scenario | Verdict | # probes fully correct | Top section(s) implicated |
|---|---|---|---|
| S12 | PASS | 3/3 | FALLBACK (multi-`→` form, "insufficient" criterion); HITL (continuation after a usable response) |
| S14 | PASS | 3/3 | WHEN (non-exclusivity only inferred; misleading example); TRANSITION (overwrite semantics); JOIN ("required", completion) |
| S15 | PASS | 3/3 (p1 has a minor hedge error) | STOP (scope only stated in BREAK); JOIN (completion with STOP); FORK (does the parent flow reach JOIN) |
