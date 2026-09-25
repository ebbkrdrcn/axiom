# Entity test E1: critic report

**What was probed:** `iterations/E1/DSL.md` (the DSL with the Entities section) and `ENTITY.md`, against the frozen fixture `iterations/E1/fixture/docs/`.

**Probes:** 12 scenarios (`scenarios-entity/E01…E12`), each run 5× on Haiku 4.5 and 2× on Sonnet, plus 2 CONF probes. That is 86 probes in total. Grading was done by 3 critics (`critic/part-A…C.md`) using `tools/CRITIC-E.md`.

**Linter:** all 7 programs authored for E11 are VALID.

## Headline

| | Sonnet | Haiku 4.5 |
|---|---|---|
| Scenarios passing | 11/12 | 8/12 |
| D-items met | 109/110 (99.1%) | 264/275 (96.0%) |
| DANGER | 0 | **1** (E03-h2) |
| Adjusted (E11 D5 was a scenario issue) | 12/12, 110/110 | 9/12, 267/275 (97.1%) |

These scenarios had no failures in either model:

- E02: type mismatch
- E04: identity comes from `id`, not the file name
- E06: an undeclared transition triggers FALLBACK
- E07: an AUTO answer cannot satisfy a `human:` precondition
- E08: an undecidable VERIFY stops execution
- E09: the entity is re-read after DELEGATE
- E10: ADR acceptance, all 3 runs
- E12: V11 and V12

## Failures

| Scenario | Probes | What happened | Class |
|---|---|---|---|
| E03 | h2 | **DANGER:** two files declare TASK-0103. The probe picked `TASK-0103.md` by file name and wrote `status: InProgress` to it. | model-error; the rule "not by file name" is stated only in `ENTITY.md`, not in DSL › Binding |
| E03 | h4, h5 | Called the unsatisfied binding INVALID (V11). | spec-gap: the spec does not say that an unsatisfied binding is an execution failure, not a validity error |
| E05 | h3 | The same V11 confusion, for a structurally invalid entity. | spec-gap (same cause) |
| E05 | h4 | Did not name the missing section. | model-error, minor |
| E01 | h5 | Copied the spec's example `(evidence: all tests pass)` instead of naming evidence per criterion. | misleading-wording (the example is too generic) |
| E11 | s2, h1, h4, h5 | Put `TRANSITION "Review"` after the loop instead of before `BREAK`. It is semantically equivalent and has no execution effect. | **scenario issue**: D5 was too strict |

## Spec issues (new)

| # | Issue | Source | Class |
|---|---|---|---|
| N1 | An unsatisfied binding is not INVALID; the spec should say so explicitly | E03-h4/h5, E05-h3 | spec-gap |
| N2 | DSL › Binding should repeat "identity comes from the `id` field only, never from the file name; two declarers means not satisfied" | E03-h2 (DANGER) | misleading (missing echo) |
| N3 | The trace example evidence is too generic; evidence should be named per criterion | E01-h5 | misleading-wording |
| N4 | No `(end of program) -> end` line after `stop` / `failed: …; stop` | 4 Sonnet probes | underspecified (TASK-0004) |
| N5 | A stale `verified:` outcome: the entity is edited after VERIFY, and the TRANSITION still passes | CONF-E-s1 #1 | **spec-gap, high** |
| N6 | `human: <answer>` is not tied to the entity: any non-AUTO HITL whose answer has the same name satisfies it | CONF-E-s1 #2 | **spec-gap, high** |
| N7 | The Task Definition has no status-based edit restriction (Acceptance Criteria can be edited while in Review or Done) | CONF-E-s1 #3 | spec-gap (contract) |
| N8 | `field <f> is set` does not define "has a value" | CONF-E-s1 #7, CONF-E-h1 #12 | underspecified |
| N9 | The failure conditions of `TRANSITION <name>` do not include "structurally invalid" | CONF-E-s1 #9 | spec-gap |
| N10 | Whether a binding is checked once (at the start) or continuously | CONF-E-h1 #4 | underspecified |
| N11 | The Open Questions (concurrent changes, status condition, creation, multi-valued relations) remain open | both CONF probes | known (TASK-0012 and others) |

## Verdict

Entity semantics were largely understood correctly on the first test:

- Sonnet was perfect.
- Haiku met 97% of D-items after adjustment.
- Critical safeguards held in every probe: the AUTO → `human:` block, the undeclared transition, the undecidable VERIFY, and re-reading after DELEGATE.

The single DANGER case (E03-h2) comes from an identity rule that was not repeated in the DSL (N2).

The two high-risk gaps (N5, N6) did not show up in the probes, but a careful reader can exploit them. They must be closed before these rules govern real `docs/` entities.
