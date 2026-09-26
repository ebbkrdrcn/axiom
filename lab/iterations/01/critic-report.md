# Iteration 01 — critic report (aggregate)

Spec probed: `iterations/01/DSL.md` (baseline, unchanged `dsl.md`).
Probes: 16 scenarios × 3 blind probes (sonnet) plus 2 confusion probes. Each probe received only one file containing the spec and one task.
Critics: 5 sub-agents (`critic/part-A…E.md`) following `tools/CRITIC.md`.

## Results

| Scenario | Verdict | Probes meeting all D-items | Divergence | Main section implicated |
|---|---|---|---|---|
| S01 AUTO merge decision | **FAIL** | 3/3 | AUTO form (3 different forms); outcome names | AUTO (no syntax), HITL ("surrounding definition"), VERIFY (only VERIFY produces outcomes) |
| S02 verify loop | PASS | 3/3 | none | LOOP (re-entry implicit) |
| S03 parallel reviews | PASS | 3/3 | none | JOIN ("required") |
| S04 REQUIRE + FALLBACK | PASS | 3/3 | none (all used `→` + nested lines, not the canonical form) | FALLBACK form, `→` overloading |
| S05 invalid constructs | PASS | 3/3 | whether a snippet is judged as a complete program (minor) | BREAK, AUTO, Scope |
| S06 no WHEN matches | PASS | 3/3 | none | LOOP re-entry, WHEN no-match (implicit) |
| S07 WAIT | PASS | 3/3 | none | WAIT (event, timeout) |
| S08 REQUIRE unsatisfied | PASS | 3/3 | Q4 "what should the agent do" differs slightly (all marked it as an assumption) | REQUIRE (failure handling) |
| S09 outcome names | **FAIL** | 3/3 | Q2 (is `.passed` established?) and Q4 | VERIFY (no vocabulary), WHEN example (`tests.*` has no source) |
| S10 `→` scope | PASS | 3/3 | none | Scope (nesting under a `→` item), `→` overloading |
| S11 BREAK in FORK in LOOP | **FAIL** | 3/3 | fate of the sibling branch (orphaned / awaited / abandoned); JOIN skipped vs blocking | BREAK × FORK × JOIN |
| S12 HITL fallback | PASS | 3/3 | none | FALLBACK form, "insufficient" |
| S13 AUTO uncertain | PASS | 3/3 | none (all: `AUTO HITL(...)` is not valid, because the spec defines no AUTO syntax) | AUTO syntax, HITL waiting |
| S14 FORK branch fails | PASS | 3/3 | none (all assume WHENs are independent and the last TRANSITION wins) | WHEN exclusivity, TRANSITION overwrite |
| S15 STOP in FORK | PASS | 3/3 | none | STOP scope (stated only in BREAK) |
| S16 TDD loop (baseline) | PASS | 3/3 | none | — |

**Pass rate: 13/16 (81%).** Every failure is a divergence between probes. No probe missed a D-item; there were 2 minor model-errors, neither on a D-item.

**Scenarios without divergence:** 13/16.

## Failure classification

| Class | Count | Where |
|---|---|---|
| spec-gap | 3 failing scenarios, plus about 20 latent gaps that all probes flagged as assumptions | AUTO syntax/binding; outcome vocabulary; BREAK × FORK |
| misleading-wording | 3 | WHEN example `tests.passed` (no source); FALLBACK vs AUTO escalation; REQUIRE "as if" |
| underspecified-syntax | 4 | `→` overloading; FALLBACK multi-`→`; nesting under a `→` item; `<keyword> <argument>` vs argument-less keywords |
| model-error | 2 | S05-p3 (FALLBACK as AUTO escalation; misreads its own BREAK fix), S09-p1 (REQUIRE analogy) |

## Top failure sections

1. **AUTO / HITL.** AUTO has no syntax and no binding to a HITL (S01 fails, S13 unanimous that it is "not valid", S05 has no rewrite).
2. **VERIFY / WHEN.** The outcome vocabulary is undefined, and the WHEN example tests an identifier that nothing establishes (S09 fails; S01 names diverge).
3. **BREAK × FORK × JOIN.** Undefined (S11 fails).
4. **Syntax / Scope / `→`.** Probes converged, but every probe had to argue its way there by analogy (S04, S10, S12).
5. **Implicit execution rules.** Loop re-entry, WHEN no-match and fall-through, WHEN independence, STOP scope, normal termination, TRANSITION overwrite, HITL waiting. Probes converged, but each one flagged these as assumptions.

## Confusion probes (CONF-p1: 17 items, CONF-p2: 14 items)

Every item maps to an existing finding or to one of these new ones:

- F-16 DELEGATE sync vs async
- F-17 TRANSITION overwrite
- F-18 outcome lifetime and visibility
- F-19 normal termination
- F-20 LOOP re-entry and the purpose of the loop name
- F-21 `<keyword> <argument>` contradicts the argument-less keywords
- F-22 program vs fragment
- F-23 REQUIRE scope and duration
- F-24 FALLBACK applicability (HITL only?)

These items are outside the DSL's remit by design (Semantic Principles), so they need no action:

- how DELEGATE selects an actor (CONF-p2 #14)
- a closed vocabulary for TRANSITION states (CONF-p1 #16)
- no ordering constraint between EMIT and VERIFY (CONF-p1 #17, CONF-p2 #13)
