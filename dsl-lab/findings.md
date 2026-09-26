# Findings: go_harness DSL (`dsl.md`)

Status values:

- **open**: the editor may fix it without approval.
- **fixed**: resolved in the spec. The iteration that fixed it is noted.
- **needs-decision**: the fix changes semantics, adds or renames a keyword or syntax, or touches the Semantic Principles. It needs owner approval; see Decision points.
- **underdetermined**: the spec gives no answer, and the finding is not yet classified.
- **wontfix**: outside the DSL's remit by design (Semantic Principles).

Section names refer to headings in `dsl.md`.

## Findings

| ID | Seed | Section | Finding | Evidence (it01) | Status |
|----|------|---------|---------|-----------------|--------|
| F-01 | yes | AUTO | AUTO has no syntax. The only code involving AUTO is the *invalid* example. | **Confirmed.** In S01 the 3 probes wrote 3 different forms: `HITL → AUTO`, `AUTO merge-decision` before the HITL, and a bare `AUTO` before the HITL. All 3 S13 probes judged `AUTO HITL(...)` invalid. | needs-decision → **DP-1** |
| F-02 | yes | AUTO, HITL | The binding of AUTO to HITL is unspecified ("surrounding definition … through AUTO"). | **Confirmed** (S01, S05). The probes also disagreed on the scope of a standalone AUTO: the next HITL only, or everything after it. | needs-decision → **DP-1** |
| F-03 | yes | WHEN, VERIFY | Outcome names are not defined. The WHEN example uses `tests.passed/failed`, which nothing establishes; the VERIFY example uses `.accepted/.rejected`. | **Confirmed.** S09 fails: p1 says `implementation.passed` is not established, while p2 and p3 treat it as a synonym of accepted. In S01 the outcome names diverge. | needs-decision → **DP-2** |
| F-04 | yes | WHEN, Syntax | The scope of multi-line flows after `→` is ambiguous, and `→` is overloaded (sequential under WHEN, concurrent under FORK, attachment under HITL). | **Confirmed as underspecified-syntax.** Probes converged (S04, S10, S12), but every one argued its way there by analogy. The Scope rule only covers "scoped constructs". | **fixed (it01)**: Syntax/Scope indentation rules, the "The arrow `→`" table, Conditional Flow example, EBNF |
| F-05 | yes | WHEN, Flow | Nothing says what happens when no WHEN matches. | **Confirmed as implicit.** All S06 probes inferred skip-and-continue and flagged it. | **fixed (it01)**: WHEN execution rules |
| F-06 | — | WHEN | Multiple WHENs: independent or first-match? Evaluated once, or a standing trigger? | S14 probes converged on independent, but all flagged it. The WHEN example invites an if/elif reading. | **fixed (it01)**: an implicit rule stated explicitly (statements run in declaration order; nothing states exclusivity). *Owner: confirm this is the intended semantics.* |
| F-07 | — | HITL | How a HITL response determines the next flow, and how WHEN refers to it. | S01 and S13 probes invent `merge.approved` etc. The spec never says HITL produces outcomes. | needs-decision → **DP-3** |
| F-08 | — | BREAK, FORK, JOIN | BREAK inside a FORK branch inside a LOOP. | **S11 fails.** The sibling branch is orphaned (p1), awaited through JOIN (p2), or abandoned (p3). | needs-decision → **DP-5** |
| F-09 | — | WAIT | WAIT has no argument and no timeout. | S07 converged. | **fixed (it01)**: WAIT clarifications (the event is runtime-defined; stays suspended; next statement). Whether a timeout can be expressed → **DP-8** |
| F-10 | — | REQUIRE | What an unsatisfied REQUIRE does: suspend, terminate, or escalate? "Must not proceed *as if* satisfied" invites a degraded-mode reading. | S08 converged on D1–D3; Q4 varied. | wording **fixed (it01)**; behaviour → **DP-4** |
| F-11 | — | FALLBACK | The multi-statement fallback form; the meaning of "unavailable" and "insufficient"; what happens after a fallback flow without STOP. | S04 and S12 converged, but by analogy. | form and triggers **fixed (it01)**; after-fallback → **DP-6** |
| F-12 | — | FORK, JOIN | The meaning of "corresponding FORK" and "required"; whether a rejected branch counts as completed; FORK without JOIN. | S03 and S14 converged, but flagged it. | **fixed (it01)**: FORK and JOIN execution rules |
| F-13 | — | Syntax | The grammar is incomplete: `<keyword> <argument>` does not cover argument-less keywords, `HITL(...)`, `LOOP:`, or conditions. | CONF-p1 #1, CONF-p2 #8/#10. | **fixed (it01)**: Statement table and EBNF |
| F-14 | — | BREAK, LOOP | BREAK outside a LOOP; nested loops; the unused LOOP name. | S05 converged. CONF-p1 #5, CONF-p2 #5. | **fixed (it01)**: BREAK rules, LOOP rules |
| F-15 | — | STOP | STOP inside a concurrent branch. "Entire execution" was stated only under BREAK. | S15 converged by contrast. | **fixed (it01)**: STOP section |
| F-16 | — | DELEGATE, Flow | Is DELEGATE synchronous (the next statement waits for the delivered result) or fire-and-forget? | S12/S16 probes; CONF-p1 #7. | needs-decision → **DP-7** |
| F-17 | — | TRANSITION | Two TRANSITIONs in one pass: overwrite or conflict? | S14 (all 3 assumed last-write-wins). CONF-p2 #12. | **fixed (it01)**: "exactly one current state" is an implicit rule stated explicitly (the spec already says "the current process state") |
| F-18 | — | VERIFY, FORK | Outcome lifetime (per iteration? overwritten?) and visibility after JOIN. | S14, S16. | visibility after JOIN **fixed (it01)**; lifetime → part of **DP-2** |
| F-19 | — | STOP, Flow | Normal termination without STOP. | S12, S14, S16. | **fixed (it01)**: STOP section |
| F-20 | — | LOOP | Loop re-entry at the end of the body; "another explicit control flow". | S02, S06, S16 (every probe). | **fixed (it01)**: LOOP execution rules |
| F-21 | — | Syntax/Statement | The generic `<keyword> <argument>` form contradicts JOIN/BREAK/WAIT/STOP. | CONF-p1 #1. | **fixed (it01)**: Statement table |
| F-22 | — | Scope | Is a snippet judged as a complete program, or may it sit inside an unseen scope? What does "invalid" mean? | S05 (p1 and p2 hedge). | **fixed (it01)**: "Programs, fragments, and validity". *Owner: confirm that "reject as a whole" is intended.* |
| F-23 | — | REQUIRE | REQUIRE scope and duration: checked once, or continuously? | CONF-p2 #9. | underdetermined; folded into **DP-4** |
| F-24 | — | FALLBACK | Is FALLBACK HITL-only, or can it attach to WAIT or REQUIRE? | S07, S08 (every probe asked). | needs-decision → part of **DP-4 / DP-8** |
| F-25 | — | VERIFY | A VERIFY with no WHEN: does it gate the flow? | S01, S03. | **fixed (it01)**: VERIFY "does not branch by itself" |
| F-26 | — | HITL | Does the flow wait at a HITL? What follows a usable response? | S12, S13. CONF-p1 #8. | **fixed (it01)**: HITL waiting sentence |
| F-27 | — | AUTO, FALLBACK | AUTO's escalation to a human is confused with FALLBACK. | S05-p3 (misleading-wording). | **fixed (it01)**: AUTO note |
| F-28 | — | DELEGATE | Actor selection; closed TRANSITION vocabulary; EMIT allowed before VERIFY. | CONF-p2 #13/#14, CONF-p1 #16/#17. | wontfix (runtime-independent by design) |
| F-29 | — | HITL, FALLBACK | A HITL **without** FALLBACK whose response is unavailable or insufficient: suspend indefinitely, or invalid? | AUTO experiment: flagged in X06 in all variants; every probe assumed suspension. | needs-decision (joins **DP-6**) |
| F-30 | — | HITL (provisional DP-3 A) | The scope of "the WHEN constructs that follow", which defines a HITL's answer set. | AUTO experiment: all 4 CONF probes. | open; depends on **DP-3** |
| F-31 | — | HITL, FALLBACK | Two definitions of "insufficient": the answer matches no tested answer, vs. the response does not provide the requested decision. | A-CONF #2. | open; depends on **DP-3** |
| F-32 | — | AUTO | Must an AUTO answer be one of the tested answers? "protocol-compatible" is undefined. | All 4 CONF probes. | open (wording) |
| F-33 | — | VERIFY, HITL | Outcome lifetime, overwriting and name reuse (loops, repeated HITL names). | B-, C- and D-CONF. | part of **DP-2** |
| F-34 | — | FALLBACK | Flow after a FALLBACK flow that does not stop. | All 4 CONF probes. | **DP-6** |
| F-35 | — | HITL | A response that matches more than one tested answer. | B-CONF #8. | open; depends on **DP-3** |
| F-36 | — | HITL | Mapping a paraphrased or feedback-laden response ("Not like this, rewrite the intro.") to a listed answer. | T2 S12: Haiku 3/3 → insufficient; Sonnet 3/3 flag it | open (spec-gap) → TASK-0001 |
| F-37 | — | AUTO | The defining sentence "when it is sufficiently determined" omits authority. | T2 X06-h1 | open (misleading-wording) → TASK-0002 |
| F-38 | — | WHEN, LOOP | "continue after the `WHEN`" is read as the next text line when a WHEN ends a LOOP body. | T2 S20-h2 | open (misleading-wording) → TASK-0003 |
| F-39 | — | Trace | No rule for the first LOOP entry in a trace (example only). | T2 ST01-h3, S20 Sonnet | open → TASK-0004 |
| F-40 | — | Trace | No line form for an AUTO HITL answered by the agent. | T2 ST01 (all inferred) | open → TASK-0004 |
| F-41 | — | Trace | No effect for "ends because REQUIRE/HITL failed with no FALLBACK"; `end` added after `stop`. | T2 S08, ST04-h1, ST06-s1, S12-h3 | open → TASK-0004 |
| F-42 | — | Validity | A line matching no statement form (e.g. `BREAK release`) has no rule number. | T2 S20 Sonnet ×3 | open → TASK-0005 |
| F-43 | — | Examples | `invalid` examples do not name the rules they break. | T2 S05 | open → TASK-0005 |
| F-44 | — | TRANSITION | State before the first TRANSITION is undefined. | T2 ST06, S09, S10 | **fixed (entity integration)**: process state is `none` before the first TRANSITION |
| F-45 | — | DELEGATE, VERIFY | The `VERIFY x` ↔ `DELEGATE x` name link is shown only in examples. | T2 ST05/ST06 | open → TASK-0008 |
| F-46 | — | HITL | When the runtime stops waiting (unavailable) is not stated as runtime-defined. | T2 S13 Sonnet ×3 | open → TASK-0008 |
| F-47 | — | Names | May a HITL name equal an EMIT artifact name? | T2 ST07, X02 | open (harmless) → TASK-0008 |
| F-48 | — | WHEN | Rule 7 wording: an established other outcome also makes WHEN false. | T2 S06-h1, S10-h3 | open → TASK-0003 |
| F-49 | — | Execution protocol | The validity verdict is not required to appear before the trace. | T2 S21 | open → TASK-0004 |
| F-50 | — | FORK, BREAK, V3 | **Contradiction:** the FORK table says any `BREAK` in a branch is INVALID, while BREAK/V3 allow a BREAK that leaves a LOOP nested inside the same branch. | T2 CONF-s1 #1 | open (contradiction) → TASK-0006 |
| F-51 | — | V10 | V10 is static (text order) but its wording and the Outcomes rationale suggest a dynamic reading; a FORK with no JOIN makes its outcomes untestable forever. | T2 CONF-s1 #2 | open → TASK-0007 |
| F-52 | — | Entities › Binding | An unsatisfied binding is an execution failure, not INVALID; this is not stated explicitly. | E1: E03-h4/h5, E05-h3 | open → v3 |
| F-53 | — | Entities › Binding | The DSL does not repeat "identity only from `id`, never from the file name". | E1: E03-h2 (DANGER) | open → v3 |
| F-54 | — | Trace | The evidence example is too generic; evidence should be named per criterion. | E1: E01-h5 | open → TASK-0004 |
| F-55 | — | Preconditions | A stale `verified:` outcome: the entity is edited after VERIFY and the TRANSITION still passes. | E1: CONF-E-s1 #1 | open (high) → v3 |
| F-56 | — | Preconditions | `human: <answer>` is not tied to the entity or transition being decided. | E1: CONF-E-s1 #2 | open (high) → v3 |
| F-57 | — | Task Definition | No status-based restriction on edits by delegated work. | E1: CONF-E-s1 #3 | open → contract |
| F-58 | — | Preconditions | `field <f> is set`: "has a value" is undefined. | E1: CONF-E ×2 | open → v3 |
| F-59 | — | Entities › TRANSITION | Failure conditions omit "entity no longer structurally valid". | E1: CONF-E-s1 #9 | open → v3 |
| F-60 | — | Entities › Binding | A binding is checked once or continuously: not stated. | E1: CONF-E-h1 #4 | open → v3 |
| F-61 | — | Entities › Binding | The v3 identity rule ("two declarers → not satisfied") is declarative; Haiku still binds one of two files with the same id (DANGER, repeated from E1). | Test 3: E03-h2 | open → v4 (make procedural: list and count files) |
| F-62 | — | Entities › Preconditions | `verified:` expiry after a data change is stated once; Haiku ignores it and transitions (DANGER ×2). | Test 3: N06-h4, N06-h5 | open → v4 (procedural check + example) |
| F-63 | — | FALLBACK (authoring) | No rule limits what an authored FALLBACK may do; Haiku adds unrequested FALLBACKs, one of which moves an entity on a non-answer. | Test 3: E11-h2, N09-h5, S01-h5 | open → v4 (authoring rule) |

---

## Decision points (need owner approval)

Each decision point lists options; the recommended option comes first.

### DP-1: AUTO syntax and binding to HITL (F-01, F-02)

> **Experiment result** (`experiments/auto-syntax/report.md`): with the syntax fully documented, variants A, B, C and D all scored 6/6 with 0 errors and 0 hesitations. The placement is not decisive; the documentation is. Choosing among them needs a stress test (cold reading, a weaker model, harder programs) or design criteria.

- **A (recommended). Prefix modifier on one HITL: `AUTO HITL("Merge this change?")`.** AUTO applies only to that HITL. The agent resolves the decision itself when it is sufficiently determined; otherwise the HITL is asked normally, and the HITL's FALLBACK (if any) still applies to the human's response. This is local and explicit, it reads naturally, and all S13 probes understood the intent even while calling the form invalid.
- B. Modifier line under the HITL, like FALLBACK: `HITL("…")` followed by an indented `→ AUTO`. This is what S01-p1 wrote. It mixes AUTO into the `→` arrow system.
- C. A standalone `AUTO` statement on the line before the HITL. Two S01 probes did this. Its scope is ambiguous: the next HITL, or all following ones?
- D. A scope-level AUTO that covers every HITL in the enclosing block. This is broad and risks silently authorizing decisions.

### DP-2: Outcome vocabulary of VERIFY and form of conditions (F-03, F-18)

- **A (recommended). Closed vocabulary.** `VERIFY x` establishes exactly one of `x.accepted` or `x.rejected`. The WHEN example changes from `tests.passed/failed` to `tests.accepted/rejected` and gains a preceding `VERIFY tests`. A WHEN whose subject no statement can establish is invalid. A later `VERIFY x` replaces the earlier outcome. A WHEN evaluated before any `VERIFY x` is simply unsatisfied.
- B. Closed vocabulary with aliases: `passed` = `accepted`, `failed` = `rejected`.
- C. Open vocabulary: outcome names are process-defined and the runtime maps results to them. This keeps the current examples as they are, but S09 shows that agents then cannot tell whether a condition is valid.

### DP-3: How WHEN refers to a HITL (or AUTO) decision (F-07)

- **A (recommended). Name the decision like a loop: `HITL:merge("Merge this change?")`.** Following WHENs test `merge.<answer>`, where the answers are the words the author uses in those WHENs (for example `merge.approved` and `merge.declined`). A response that maps to none of those answers is *insufficient*, which triggers the FALLBACK. This ties neatly into the existing FALLBACK semantics. It adds syntax (`HITL:<name>`).
- B. The same named form, but with a closed answer vocabulary: `<name>.approved` / `<name>.rejected`.
- C. No reference. A HITL only gates (continue or fallback), and branching on the answer is not expressible.

### DP-4: Unsatisfied REQUIRE (F-10, F-23, F-24)

- **A (recommended). Allow `→ FALLBACK` under REQUIRE.** When the requirement cannot be satisfied, the fallback flow runs. Without a FALLBACK, execution halts at the REQUIRE: nothing after it runs, and the runtime reports the unmet requirement. This is not a success, and the agent does not guess.
- B. The requirement is always a suspension: execution waits at REQUIRE until the requirement is satisfied, like WAIT.
- C. It always terminates, like STOP.
- D. It implicitly escalates to a human, like an implicit HITL.

Also to confirm: REQUIRE is checked when it is reached, not continuously afterwards.

### DP-5: BREAK inside a FORK branch (F-08)

- **A (recommended). Invalid.** `BREAK` must not appear inside a FORK branch, because a branch cannot exit an enclosing loop. Authors instead JOIN and then branch on the outcomes: `JOIN` / `WHEN security-review.rejected → BREAK`. This is simple and has no cancellation semantics.
- B. BREAK cancels the sibling branches immediately and exits the loop. JOIN is skipped.
- C. BREAK marks the loop for exit. The sibling branches run to completion, the pending JOIN is satisfied, and then the loop exits (TRANSITION "Reviewed" is skipped).

### DP-6: After a FALLBACK flow that does not STOP (F-11)

- **A (recommended). Continue with the statement after the HITL construct.** Nothing was decided, so any WHEN on the decision (see DP-3) is unsatisfied. This is consistent with "the fallback does not invent a decision".
- B. The fallback flow must end with STOP, BREAK, or WAIT; anything else is invalid.
- C. Ask the HITL again after the fallback flow.

### DP-7: DELEGATE completion (F-16)

- **A (recommended). A DELEGATE completes when the actor has delivered its result.** The next statement waits for it; use FORK for concurrent delegation. This matches every probe's reading of `DELEGATE x` / `VERIFY x`.
- B. A DELEGATE completes when the work has been assigned. A later `VERIFY x` waits for the result.

### DP-8: Timeouts and fallback for WAIT (F-09, F-24)

- **A (recommended). Keep WAIT argument-less and without a timeout.** A timeout is a runtime policy, which fits the Semantic Principles. FALLBACK stays HITL-only (plus REQUIRE if DP-4 A is chosen).
- B. Allow `WAIT` followed by an indented `→ FALLBACK` block.
- C. Add a `WAIT <event>` argument.

### Confirmations of applied clarifications (veto if wrong)

- F-06: consecutive WHENs are independent. Every satisfied WHEN runs; there is no else.
- F-22: a program containing an invalid construct is rejected as a whole.
- F-17: the most recent TRANSITION wins.
