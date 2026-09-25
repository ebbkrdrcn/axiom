# Findings — go_harness DSL.md

Status values: **open** (editor may fix without approval) · **fixed** · **needs-decision** (semantic / keyword / Semantic-Principles change — requires owner approval) · **underdetermined** (spec gives no answer; classification pending)

Section names refer to headings in `DSL.md`.

## Seed findings (verified before iteration 1)

| ID | Seed? | Section | Finding | Verified | Status |
|----|-------|---------|---------|----------|--------|
| F-01 | yes | AUTO | AUTO has no syntax at all. The only code involving AUTO is the *invalid* example (bare `AUTO` line with an indented block). Syntax/Statement `<keyword> <argument>` does not cover it. | **confirmed** | underdetermined |
| F-02 | yes | AUTO, HITL | Binding of AUTO to HITL unspecified: HITL says "unless the surrounding definition explicitly permits automatic resolution through AUTO" — it is unclear whether AUTO attaches to one HITL, to a scope, or to the whole process. | **confirmed** | underdetermined |
| F-03 | yes | WHEN, VERIFY | Condition grammar and outcome vocabulary undefined. WHEN example uses `tests.passed/.failed` (no VERIFY produces `tests`); VERIFY example uses `implementation.accepted/.rejected`. Nothing says which names VERIFY establishes, nor how a HITL response is referenced in a WHEN. | **confirmed** (also extends to HITL responses) | underdetermined |
| F-04 | yes | WHEN, Syntax/Conditional Flow, Syntax/Forked Flow | Scope of multi-line flows after `→`: nested statements under a `→` are defined only for FORK. `→` has three meanings (WHEN: sequential flow; FORK: concurrent branch; under HITL: response handler). End-of-scope rule (dedent) only implied. | **confirmed** | underdetermined |
| F-05 | yes | WHEN, Syntax/Flow | No statement of what happens when no WHEN matches. Inferable from "declaration order" + "flow executed when the condition is satisfied": skip and continue. | **confirmed** (inferable, not explicit) | underdetermined |

## Additional findings from corpus construction (pre-iteration)

| ID | Section | Finding | Status |
|----|---------|---------|--------|
| F-06 | WHEN | Multiple WHENs: independent (all matching run, in order) vs. exclusive (first match) not stated. Also not stated that a WHEN is evaluated once, when reached (vs. a standing trigger). | underdetermined |
| F-07 | HITL | How the HITL response "determines the subsequent flow" is not specified (no name for the response). Overlaps F-03. | underdetermined |
| F-08 | BREAK, FORK, JOIN | BREAK inside a FORK branch inside a LOOP: permitted? Fate of sibling branches and the pending JOIN? | underdetermined |
| F-09 | WAIT | WAIT has no argument: which event it waits for is not expressible; no timeout. | underdetermined |
| F-10 | REQUIRE | Unsatisfied REQUIRE: only "must not proceed as if satisfied". Suspend / terminate / escalate / error not specified; FALLBACK not defined for REQUIRE. | underdetermined |
| F-11 | FALLBACK | When a response becomes "unavailable" (no timeout notion); form of a multi-statement fallback flow; what happens after the fallback flow finishes without STOP (resume after HITL? re-ask?); whether FALLBACK can attach to anything but HITL. | underdetermined |
| F-12 | FORK, JOIN | "corresponding FORK" matching rule; "all required forked flows" — "required" undefined; whether a branch whose VERIFY is negative has "completed"; behaviour of FORK without JOIN only implied. | underdetermined |
| F-13 | Syntax | Grammar incomplete: `HITL("…")`, `LOOP:<name>`, argument-less JOIN/BREAK/WAIT/STOP, `→` lines and conditions are not covered by `<keyword> <argument>`; indentation width unspecified; no EBNF. | open |
| F-14 | BREAK | BREAK outside any LOOP: "may only exit a loop scope" implies invalid but does not say so; nested loops: "current LOOP" = innermost only by implication; LOOP name is never referenced. | open |
| F-15 | STOP, FORK | STOP inside a concurrent branch: "entire execution" (stated only in BREAK) implies all branches stop; not stated in STOP. | open |
