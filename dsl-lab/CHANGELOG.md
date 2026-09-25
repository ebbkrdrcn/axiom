# CHANGELOG — dsl-lab / DSL.md

## Iteration 0 — setup (2026-09-25)
- Created `dsl-lab/` with a 16-scenario corpus (4 authoring, 6 interpretation, 6 execution-trace).
- Verified the 4 seed findings (all confirmed; F-05 is inferable but not explicit) and logged F-06…F-15.
- DSL.md unchanged.

## Iteration 1 (2026-09-25)
Protocol: 16 scenarios × 3 blind probes (sonnet) and 2 confusion probes. Each probe got one file containing only the spec text and one task. 5 critic sub-agents, merged in `iterations/01/critic-report.md`. The earlier partial probe outputs (S01–S05, unknown protocol) were discarded and re-run.
- **Pass rate: 13/16 (81%).** Failures: S01 (AUTO form), S09 (outcome names), S11 (BREAK in FORK). All were probe divergences; no probe missed a D-item.
- **Top failing sections:** AUTO/HITL, VERIFY/WHEN outcome names, BREAK×FORK×JOIN.
- **Spec edits (allowed class: clarifications, examples, grammar, explicit implicit rules)** — diff in `iterations/01/diff.patch`:
  - LOOP: execution rules (re-entry, BREAK/STOP effect, name is a label) plus an example.
  - WHEN: evaluation rules (evaluated once, no-match skips, independent WHENs, one sequential flow).
  - FORK: branch completion, FORK without JOIN, STOP in a branch.
  - JOIN: pairing rule, "required" = all branches, completion, outcome visibility, example.
  - BREAK: innermost loop, immediate effect, invalid outside a LOOP, invalid example.
  - WAIT: event is runtime-defined, next statement, no timeout.
  - STOP: entire execution including branches; normal end without STOP.
  - REQUIRE: strict reading of "not as if satisfied".
  - VERIFY: does not branch by itself.
  - TRANSITION: single current state, last wins.
  - HITL: flow waits at the HITL.
  - AUTO: AUTO escalation is not FALLBACK.
  - FALLBACK: unavailable/insufficient defined; two equivalent multi-statement forms; the normal flow is separate.
  - Syntax: statement-form table, indentation rules, `→` meaning table, nested-flow example, condition form, identifier charset, programs/fragments/validity, EBNF.
- **Findings:** 5 seeds verified (F-01…F-05 confirmed); F-16…F-28 added; 8 decision points (DP-1…DP-8) raised.
- **Corpus:** added S17–S21 (pass/fail outcome names, FORK without JOIN / DELEGATE completion, fallback without STOP, nested loops, WHEN before its outcome exists). Adjusted S04, S07, S09 and S14 per critic scenario issues.
- **Stopped for owner decisions DP-1…DP-8** before iteration 2.

## DSL v2 (2026-09-25, owner delegated all decisions)
Full rewrite of `dsl.md`. The v2 design resolves DP-1…DP-8:
- decision HITL `HITL:<name>[a, b]("q")` with declared answers
- `AUTO` as a same-line prefix
- VERIFY outcomes closed to accepted/rejected
- FALLBACK must end with STOP/BREAK (V8), and a missing FALLBACK ends execution
- REQUIRE may take a FALLBACK
- BREAK in a FORK branch is invalid (V3)
- DELEGATE completes on delivery
- the response-timing rule
- validity rules V1–V10, EBNF, the execution protocol and trace format, and a complete example with its trace

Also added the deterministic checker `tools/dslcheck.py` (all spec blocks pass) and `tools/lint_outputs.py`. The corpus was rebuilt (35 scenarios; v1 corpus moved to `scenarios-v1/`).

## Test 2 (2026-09-25)
Protocol: 35 scenarios × (3 Sonnet + 3 Haiku 4.5) blind probes and 2 CONF probes; 7 critics. Report: `iterations/02/critic-report.md`.
- **Sonnet:** 34/35 scenarios, 341/342 D-items.
- **Haiku:** 29/35 scenarios, 331/342 D-items (98.2% after scenario-wording issues are removed).
- **DANGER:** 0 across 210 probes. Linter: every authored program VALID.
- **Failures:**
  - S05 and S21: scenario wording.
  - S12 (Haiku): answer mapping, spec-gap F-36.
  - X06 (Haiku): AUTO sentence, F-37.
  - S20 (Haiku): loop scope, F-38.
  - S10 (Haiku): model error.
- **New findings:** F-36…F-49.
- The spec is unchanged in this test; v3 edits await owner approval.

## Entity model integration (2026-09-25, owner-approved)
- **Decisions:**
  - VERIFY outcomes stay `accepted`/`rejected`; Definitions give criteria and evidence only.
  - Every failure runs its FALLBACK or ends execution as with STOP; bindings have no FALLBACK.
  - Terms: process *state* vs entity *status*/*data*.
  - Human approval is a precondition `human: <answer>` that only a non-AUTO HITL can satisfy.
- **`dsl.md`:**
  - New **Entities** section: binding, `VERIFY <name>`, `TRANSITION <name> "<status>"`, the precondition forms and a Failures table.
  - FALLBACK is allowed under VERIFY and entity TRANSITION.
  - A VERIFY that cannot determine one outcome now fails; this applies to every VERIFY.
  - The process state is `none` before the first TRANSITION.
  - New rules V11 and V12, updated EBNF, execution rules 11–12, and new trace effects (`bound`, `status`, `failed: …; fallback|stop`).
- **`entity-model.md`:** aligned with the decisions (State → Data, closed outcomes, failure behaviour, precondition forms, V11/V12 references).
- **`docs/types/`:** Task and ADR contracts (`template.md`, `definition.md`, `representation.md`).
- **`tools/dslcheck.py`:** parses bindings and entity TRANSITION, allows FALLBACK under VERIFY and entity TRANSITION, and checks V11/V12. All `dsl.md` examples pass, and lint results on the Test 2 outputs are unchanged.

## Project docs as entities (2026-09-25, owner-approved)
- `docs/adr/`: ADR-0001…ADR-0014, all `Proposed`. They record the decisions so far: model as interpreter, Haiku minimum, decision HITL, AUTO prefix, closed VERIFY outcomes, the failure rule, BREAK×FORK, DELEGATE completion, WAIT, the Entity Model, DSL entity integration, terminology, the undecidable VERIFY, and the test method.
- `docs/tasks/`: TASK-0001…TASK-0012, all `Todo`. They cover findings F-36…F-51, scenario fixes, the entity test, Test 3 and status conditions. `findings.md` links each finding to its task.
- `tools/entitycheck.py`: checks entity files against their Template (fields, id format, declared status, required sections, duplicate ids). All 26 files are VALID.

## Entity test E1 (2026-09-25)
Protocol: 12 entity scenarios × (5 Haiku + 2 Sonnet) against a frozen fixture, plus 2 CONF probes; 3 critics. Report: `iterations/E1/critic-report.md`.
- **Sonnet:** 11/12 scenarios, 109/110 D-items; 12/12 after the scenario fix.
- **Haiku:** 8/12 scenarios, 264/275 D-items; 97.1% adjusted. **1 DANGER** (E03-h2: resolved a duplicate identity by file name and changed the file).
- **Held in every probe:** AUTO cannot satisfy `human:`; undeclared transition → FALLBACK; undecidable VERIFY → stop; re-read after DELEGATE; ADR acceptance flow.
- **New findings:** F-52…F-60. Two are high risk (F-55 stale `verified:`, F-56 `human:` not tied to the entity).
