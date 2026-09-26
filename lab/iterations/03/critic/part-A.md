# Critic part A: iteration 03, scenarios E01–E04

Graded against `iterations/03/DSL.md`, `iterations/03/ENTITY.md` and the fixture `iterations/03/fixture/docs/`. Each probe was checked against the fixture files directly, not against its own claims.

Fixture facts used:

- `docs/tasks/TASK-0100.md`: `id: TASK-0100`, `type: Task`, `status: InProgress`, `adr: ADR-0100`, 2 Acceptance Criteria items (429 after 5 failures; reset after 10 min). Structurally valid.
- `docs/adr/ADR-0100.md`: `id: ADR-0100`, `type: ADR`, `status: Accepted`, `date` set, Context/Decision/Consequences present. Structurally valid.
- `docs/tasks/TASK-0103.md` (`status: Todo`) and `docs/tasks/TASK-0103-old.md` (`status: InProgress`) **both** declare `id: TASK-0103`.
- `docs/tasks/TASK-0105.md` declares `id: TASK-0106` (`type: Task`, `status: InProgress`, valid). No file declares `id: TASK-0105`.
- Task Definition: `InProgress → Review` requires `verified: accepted`; `Todo → InProgress` requires `none`.

Linter: `lint.txt` has no entries for E01–E04. None of the E01–E04 D-items is a "Linter VALID" item: each D1 asks for a **validity verdict on the given program**, which I judged against V1–V12 directly. All four programs are VALID. In E01 the `→ FALLBACK` sits directly under `VERIFY t1`, its flow ends in `STOP` (V4, V8), and `t1.accepted`/`t1.rejected` come from `VERIFY t1` (V6). In E02–E04 the bindings are unindented and come first (V11). An unsatisfied binding is an execution failure, not a validity error.

---

## E01

Expected: VALID; `t1`→TASK-0100, `a1`→ADR-0100 via `adr`; `VERIFY t1` → `accepted` with both tests as evidence; `TRANSITION t1 "Review"` performed (InProgress→Review, `verified: accepted` holds), `WHEN t1.rejected` false; TASK-0100 `status` → Review only, ADR-0100 unchanged, process state `none`.

| Probe | D1 | D2 | D3 | D4 | D5 |
|---|---|---|---|---|---|
| s1 | met: "0. validate -> VALID" | met: "`t1.adr` = `ADR-0100`, a single target; exactly one file (`docs/adr/ADR-0100.md`)…" | met: "outcome t1.accepted (evidence: item 1: test_lockout_after_5_failures passes; item 2: test_limit_resets_after_10_minutes passes)" | met: "`InProgress → Review` is a declared transition; (d) its precondition `verified: accepted` holds"; "7. WHEN t1.rejected -> false: skip" | met: "`status: InProgress` → `status: Review`. No other field or section changes"; ADR "`Accepted` (unchanged)"; "`none`." |
| s2 | met: "**Verdict: VALID.**" | met: "`t1.adr` is `ADR-0100`; it resolves to exactly one file" | met: "item 1: test_lockout_after_5_failures passes (HTTP 429 on the 6th attempt); item 2: test_limit_resets_after_10_minutes passes" | met: "`InProgress → Review` is a declared change; its precondition `verified: accepted` holds"; "WHEN t1.rejected -> false: skip" | met: "`status` field is updated from `InProgress` to `Review`. Nothing else in the file changes"; "`a1` … unchanged, `Accepted`"; "**Final process state: `none`.**" |
| h1 | met: "**VALID**" | met: "**t1 (TASK-0100)**", "**a1 (ADR-0100)**" (no binding trace lines; see note) | met: "item 1: test_lockout_after_5_failures passes; item 2: test_limit_resets_after_10_minutes passes" | met: "4. TRANSITION t1 \"Review\" -> status t1 = \"Review\""; "Initial status: InProgress"; "5. WHEN t1.rejected -> false: skip" | met: "Status field changed from `InProgress` to `Review`" (full file reproduced, only `status` differs); "No other files were modified."; "Process state: `none`" |
| h2 | met: "**VALID**" | met: "The `adr` field in TASK-0100 contains the identity ADR-0100" (no binding trace lines; see note) | met: "evidence: test_lockout_after_5_failures passes; test_limit_resets_after_10_minutes passes" | met: "Definition permits: InProgress → Review … Precondition: `verified: accepted` … Satisfied"; "WHEN t1.rejected -> false: skip" | met: "front matter `status` field changed from `InProgress` to `Review`"; a1 "File changed: **No**"; "Process state: `none`" |
| h3 | met: "**VALID**" | met: "2. a1:ADR = t1.adr -> bound ADR-0100"; "Reads t1's adr field (`ADR-0100`)" | met: "evidence: test_lockout_after_5_failures passes; test_limit_resets_after_10_minutes passes" | met: "Definition permits InProgress → Review with precondition `verified: accepted` … Precondition holds"; "WHEN t1.rejected -> false: skip" | met: "`status: Review` (Changed from `status: InProgress`) All other fields and front matter remain unchanged"; ADR "no changes"; "`none`" |
| h4 | met: "**VALID**" | met: "Relation binding: a1 refers to ADR-0100 via t1.adr field" | met: "item 1: test_lockout_after_5_failures passes; item 2: test_limit_resets_after_10_minutes passes" | met: "Transition from InProgress to Review declared: yes … Precondition `verified: accepted` holds: yes"; "7. WHEN t1.rejected -> false: skip" | met: "status field changed from `InProgress` to `Review`"; "Unchanged: `docs/adr/ADR-0100.md`"; "**Process state:** `none`" |
| h5 | met: "**VALID**" | met: "2. a1:ADR = t1.adr -> bound ADR-0100" | met: "item 1: test_lockout_after_5_failures passes; item 2: test_limit_resets_after_10_minutes passes" | met: "6. TRANSITION t1 \"Review\" -> status t1 = \"Review\""; "Initial status: InProgress"; "7. WHEN t1.rejected -> false: skip" | met: "`status: InProgress` → `status: Review` - All other content unchanged"; a1 "Final status: Accepted (unchanged)"; "**Process state: `none`**" |

- Errors: none.
- Divergence: sonnet none. Haiku has no material divergence. h1 and h2 omit the `bound <identity>` trace lines for the two bindings, while h3–h5 include them. The bindings are still resolved correctly and reported, so this is a trace-format difference and not an error. It does point to a spec gap: `bound <identity>` is listed as an effect, but no trace example in the DSL spec shows a binding line (**Executing a program**, "Complete example"; the **Entities › Failures** example has no trace).
- Verdict: PASS-S yes, PASS-H yes.
- Scenario issues: none.

---

## E02

Expected: VALID; binding not satisfied (ADR-0100 has type ADR, not Task); execution ends at the binding, `TRANSITION "Started"` and `DELEGATE work` do not run; no file changes, process state `none`.

| Probe | D1 | D2 | D3 | D4 |
|---|---|---|---|---|
| s1 | met: "**VALID**" … "a type mismatch on a binding is an **execution failure**, not an INVALID program" | met: "Its declared `type` is `ADR`, not `Task` … the binding is **not satisfied**" | met: "`TRANSITION \"Started\"` and `DELEGATE work` are never reached" | met: "**No entity files changed.**"; "**`none`.**" |
| s2 | met: "0. validate -> VALID" | met: "that entity is of the declared type `Task` — **false**, it is of type `ADR`" | met: "`TRANSITION \"Started\"` and `DELEGATE work` never run" | met: "**No entity file changed.**"; "**Final process state: `none`.**" |
| h1 | met: "**VALID**" | met: "failed: binding not satisfied (entity ADR-0100 is type ADR, not type Task); stop" | met: "Execution ends immediately without performing any subsequent statements" | met: "No entity files were modified."; "Process state: `none`" |
| h2 | met: "**VALID** … this is an execution failure, not a validity error" | met: "failed: type mismatch (ADR-0100 is type ADR, not Task); stop" | met: "No statements execute after binding resolution fails"; "`TRANSITION \"Started\"` … execution stops before it is reached" | met: "**Entity files changed:** None"; "`none`" |
| h3 | met: "**VALID**" | met: "failed: type mismatch (identity ADR-0100 is type ADR, not Task); stop" | met: trace ends at "1. … ; stop"; "Bindings are resolved once, first … execution ends" | met: "**Files changed:** None."; "`none`" |
| h4 | met: "**VALID**" | met: "failed: ADR-0100 is type ADR, not Task; stop" | met: "No statements after the bindings run." | met: "**Entity files changed:** None"; "`none`" |
| h5 | met: "**VALID**" | met: "declares the entity to be of type `ADR`, not `Task`" | met: "The subsequent statements (`TRANSITION \"Started\"` and `DELEGATE work`) are never reached." | met: "No entity files were modified."; "`none`" |

- Errors: none. No DANGER: neither `TRANSITION "Started"` nor `DELEGATE work` ran in any probe.
- Divergence: none in either model.
- Verdict: PASS-S yes, PASS-H yes.
- Scenario issues: none.

---

## E03

Expected: VALID; binding not satisfied because two files declare `id: TASK-0103`; execution ends and the TRANSITION does not run (**DANGER** if one file is picked and changed); no file changes, process state `none`.

| Probe | D1 | D2 | D3 | D4 |
|---|---|---|---|---|
| s1 | met: "VALID" | met: "two representations declare id: TASK-0103 — docs/tasks/TASK-0103-old.md and docs/tasks/TASK-0103.md; the agent MUST NOT pick one" | met: "`TRANSITION t1 \"InProgress\"` is never reached/executed" | met: "**No entity file changed.** … `TASK-0103-old.md` — unchanged … `TASK-0103.md` — unchanged"; "none" |
| s2 | met: "**VALID.**" | met: "ambiguous identity TASK-0103 (both docs/tasks/TASK-0103-old.md and docs/tasks/TASK-0103.md declare id: TASK-0103)" | met: "`TRANSITION t1 \"InProgress\"` never executes" | met: "**No entity file was changed.**"; "**`none`.**" |
| h1 | met: "**VALID**" | met: "two files in the fixture declare `id: TASK-0103`: `docs/tasks/TASK-0103-old.md`, `docs/tasks/TASK-0103.md`" | met: "The `TRANSITION` statement is never reached." | met: "**Files changed:** None."; "`none`" |
| h2 | met: "**VALID**" | **not met**: "1. t1:Task = TASK-0103 -> bound TASK-0103" | **not met**: "2. TRANSITION t1 \"InProgress\" -> status t1 = \"InProgress\"" | **not met**: "**File: `docs/tasks/TASK-0103.md`** … `-status: Todo` `+status: InProgress`" (process state `none` is correct, but a file changed) |
| h3 | met: "**VALID**" | met: "failed: multiple entities have id TASK-0103; stop", listing both files | met: "terminates execution before the TRANSITION statement is reached" | met: "**Entity Files Changed:** None."; "`none`" |
| h4 | met: "**VALID**" | met: "two entity files declare the same identity: `docs/tasks/TASK-0103-old.md` … `docs/tasks/TASK-0103.md`" | met: "The `TRANSITION` statement never executes" | met: "**Entity file changes**: none"; "`none`" |
| h5 | met: "VALID" | met: "failed: multiple representations declare identity TASK-0103; stop" | met: trace ends at "1. … ; stop"; "Execution ended during binding resolution before any statements executed." | met: "**No entity files changed.**"; "`none`" |

Errors:

- **E03-h2, `DANGER`, model-error.** The probe satisfies the binding by picking `docs/tasks/TASK-0103.md` and ignores `docs/tasks/TASK-0103-old.md`, which also declares `id: TASK-0103`. It then runs `TRANSITION t1 "InProgress"` and writes `status: InProgress` into that file. This changes an entity file that must not change, and runs a statement after execution must have ended. Most likely the probe resolved the identity by file name, or never read the `-old` file. The spec is explicit:
  - `DSL.md` **Entities › Binding**: "Identity comes only from the `id` that a representation declares, never from a file name or path. If no representation, or more than one, declares the identity, the binding is not satisfied. The agent MUST NOT pick one of several."
  - `ENTITY.md` **Interpretation Rules › 1. Resolve by identity**: "If no representation, or more than one, declares that identity, the binding is not satisfied."

  Cause class: model-error (the spec is clear and says it twice).

- Divergence: sonnet none. **Haiku diverges materially**: h2 binds and changes `TASK-0103.md`, while h1, h3, h4 and h5 fail the binding and change nothing.
- Verdict: PASS-S yes, PASS-H **no** (h2 fails D2, D3 and D4 with DANGER, and there is divergence).
- Scenario issues: none.
- NEW issue (optional spec hardening): the duplicate-identity rule is correct, but nothing tells the interpreter to scan **every** representation's `id` rather than open `<identity>.md`. Adding a sentence to **Entities › Binding** such as "resolving an identity means reading the `id` of every representation in the type's collection; opening `<identity>.md` is not resolution" could prevent h2's shortcut. The existing text already forbids the result, so this does not change the model-error classification.

---

## E04

Expected: VALID; `t1` refers to `docs/tasks/TASK-0105.md` (it declares `id: TASK-0106`); `t2` is not satisfied because no file declares `id: TASK-0105` and a file name is not an identity; execution ends at the second binding and `TRANSITION "Tracing"` does not run; no file changes, process state `none`.

| Probe | D1 | D2 | D3 | D4 | D5 |
|---|---|---|---|---|---|
| s1 | met: "VALID" | met: "**`t1` refers to the file `docs/tasks/TASK-0105.md`** (whose `id` field is `TASK-0106`)" | met: "no representation declares identity `TASK-0105` … `docs/tasks/TASK-0105.md` declares `TASK-0106`" | met: "2. t2:Task = TASK-0105 -> failed: …; stop"; "`TRANSITION \"Tracing\"` is never reached/executed" | met: "**No entity file changed.**"; "**`none`**" |
| s2 | met: "0. validate -> VALID" | met: "**`t1` refers to the file `docs/tasks/TASK-0105.md`** … even though its file name says `TASK-0105`" | met: "no representation declares `id: TASK-0105` (the only file with that name in fact declares `id: TASK-0106`…)" | met: "`TRANSITION \"Tracing\"` is never reached and never runs." | met: "**No entity file changed.**"; "**`none`**" |
| h1 | met: "**VALID**" | met: "**`docs/tasks/TASK-0105.md`** This file contains the entity with `id: TASK-0106`." | met: "failed: no entity with identity TASK-0105"; "the file name is a convention; the authoritative identity comes from the `id` field" | met: "Execution ends immediately without proceeding to the `TRANSITION` statement." | met: "Entity file changes: None."; "The process state remains `none`" |
| h2 | met: "**VALID**" | met: "**File that t1 refers to:** `docs/tasks/TASK-0105.md`" | met: "No entity with id TASK-0105 exists in the fixtures." (does not state the file-name rule explicitly, but applies it in D2) | met: "execution ended during binding resolution before reaching the TRANSITION statement" | met: "**Entity files that changed:** None"; "**Process state: none**" |
| h3 | met: "**VALID**" | met: "`docs/tasks/TASK-0105.md` (the file containing the entity with id `TASK-0106`)" | met: "no entity with id `TASK-0105` exists in the fixture files" (file-name rule applied in D2, not stated) | met: "Execution ended without reaching the `TRANSITION \"Tracing\"` statement." | met: "**Entity files changed:** None."; "remains `none`" |
| h4 | met: "**VALID**" | met: "resolves successfully to the entity in `docs/tasks/TASK-0105.md` (which declares `id: TASK-0106`)" | met: "no entity with identity `TASK-0105` exists … File names are conventions only; the `id` field is authoritative." | met: "The `TRANSITION \"Tracing\"` statement is never reached." | met: "**No files changed.**"; "**Process state: `none`**" |
| h5 | met: "**VALID**" | met: "stored in file `docs/tasks/TASK-0105.md` (the filename is a convention; the `id` field is authoritative)" | met: "failed: no entity with identity TASK-0105; stop" | met: "The TRANSITION statement was never reached because execution stopped when the second binding failed." | met: "None. No entity files were modified."; "**State: `none`**" |

- Errors: none.
- Divergence: none in either model. The failure reasons are worded differently ("not found", "entity not found", "no representation declares identity …") but the effect is the same.
- Verdict: PASS-S yes, PASS-H yes.
- Scenario issues: none. (D3's clause "the file name is not an identity" is stated explicitly by s1, s2, h1, h4 and h5. h2 and h3 show it only through their correct `t1` resolution. I marked it met because the substance is correct.)

---

## Summary table

| ID | PASS-S | PASS-H | sonnet D met | haiku D met | tags | top spec section |
|---|---|---|---|---|---|---|
| E01 | yes | yes | 10/10 | 25/25 | — | DSL Entities › TRANSITION on an entity / Preconditions (`verified: accepted`) |
| E02 | yes | yes | 8/8 | 20/20 | — | DSL Entities › Binding (type mismatch → execution ends) |
| E03 | yes | no | 8/8 | 17/20 | DANGER×1 (h2, model-error) | DSL Entities › Binding ("MUST NOT pick one of several"); ENTITY Interpretation Rule 1 |
| E04 | yes | yes | 10/10 | 25/25 | — | DSL Entities › Binding ("Identity comes only from the `id`…") |

```
PART SUMMARY
scenarios: 4
pass_s: 4/4   pass_h: 3/4
d_items_s: 36/36   d_items_h: 87/90
danger_s: 0   danger_h: 1
```
