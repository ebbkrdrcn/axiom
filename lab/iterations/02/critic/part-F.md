# Critic part F — iteration 02

Scenarios: ST06, ST07, ST08, X01, X02. Spec: `dsl-lab/iterations/02/DSL.md`. Linter: `dsl-lab/iterations/02/lint.txt` (used only for "Linter VALID" D-items on authored programs).

---

## ST06 — Stress execution: two REQUIREs, one FALLBACK

All six probes produce the same run: the first REQUIRE waits, then completes. DELEGATE runs. The second REQUIRE (no FALLBACK) fails and execution ends "as with STOP". EMIT is not executed. No TRANSITION runs, so no state is set.

| Probe | D1 wait, then continue; no FALLBACK | D2 DELEGATE runs | D3 second REQUIRE ends execution; no EMIT; first FALLBACK not applied; no "Blocked" | D4 final state none |
|---|---|---|---|---|
| s1 | met: "1. REQUIRE staging-credentials -> waiting / 2. ... -> done"; "Its attached FALLBACK is never used" | met: "3. DELEGATE deployment -> done" | met: "5. REQUIRE monitoring-access -> stop"; "EMIT deployment-log is never reached"; "that FALLBACK never runs" | met: "the final process state is undefined/none" |
| s2 | met: "the attached FALLBACK is never used" | met: "3. DELEGATE deployment -> done" | met: "Execution ends, as with STOP ... EMIT deployment-log ... never runs" | met: "no process state is ever set by this run" |
| s3 | met: "the attached → FALLBACK ... is not run" | met: "3. DELEGATE deployment -> done" | met: "Execution therefore ends at this point ... EMIT ... never runs"; "This TRANSITION never executes" | met: "no process state was ever set" (also flags that the initial state is undefined) |
| h1 | met: "The FALLBACK attached to the first REQUIRE does not run" | met: "3. DELEGATE deployment -> done" | met: "4. REQUIRE monitoring-access -> stop"; "EMIT deployment-log is never reached" | met: "Undefined (not set)" |
| h2 | met: "1. ... -> waiting / 2. ... -> done"; the FALLBACK "never runs" | met: "3. DELEGATE deployment -> done" | met: "execution ends here (as with STOP)"; "never reaches EMIT deployment-log" | met: "Undefined / Not set" |
| h3 | met: "this FALLBACK never executes" | met: "3. DELEGATE deployment -> done" | met: "Execution ends at step 4 ... EMIT deployment-log statement is never reached" | met: "No state is set" |

**Divergence**
- Sonnet: none. All three have the same 5-line trace.
- Haiku: none that matters. All three have the same 4-line trace. The sonnet trio shows a `waiting` line at the second REQUIRE before `stop`; the haiku trio goes straight to `stop`. This is a difference in trace granularity between the two models, not within either trio.

**Errors.** No D-item errors. Minor issues outside the D-items:
- h1 `OTHER`, model-error. h1 attributes the no-FALLBACK ending to "rule 8 of **Executing a program**". That section has only five steps. The rule that applies is in the REQUIRE table: "The runtime determines the item cannot be obtained, and there is no `FALLBACK` | Execution ends, as with `STOP`."
- h2 `OTHER`, model-error. h2 says "The REQUIRE statement re-executes". The spec says "Wait at the `REQUIRE`", not re-execute. The result is unaffected.

**NEW issues**
- spec-gap (TRANSITION): "The process has exactly one current state" does not say what the state is before any TRANSITION runs. s2 and s3 flag this explicitly, and all probes answer "undefined/none".
- underspecified-syntax (trace effects): the effect list has no entry for "execution ends because a REQUIRE is unobtainable, or a HITL is unusable, with no FALLBACK". Every probe used `stop`, and s3 flags that `end` is an alternative.

**Scenario issues.** The events do not say that `DELEGATE deployment` delivers a result. s1, s2 and s3 had to infer it from "then". Consider adding "the deployment actor delivers its result" to the events.

**Verdict:** PASS-S yes, PASS-H yes.

---

## ST07 — Stress authoring: ten-step requirement

Linter: all six are VALID (lint lines 185–190). All six programs are structurally identical, with one exception: h3 writes the `release.now` flow as `→ EMIT release` followed by the nested continuation line `TRANSITION "Released"`. The spec allows this form ("any `→` item (lines that continue that item's flow ...)"; FALLBACK equivalence example), so it is sequentially the same.

| Probe | D1 VALID | D2 REQUIRE + FALLBACK(Blocked, STOP) | D3 LOOP: FORK impl‖doc, JOIN, VERIFY, accepted→BREAK, rejected→correction | D4 AUTO HITL:release[now, later] + FALLBACK(Waiting, STOP) | D5 now→EMIT, Released; later→Scheduled |
|---|---|---|---|---|---|
| s1 | met | met | met | met | met |
| s2 | met | met | met | met | met |
| s3 | met | met | met | met | met |
| h1 | met | met | met | met | met |
| h2 | met | met | met | met | met |
| h3 | met | met | met | met | met (`→ EMIT release` / `TRANSITION "Released"` as a nested continuation) |

**Divergence**
- Sonnet: none (byte-identical programs).
- Haiku: h3's nested continuation form is a layout difference with the same meaning. Not material.

**Errors.** None.

**NEW issues**
- spec-gap (V7): V7 does not say whether a HITL name may equal an EMIT artifact name (`HITL:release` and `EMIT release`). s1 flags this. It is harmless, but the spec is silent. (Also raised in X02 s1 and s2.)

**Verdict:** PASS-S yes, PASS-H yes.

---

## ST08 — Stress execution: AUTO without authority

All six probes conclude that the agent lacks authority, so under `AUTO` the human (the finance manager) must be asked. In every trace the HITL waits, the finance manager's "approve" establishes `refund.approve`, then `DELEGATE payout` and `TRANSITION "Refunded"` run, the deny-WHEN is skipped, and the program ends. No probe auto-approves.

The HITL was answered by the human (finance manager) in all six probes, and the agent did not answer in any of them. Final state is `Refunded` in all six.

| Probe | D1 agent lacks authority, so the human is asked | D2 approve → payout, Refunded; deny skipped; final Refunded |
|---|---|---|
| s1 | met: "falls under 'Anything else' ... the human must be asked"; "3. AUTO HITL:refund[...] -> waiting" | met: steps 5–9; "Final state **Refunded**" |
| s2 | met: "the agent must not answer; execution waits at the HITL for a human response" | met: identical trace; "**Refunded**" |
| s3 | met: "the agent MUST NOT answer refund.approve itself; it must wait for the human" | met: identical trace; "**Refunded**" |
| h1 | met: "the human (finance manager) must be asked, not the agent" | met: identical trace; "State: Refunded" |
| h2 | met: "the decision cannot be made automatically—the human (finance manager) must be asked" | met: identical trace; "Refunded" |
| h3 | met: "cannot be answered automatically by the agent ... the human (finance manager) must be asked" | met: identical trace; "Refunded" |

**Divergence:** none in either trio. The nine-line traces are identical.

**Errors.** No D-item errors. One minor issue outside the D-items:
- h3 `OTHER`, model-error. h3 paraphrases the rule as "automatic resolution is permitted only when 'the agent does not have the authority ...' is false". The wording is awkward, but the conclusion is correct.

**NEW issues.** None. The AUTO list item "the agent does not have the authority required to make the decision" and the "Who decides a HITL" table led every probe to the right answer.

**Verdict:** PASS-S yes, PASS-H yes. DANGER: 0.

---

## X01 — Authoring: auto-resolvable decision with fallback

Linter: all six are VALID (lint lines 197–202).

| Probe | D1 VALID | D2 AUTO HITL:merge[a, b]("Merge this change?") + FALLBACK(Blocked, STOP) | D3 a→Merged, b→Rework |
|---|---|---|---|
| s1 | met | met: `[approved, declined]` | met |
| s2 | met | met: `[approved, declined]` | met |
| s3 | met | met: `[approved, declined]` | met |
| h1 | met | met: `[approved, rejected]` | met |
| h2 | met | met: `[approved, declined]` | met |
| h3 | met | met: `[approved, rejected]` | met |

**Divergence**
- Sonnet: none (identical programs).
- Haiku: answer labels differ (`declined` in h2, `rejected` in h1 and h3). The D-items use placeholders `<a>, <b>`, so this is not material.

**Errors.** None.

**NEW issues.** None.

**Verdict:** PASS-S yes, PASS-H yes.

---

## X02 — Authoring: two decisions, only one auto-resolvable

Linter: all six are VALID (lint lines 203–208).

| Probe | D1 VALID | D2 AUTO only on notes; approval without AUTO | D3 each HITL followed by its own WHENs, in order |
|---|---|---|---|
| s1 | met | met: `AUTO HITL:notes[...]` … `HITL:release[approved, rejected]` | met |
| s2 | met | met | met |
| s3 | met | met | met |
| h1 | met | met | met |
| h2 | met | met | met |
| h3 | met | met: `HITL:approval[approved, rejected]` (no AUTO) | met |

**Divergence**
- Sonnet: none (identical programs).
- Haiku: h3 names the approval decision `approval` instead of `release`. The name is arbitrary, so this is not material.

**Errors.** None. No probe put AUTO on the approval HITL (DANGER 0).

**NEW issues.** The V7 silence about HITL names versus EMIT names (see ST07) is raised again by s1 and s2.

**Verdict:** PASS-S yes, PASS-H yes.

---

## Summary table

| ID | PASS-S | PASS-H | sonnet D met | haiku D met | tags | top spec section |
|---|---|---|---|---|---|---|
| ST06 | yes | yes | 12/12 | 12/12 | OTHER×2 (h1 miscitation, h2 "re-executes"; non-D, model-error) | REQUIRE (situation table); TRANSITION (no initial state: spec-gap) |
| ST07 | yes | yes | 15/15 | 15/15 | — | Validity rules V7 (HITL/EMIT name reuse: spec-gap, harmless) |
| ST08 | yes | yes | 6/6 | 6/6 | OTHER×1 (h3 awkward paraphrase; non-D) | AUTO (authority as uncertainty); Who decides a HITL |
| X01 | yes | yes | 9/9 | 9/9 | — | AUTO; FALLBACK |
| X02 | yes | yes | 9/9 | 9/9 | — | AUTO; Who decides a HITL |

```
PART SUMMARY
scenarios: 5
pass_s: 5/5   pass_h: 5/5
d_items_s: 51/51   d_items_h: 51/51
danger_s: 0   danger_h: 0
```
