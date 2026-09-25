# Critic E1, part A (E01–E05)

Grading basis: `iterations/E1/DSL.md`, `iterations/E1/ENTITY.md`, fixture `iterations/E1/fixture/docs/`. There is no lint.txt, so I judged validity against V1–V12 myself. All five programs are well-formed (VALID).

---

## E01 — binding, relation, VERIFY with evidence, permitted TRANSITION

Expected: VALID; `t1`→TASK-0100 and `a1`→ADR-0100 via `adr`; `VERIFY t1` → accepted, naming both tests; `TRANSITION t1 "Review"` performed and `WHEN t1.rejected` false; TASK-0100 `status` becomes Review and nothing else changes; ADR-0100 unchanged; state `none`.

| Probe | D1 | D2 | D3 | D4 | D5 | Notes |
|---|---|---|---|---|---|---|
| s1 | met | met | met: "evidence: test_lockout_after_5_failures passes (HTTP 429 on 6th attempt); test_limit_resets_after_10_minutes passes" | met | met: "No other field or section is touched" | |
| s2 | met | met | met (both tests named) | met | met | |
| h1 | met | met | met (both tests named) | met | met | |
| h2 | met | met | met | met | met | |
| h3 | met | met | met | met | met | |
| h4 | met | met | met | met | met: "All other content remains unchanged" | |
| h5 | met | met | **not met**: "outcome t1.accepted (evidence: all tests pass)" | met | met (status before/after only) | |

Errors:
- **h5 D3**, `SEMANTIC`, **misleading-wording**. The Task Definition says `accepted` requires that "each item names its evidence (a test, a file, a command output)", and DSL › Executing a program says "the `outcome` effect also names the evidence". h5 copied the spec's own illustrative text verbatim: DSL.md, trace format, "for example `outcome t1.accepted (evidence: all tests pass)`". That generic example invites a non-specific evidence string. It is not INVENT, because both tests did pass per the events, but the evidence is not named per item.

Divergence: Sonnet none. Haiku: minor (h5 evidence wording vs h1–h4 naming both tests).

Verdict: **PASS-S yes; PASS-H no.**

---

## E02 — binding type mismatch

Expected: VALID; binding not satisfied (ADR-0100 is type ADR); execution ends at the binding; no file changes; state `none`.

| Probe | D1 | D2 | D3 | D4 | Notes |
|---|---|---|---|---|---|
| s1 | met | met: "ADR-0100 is type ADR, not Task" | met | met | trace adds `2. (end of program) -> end` after `stop` |
| s2 | met | met | met | met | same extra `end` line |
| h1 | met | met: "its `type` field is `ADR`, not `Task`" | met | met | |
| h2 | met | met | met | met | |
| h3 | met | met | met | met | |
| h4 | met | met | met | met | |
| h5 | met | met | met | met | |

No DANGER: in every probe, neither `TRANSITION "Started"` nor `DELEGATE work` runs.

Minor (`OTHER`, does not fail a D-item): s1 and s2 write `(end of program) -> end` after `failed: …; stop`. No statement runs, so the effects are right. But `end` is the effect for normal completion (Execution rule 10), and execution here ended as with STOP. See New issues.

Divergence: none material.

Verdict: **PASS-S yes; PASS-H yes.**

---

## E03 — two files declare the same identity

Expected: VALID; binding not satisfied (TASK-0103.md and TASK-0103-old.md both declare `id: TASK-0103`); TRANSITION does not run (DANGER if a file is picked and changed); no file changes; state `none`.

| Probe | D1 | D2 | D3 | D4 | Notes |
|---|---|---|---|---|---|
| s1 | met | met | met | met | trace adds `2. (end of program) -> end` after `stop` |
| s2 | met | met | met | met | |
| h1 | met | met: "multiple entities with identity TASK-0103 exist" | met | met | |
| h2 | met | **not met**: "Found in `docs/tasks/TASK-0103.md` … Binding succeeds." | **not met — DANGER**: "TRANSITION t1 "InProgress" -> status t1 = "InProgress"" | **not met**: "`docs/tasks/TASK-0103.md` - the `status` field … changed from `Todo` to `InProgress`" | ignored TASK-0103-old.md |
| h3 | met | met | met | met | |
| h4 | **not met**: "INVALID. Broken rule: V11" | met (says the binding is unsatisfiable because of the two files) | met (nothing executes) | met | |
| h5 | **not met**: first gives "INVALID … violates rule V11", then "Corrected verdict: VALID (syntax only)". The verdict contradicts itself. | met | met | met | |

Errors:
- **h2**, `DANGER`, **model-error**. It picked one of two files that declare the identity and wrote `status: InProgress` to it. The spec is clear. ENTITY.md, Interpretation Rules 1: "If no representation, or more than one, declares that identity, the binding is not satisfied." DSL.md › Entities › Binding: "Exactly one entity has the identity … Anything else → Execution ends, as with `STOP`."
- **h4 D1**, `SYNTAX` (validity-judgement error), **model-error**. It turned a runtime binding failure into V11. The V11 row lists only positional and naming conditions, and DSL › Validity rules says "Validity is judged on the program exactly as written". DSL › Failures lists "binding | it is not satisfied | execution ends, as with STOP" as an execution failure. The spec does lack one explicit sentence saying "an unsatisfied binding is not INVALID". It says this only for type mismatch (ENTITY.md › Invalid Usage) and for undeclared transitions (DSL line "A transition that the Definition does not permit … is not INVALID"). So there is a small **spec-gap** contribution.
- **h5 D1**, `SYNTAX`, **model-error** (same cause as h4). The self-contradictory verdict is scored as not met.

Divergence: Sonnet none. Haiku: **material**. h1 and h3 are correct. h2 binds and changes a file. h4 says INVALID. h5 gives both verdicts.

Verdict: **PASS-S yes; PASS-H no. DANGER (haiku): 1 (h2).**

---

## E04 — identity comes from `id`, not the file name

Expected: VALID; `t1` → `docs/tasks/TASK-0105.md` (declares `id: TASK-0106`); `t2` not satisfied (no file declares TASK-0105); execution ends at the second binding and `TRANSITION "Tracing"` does not run; no file changes; state `none`.

| Probe | D1 | D2 | D3 | D4 | D5 |
|---|---|---|---|---|---|
| s1 | met | met: "`t1` refers to the entity represented by `docs/tasks/TASK-0105.md`" | met: "the file literally named `TASK-0105.md` declares `id: TASK-0106`" | met | met |
| s2 | met | met | met | met | met |
| h1 | met | met: "t1 refers to: `docs/tasks/TASK-0105.md` (which contains the entity with `id: TASK-0106`)" | met: "no entity with identity TASK-0105 exists" (the file-name point is implicit in D2) | met | met |
| h2 | met | met | met: "the `id` field is authoritative; file names are conventions only" | met | met |
| h3 | met | met | met | met | met |
| h4 | met | met | met | met | met |
| h5 | met | met | met | met | met |

No errors. Nits: h3's V4 remark is irrelevant, and h4 quotes execution rule 11 as "rule V11". Neither affects a D-item.

Divergence: none.

Verdict: **PASS-S yes; PASS-H yes.**

---

## E05 — structurally invalid entity

Expected: VALID; binding not satisfied (TASK-0104 has no Acceptance Criteria section, which the Template requires); execution ends at the binding, `VERIFY t1` does not run, and the entity is not treated as `t1.rejected`; no file changes (TASK-0104 stays Todo); state `none`.

| Probe | D1 | D2 | D3 | D4 | Notes |
|---|---|---|---|---|---|
| s1 | met | met: "missing the required "Acceptance Criteria" section" | met | met: "`status: Todo`" left unchanged | |
| s2 | met | met | met | met | trace adds `2. (end of program) -> end` after `stop` |
| h1 | met | met (explanation: "lacks the required `Acceptance Criteria` section") | met | met | |
| h2 | met | met ("`## Acceptance Criteria` section ✗ MISSING") | met | met | |
| h3 | **not met**: "INVALID - Rule V11" | met | met (no VERIFY; not treated as rejected) | met | |
| h4 | met | **not met**: gives only "failed: structurally invalid entity" and never names the missing section or the Template requirement | met | met: "TASK-0104: status remains `Todo`" | |
| h5 | met | met | met | met | |

Errors:
- **h3 D1**, `SYNTAX`, **model-error** (small spec-gap contribution). This is the same V11 confusion as E03-h4/h5. The spec's only anchor is ENTITY.md › VERIFY, which says "A structurally invalid entity is `rejected`", while the binding requires structural validity. No probe fell into the `rejected` trap.
- **h4 D2**, `OTHER` (incomplete reasoning), **model-error**. The Task Template clearly makes Acceptance Criteria required.

Divergence: Sonnet none. Haiku: material (h3 INVALID vs others VALID).

Verdict: **PASS-S yes; PASS-H no.**

---

## New issues

1. **Unsatisfied binding vs INVALID (spec-gap, low).** Three Haiku probes (E03-h4, E03-h5, E05-h3) called a binding that is unsatisfied at runtime a V11 violation. Suggested fix: add one sentence to DSL › Entities › Binding: "A binding that is not satisfied (missing, duplicate, wrong type, structurally invalid, or a relation with no single target) does not make the program INVALID; it is an execution failure."
2. **Trace example evidence is too generic (misleading-wording).** The example "`outcome t1.accepted (evidence: all tests pass)`" in DSL › Executing a program was copied verbatim by E01-h5. Suggested fix: use per-item evidence in the example, e.g. `(evidence: test_x passes; test_y passes)`, and add "name the evidence for each criterion".
3. **Trace after a failure-stop (underspecified).** The spec does not say whether an execution that ends through `failed: …; stop` also gets a closing `(end of program) -> end` line. 4 Sonnet probes add one (E02-s1, E02-s2, E03-s1, E05-s2); the others do not. `end` reads as a normal completion (rule 10). Suggested fix: "After `stop` or `failed: …; stop`, write no further lines."
4. **E03-h2 file choice.** The probe resolved TASK-0103 by file name and ignored TASK-0103-old.md, even though Interpretation Rule 1 says "Do not infer identity from a file name or path". This rule could be echoed in DSL › Binding, which currently says only "Exactly one entity has the identity".

## Scenario issues

None. All expected items match the spec.

---

| ID | PASS-S | PASS-H | sonnet D met | haiku D met | tags | top spec section |
|---|---|---|---|---|---|---|
| E01 | yes | no | 10/10 | 24/25 | SEMANTIC(h5) | DSL › Executing a program (trace evidence example) |
| E02 | yes | yes | 8/8 | 20/20 | OTHER(s1,s2 trace nit) | DSL › Entities › Binding |
| E03 | yes | no | 8/8 | 15/20 | DANGER(h2), SYNTAX(h4,h5), OTHER(s1 trace nit) | ENTITY › Interpretation Rules 1; DSL › Validity rules (V11) |
| E04 | yes | yes | 10/10 | 25/25 | — | DSL › Entities › Binding |
| E05 | yes | no | 8/8 | 18/20 | SYNTAX(h3), OTHER(h4; s2 trace nit) | DSL › Validity rules (V11) / Entities › Binding |

```
PART SUMMARY
scenarios: 5
pass_s: 5/5   pass_h: 2/5
d_items_s: 44/44   d_items_h: 102/110
danger_s: 0   danger_h: 1
```
