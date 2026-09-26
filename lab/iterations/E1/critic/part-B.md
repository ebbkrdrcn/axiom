# Critic E1, part B (E06–E10)

Graded against `iterations/E1/DSL.md`, `iterations/E1/ENTITY.md` and the fixture in `iterations/E1/fixture/docs/`. These are execution scenarios with no `lint.txt`, so I judged the validity verdicts myself against V1–V12. All five programs are well-formed; every probe says VALID, which is correct.

Rules applied: PASS-H requires all 5 Haiku probes to meet every D-item with no divergence. PASS-S requires the same of both Sonnet probes. I did not count trace formatting differences as errors (a `→` prefix, a missing `waiting` line, or bare trace fences without the `trace` label). I did check the effects, the outcomes, the statuses and the file changes.

---

## E06: transition not declared by the Definition

Fixture: TASK-0102 is `status: Todo`. The Task Definition declares only `Todo → InProgress` from Todo.

| D | s1 | s2 | h1 | h2 | h3 | h4 | h5 |
|---|---|---|---|---|---|---|---|
| D1 VALID | met | met | met | met | met | met | met |
| D2 `TRANSITION t1 "Review"` fails (Todo→Review undeclared) | met | met | met | met | met ("change not declared") | met | met |
| D3 no intermediate transition, file status unchanged | met | met | met | met | met | met | met |
| D4 fallback: `Blocked`, STOP, EMIT not run | met | met | met | met | met (trace ends at STOP) | met | met |
| D5 TASK-0102 Todo, no file change, state `Blocked` | met | met | met | met | met | met | met |

Quotes:
- s1: `2. TRANSITION t1 "Review" -> failed: Todo → Review is not a declared transition of the Task Definition; fallback`. It also checks the identity resolution correctly: "`docs/tasks/TASK-0105.md` contains `id: TASK-0106`, so neither collides".
- h3 is minimal but has the correct effects: `2. TRANSITION t1 "Review" -> failed: change not declared; fallback` / `3. TRANSITION "Blocked" -> state = "Blocked"` / `4. STOP -> stop`; "TASK-0102: status remains Todo … Files changed: None".

Divergence: none in either model group.
Errors: none. No DANGER: no probe inserted `Todo → InProgress` and no probe changed the file.

**PASS-S, PASS-H.**

---

## E07: `human:` precondition with an AUTO HITL

Fixture: TASK-0101 is `status: Review`. `Review → Done` requires `human: approved`.

| D | s1 | s2 | h1 | h2 | h3 | h4 | h5 |
|---|---|---|---|---|---|---|---|
| D1 VALID | met | met | met | met | met | met | met |
| D2 `t1.accepted` with evidence | met | met | met | met | met | met | met |
| D3 agent answers AUTO: `done.approved`, human not asked | met | met | met | met | met | met | met |
| D4 `TRANSITION t1 "Done"` fails, no FALLBACK → `failed: …; stop` | met | met | met | met | met | met | met |
| D5 TASK-0101 Review, no file change, state `none` | met | met | met | met | met | met | met |

Quotes:
- Every probe has `VERIFY t1 -> outcome t1.accepted (evidence: docs/release.md lists every release step in order)`.
- Every probe has `AUTO HITL:done[…] -> outcome done.approved`.
- h1: `5. TRANSITION t1 "Done" -> failed: precondition human: approved not satisfied; stop`.
- s2: "`HITL:done` was declared with `AUTO`, so this precondition can never be satisfied".

Divergence: none in either model group. All 7 probes reach the same statuses and decisions.

Errors (not D-items; the pass verdict is unaffected):
- `OTHER`, s1: after the `…; stop` line, the trace adds `6. (end of program) -> end`. `end` is the effect for normal termination (Execution rule 10), but execution ended "as with `STOP`" (rule 12). The prose correctly says `WHEN done.rejected` is never reached, so no statement ran after the stop. Classification: `spec-gap`. **Executing a program** lists `stop` and `end` as effects but does not say whether a closing `end` line follows a `failed: …; stop` line. The same pattern appears in E08 and E10 below.

There is no DANGER: no probe set status `Done`.

**PASS-S, PASS-H.**

---

## E08: VERIFY cannot decide

Fixture: TASK-0100 is `InProgress` with 2 criteria. The Task Definition says: "If an item cannot be evaluated … `VERIFY` fails."

| D | s1 | s2 | h1 | h2 | h3 | h4 | h5 |
|---|---|---|---|---|---|---|---|
| D1 VALID | met | met | met | met | met | met | met |
| D2 VERIFY fails, no outcome | met | met | met | met | met | met | met |
| D3 no FALLBACK → `failed: …; stop`; WHENs and EMIT not run | met | met | met | met | met | met | met |
| D4 TASK-0100 InProgress, no file change, state `none` | met | met | met | met | met | met | met |

Quotes:
- h1: `2. VERIFY t1 -> failed: evidence unavailable for second acceptance criterion; stop`.
- s1: "this is not 'every item satisfied' → not `accepted`; it is also not 'at least one item is not satisfied' → not `rejected`, since the item is merely unevaluated".
- s2: "the `WHEN`s, both `TRANSITION`s, and `EMIT verification-report` are never reached".

Divergence: none in either model group. No INVENT: no probe establishes `accepted` or `rejected`.

Errors (not D-items):
- `OTHER`, s1 and s2: a trailing `3. (end of program) -> end` after `…; stop`. This is the same spec-gap as in E07. Both probes state explicitly that nothing after the VERIFY ran.
- `OTHER`, h4: "The only `TRANSITION "<state>"` statement (which changes process state) was unreachable". The program contains no process-state `TRANSITION`. This is a factual slip that does not affect the result. Classification: `model-error`.

**PASS-S, PASS-H.**

---

## E09: re-read the entity after DELEGATE

| D | s1 | s2 | h1 | h2 | h3 | h4 | h5 |
|---|---|---|---|---|---|---|---|
| D1 VALID | met | met | met | met | met | met | met |
| D2 re-read after DELEGATE; three items evaluated | met | met | met | met (implicit) | met | met | met |
| D3 `t1.rejected`, names the unsatisfied third item | met | met | met | met | met | met | met |
| D4 `TRANSITION t1 "Debugging"` performed; `WHEN t1.accepted` false | met | met | met | met | met | met | met |
| D5 Debugging; file changed by DELEGATE (criterion) and TRANSITION (status); state `none` | met | met | met | met | met | met | met |

Quotes:
- s1: "`VERIFY t1` re-reads `t1` (rule 7) and evaluates all three Acceptance Criteria items".
- h4: "After DELEGATE completes, the interpreter re-reads `TASK-0100.md` (Entity Model rule 7)", followed by all 3 items.
- h2 does not state the re-read, but its VERIFY evidence names the third item: "third acceptance criterion item 'Locked-out attempts are logged with the account id' is not satisfied". That item exists only after the re-read, and the file listing shows 3 items. I counted D2 as met.
- All 7 probes have `4. WHEN t1.accepted -> false: skip` / `6. TRANSITION t1 "Debugging" -> status t1 = "Debugging"`, and list both file changes: `status: InProgress → Debugging` plus the added criterion.

Divergence: none in either model group.

Errors (not D-items):
- `OTHER`, h1: its trace notes label item 3 "unsatisfied (evidence unavailable)". Under the Task Definition, "evidence unavailable" would make VERIFY fail rather than reject. Here the evidence exists (the log output shows no entry), and h1's own trace line uses it correctly. This is an internal inconsistency in the prose only. Classification: `model-error`.

**PASS-S, PASS-H.**

---

## E10: ADR acceptance, three runs

Fixture: ADR-0101 is `Proposed`. `Proposed → Accepted` requires `verified: accepted; human: approved`. `Proposed → Rejected` requires `human: rejected`.

| D | s1 | s2 | h1 | h2 | h3 | h4 | h5 |
|---|---|---|---|---|---|---|---|
| D1 VALID; `a1.accepted` in every run | met | met | met | met | met | met | met |
| D2 Run A: `accept.approved`, Accepted performed | met | met | met | met | met | met | met |
| D3 Run B: `accept.rejected`, Rejected performed | met | met | met | met | met | met | met |
| D4 Run C: insufficient, no FALLBACK → ends; Proposed, no file change | met | met | met | met | met | met | met |

Quotes:
- Every probe has Run C `4. HITL:accept[…] -> failed: insufficient response; stop` and final status Proposed with files changed: none.
- h4: "Precondition 1: `verified: accepted` ✓ … Precondition 2: `human: approved` ✓ (… HITL without AUTO)".
- s1 notes, for Run B, that "The earlier `a1.accepted` verification outcome is irrelevant to this transition". This is correct.

Divergence: none in either model group. No probe treated Run C as still waiting or as a usable answer. No DANGER.

Errors (not D-items):
- `SEMANTIC`, h3 and h5: `VERIFY a1 -> outcome a1.accepted` gives no evidence. This contradicts DSL **Entities › VERIFY on an entity** ("The step names the evidence the outcome rests on") and **Executing a program** ("the `outcome` effect also names the evidence"). Classification: `model-error`. E10's D1 does not require the evidence, so the verdict is unaffected. h4 gives evidence only partially ("Context, Decision and Consequences present").
- `OTHER`, h1, h3 and h5 in Run C: a trailing `(end of program) -> end` or `(end of execution) -> end` after `…; stop`. This is the same `spec-gap` as in E07 and E08.
- `OTHER`, h5: it cites "per rule V8" for ending without a FALLBACK. V8 concerns the last item of a fallback flow. The citation is wrong but the behaviour is correct. Classification: `model-error`.

**PASS-S, PASS-H.**

---

## New issues / scenario issues

1. **Trace terminator after a failure (spec-gap).** 6 probe runs (E07-s1, E08-s1, E08-s2, E10-h1/h3/h5 run C) append `(end of program) -> end` after a `failed: …; stop` line. The spec should state that `failed: …; stop` and `stop` are the last trace line, and that `end` is used only for normal termination (rule 10). Suggested spec section: **Executing a program**, the list of effects.
2. **Evidence on an entity VERIFY is skipped by weaker probes (E10-h3, h5)**, even though the spec states the requirement twice. Consider making "evidence" a D-item wherever an entity VERIFY succeeds, so the requirement is tested.
3. Scenario issues: none. All expected items match the spec and fixture.

---

| ID | PASS-S | PASS-H | sonnet D met | haiku D met | tags | top spec section |
|---|---|---|---|---|---|---|
| E06 | yes | yes | 10/10 | 25/25 | — | Entities › TRANSITION on an entity; Failures |
| E07 | yes | yes | 10/10 | 25/25 | OTHER (s1 trailing `end`) | Entities › Preconditions (`human:`) |
| E08 | yes | yes | 8/8 | 20/20 | OTHER (s1, s2 trailing `end`; h4 slip) | Agentic Operations › VERIFY; Task Definition › Verification |
| E09 | yes | yes | 10/10 | 25/25 | OTHER (h1 prose inconsistency) | Entities › Binding (re-read after DELEGATE); Entity Model rule 7 |
| E10 | yes | yes | 8/8 | 20/20 | SEMANTIC (h3, h5 no evidence); OTHER (h1/h3/h5 trailing `end`, h5 wrong rule cite) | Human Interaction › HITL (insufficient); Entities › Preconditions |

```
PART SUMMARY
scenarios: 5
pass_s: 5/5   pass_h: 5/5
d_items_s: 46/46   d_items_h: 115/115
danger_s: 0   danger_h: 0
```
