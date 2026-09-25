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
