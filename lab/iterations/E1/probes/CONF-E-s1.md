# Ambiguities, contradictions, and gaps in DSL's Entity rules

Scope: the **Entities** section of `dsl.md`, all of `entity-model.md`, and the fixture contracts under `docs/types`. Ordered high → low risk.

---

## High risk

### 1. A `verified:` precondition can be satisfied by a stale outcome, after the entity has since changed

Quote (`dsl.md`, Preconditions):

> `verified: accepted` | the most recent `VERIFY <name>` in this execution established `<name>.accepted`

Quote (`entity-model.md`, Interpretation Rules):

> **7. Refresh after external activity.** After `WAIT`, `HITL`, `DELEGATE`, or `JOIN`, the data may have changed. Re-read the authoritative representation before depending on it.

Quote (ADR Definition, permitted changes): "Delegated work may edit an ADR while it is `Proposed`... "

**Two readings.** (a) "Most recent `VERIFY`" is purely a log lookup: once `VERIFY adr` establishes `accepted`, that outcome satisfies `verified: accepted` for any later `TRANSITION`, even if the ADR's Decision/Consequences were edited afterward (edits are permitted while `Proposed`) and never re-verified. (b) The precondition implicitly requires the verified data to still be the data being transitioned — i.e., any edit after the `VERIFY` invalidates it and a fresh `VERIFY` is required.
Rule 7 only says to *re-read* data, not to *re-verify* it or invalidate stale outcomes, so nothing in the text forces reading (b). Two interpreters can therefore legally allow (or forbid) an `Accepted`/`Review` transition on data that was never actually verified.

**Risk: high** — this directly governs whether `TRANSITION t1 "Review"` or `TRANSITION a1 "Accepted"` may fire, i.e. the entity's status itself.

---

### 2. `human: <answer>` is not tied to the entity or the transition being decided

Quote (`dsl.md`, Preconditions):

> `human: <answer>` | the `TRANSITION` is inside the flow of a `WHEN <h>.<answer>`, and `HITL:<h>` has no `AUTO`

Quote (`dsl.md`, Preconditions, footnote): "A `human:` precondition can only be satisfied by a human's answer to a `HITL` without `AUTO`. The agent can never satisfy it."

**Two readings.** (a) Literal: the rule only checks syntactic nesting and answer-text equality. If `TRANSITION t1 "Done"` happens to sit inside `WHEN merge.approved` (a `HITL` about something else entirely, e.g. "Merge this change?"), the precondition `human: approved` is satisfied — the human never was asked about the task at all. (b) Intended: the `HITL` must actually be *about* the transition/entity in question — the human must have approved *this* status change, not merely have answered "approved" to an unrelated question that happens to enclose the `TRANSITION` in its flow.
Nothing in the DSL or the Definitions requires the `HITL` question text or name to relate to the entity, so a process author (or an interpreter validating one) cannot mechanically tell (a) from (b) is being avoided.

**Risk: high** — this is the sole mechanism by which a human decision reaches an entity's status (`Review → Done`, `Proposed → Accepted`, `Proposed → Rejected`, `Accepted → Superseded`), so a wrong reading changes who effectively approved what.

---

### 3. Task Definition has no status-scoped edit restriction, unlike ADR Definition — threatens the Task invariant

Quote (Task Definition, "Permitted changes by delegated work"):

> Delegated work may edit Description, Acceptance Criteria and Notes. It must not change `id`, `type` or `status`.

Quote (ADR Definition, "Permitted changes by delegated work"):

> Delegated work may edit an ADR while it is `Proposed`, and must not change `id`, `type`, `status` or `date`. On an `Accepted` ADR it may only set `superseded-by`; the Decision is never edited...

Quote (Task Definition, Invariants): "A Task in `Done` has no unsatisfied Acceptance Criteria item."

**Two readings.** (a) The Task rule is complete as written: Acceptance Criteria may be edited at *any* status, including `Review` or `Done`, with no re-`VERIFY` requirement — the invariant is then only a description of an intended state, not something the rules actively protect. (b) By analogy with ADR (which explicitly locks down what may be edited once `Accepted`), the Task Definition is simply missing an equivalent restriction, and a careful interpreter should refuse edits to Acceptance Criteria once a Task is `Review`/`Done` to preserve the stated invariant.
The two contracts are structured identically in every other respect, so the asymmetry reads as either a deliberate looser rule for tasks or an omission.

**Risk: high** — under reading (a), `TASK-0101` (already `Review`) could have new, unsatisfied Acceptance Criteria added by `DELEGATE` with no forced re-verification before `TRANSITION t "Done"`, silently breaking the stated invariant.

---

### 4. Concurrent `FORK` branches changing the same entity — explicitly unresolved

Quote (`entity-model.md`, Open Questions):

> **Concurrent changes.** What happens when concurrent `FORK` branches change the same entity.

**Two readings.** (a) The authoritative representation serializes writes somehow (last-write-wins, or writes are rejected/merged) and both branches still each see a consistent read/write. (b) Concurrent branches touching the same entity is simply undefined territory — the whole execution's outcome is unspecified, and a compliant interpreter could refuse to run such a program, silently corrupt data, or apply an implicit lock.
Nothing in `dsl.md`'s `FORK`/`JOIN` rules addresses entities at all, and the Entity Model punts explicitly.

**Risk: high** — `FORK` is a normal top-level control construct and nothing forbids two branches from `DELEGATE`ing against, or `TRANSITION`ing, the same bound entity (e.g. two branches both trying `TRANSITION t1 "Debugging"`), yet the result is entirely unspecified.

---

### 5. No defined way for `WHEN` to test an entity's current status — explicitly unresolved

Quote (`entity-model.md`, Open Questions):

> **Status conditions.** How a `WHEN` condition tests an entity's current status. This depends on the DSL condition grammar.

Quote (`dsl.md`, Outcomes): "No other statement produces outcomes." (only `VERIFY` and `HITL` do)

**Two readings.** (a) It is simply impossible in this DSL version to branch on "is `t1` currently `InProgress`?" — a process can only branch on the *last* `VERIFY`/`HITL` outcome, never on stored status directly, so any apparent need for a status check must be re-expressed via `VERIFY`/`HITL`. (b) Some interpreters might read `WHEN t1.<status>` as legal by analogy with `WHEN t1.accepted`, treating status as a de-facto outcome, even though V6 and the Outcomes table say only `VERIFY`/`HITL` produce outcomes and nothing declares status names as outcomes.
Two "careful readers" could genuinely disagree on whether `WHEN t1.InProgress` is a legal condition or automatically INVALID under V6.

**Risk: high** — affects whether entire classes of programs (any that want to branch on current status without re-verifying) are even expressible/valid.

---

## Medium risk

### 6. ADR invariant vs. its own transition precondition create a self-contradiction window

Quote (ADR Definition, Transitions): "`Accepted` | `Superseded` | `field superseded-by is set; human: approved`"

Quote (ADR Definition, Invariants): "An ADR with `superseded-by` set is `Superseded`, and the target ADR has `supersedes` pointing back."

**Two readings.** (a) The invariant is a description of the *end state only* — momentarily, between the delegated edit that sets `superseded-by` (permitted per "On an `Accepted` ADR it may only set `superseded-by`") and the completed `TRANSITION` to `Superseded`, the ADR is `Accepted` with `superseded-by` set, which literally violates the invariant as stated; this is tolerated as a transient. (b) The invariant is absolute at every point in time, so setting `superseded-by` on an `Accepted` ADR before the `TRANSITION` executes is itself not permitted — meaning the very precondition the Definition requires (`field superseded-by is set`) can never legally be reached, making the transition unreachable. There is also no stated mechanism for *who* sets the reciprocal `supersedes` field on the target ADR, or when.

**Risk: medium** — it only bites when superseding an ADR, but a strict reading makes the transition impossible to legally reach.

---

### 7. "Has a value" for `field <field> is set` is undefined

Quote (`dsl.md`, Preconditions): "`field <field> is set` | the entity's field `<field>` has a value"

**Two readings.** (a) "Has a value" means the front-matter key is present at all, regardless of its content (so `superseded-by: ""` or `superseded-by: null` counts as set). (b) "Has a value" means non-empty/non-null content specifically. The Templates only say fields are "required"/"optional" with a format, never define what an empty vs. absent vs. null value means for this precondition.

**Risk: medium** — directly gates the ADR `Accepted → Superseded` transition.

---

### 8. Terminal statuses are asserted but never enforced against the transition table

Quote (`entity-model.md`, Definition): "**Statuses** — The closed list of lifecycle statuses, the initial status, and the terminal statuses."

Quote (Task Definition, Statuses): "- Done (terminal)"; (ADR Definition): "- Rejected (terminal) / - Superseded (terminal)"

**Two readings.** (a) "Terminal" is purely documentation — the only thing that actually prevents leaving `Done` is that no row in the Transitions table lists `Done` as a `From`; the label itself has no normative force, and if a Definition ever *did* list a `From: Done` row, the table would simply win. (b) "Terminal" is a hard constraint that an interpreter must independently enforce, such that any transition row with a terminal `From` would itself be INVALID/ignored regardless of what the table says. Neither `dsl.md` nor `entity-model.md` states which is authoritative when the two could conflict.

**Risk: medium** — not exercised by the current fixture tables (which are consistent), but nothing says what should happen if they weren't, and the two concepts ("terminal" label vs. transition table) are never explicitly reconciled.

---

### 9. `TRANSITION` failure conditions omit structural invalidity, unlike `VERIFY`

Quote (`dsl.md`, Failures table): "`TRANSITION <name>` | the status or change is not declared, or the precondition does not hold | its `FALLBACK` runs; if none, execution ends"

Quote (`dsl.md`, Entities › `VERIFY` on an entity): "An entity that is no longer structurally valid is `rejected`."

**Two readings.** (a) Structural invalidity is simply not a `TRANSITION` failure mode at all — if the entity has become structurally invalid since binding (e.g. a required field was externally removed), `TRANSITION` proceeds as normal, checking only status/change/precondition. (b) The general Template rule ("A structurally invalid entity must not be treated as valid by any operation") implicitly overrides the Failures table's incomplete list, so `TRANSITION` must also fail on structural invalidity even though the Failures table never says so.

**Risk: medium** — only matters when an entity is mutated by something outside the process between bind and `TRANSITION`, which the interpreter is told to expect ("the data may have changed", rule 7).

---

### 10. Refresh rule doesn't say what to do if identity/type itself appears to change on re-read

Quote (`entity-model.md`, Interpretation Rules): "**7. Refresh after external activity.** ... Re-read the authoritative representation before depending on it."

Quote (`entity-model.md`, Identity / Entity Type): "never changes during the life of the entity" / "An entity's type never changes."

**Two readings.** (a) These invariants are guarantees about the *modeled world*, so a re-read that appears to show a different `type` or a vanished file simply cannot happen in a well-behaved environment, and no defined interpreter behavior is needed. (b) The environment is externally editable (explicitly: "A human editing the file changes the entity"), so a corrupted/edited file that now shows a different `type`, or has been deleted, is a real possibility the interpreter must handle — yet no rule says whether that ends execution (like a failed binding), triggers a `FALLBACK`, or something else.

**Risk: medium** — plausible in practice (a human or another process touching the file mid-execution) but not addressed anywhere.

---

## Low risk

### 11. Outcome persistence: `entity-model.md` calls it open, but `dsl.md` already answers it

Quote (`entity-model.md`, Open Questions): "**Outcome persistence.** Whether a verification outcome is part of the entity's Data, recorded in its representation, or exists only within an execution."

Quote (`dsl.md`, Preconditions / Outcomes): "the most recent `VERIFY <name>` **in this execution** established `<name>.accepted`" ... "Each subject holds its most recently established outcome."

**Two readings.** (a) `dsl.md` already settles this: outcomes are execution-scoped only, never written to the entity's Data/representation, so the "open question" in Part 2 is stale/inconsistent documentation, not a real gap. (b) `entity-model.md` is the authority on Data/representation, and its listing this as unresolved means an interpreter *could* legitimately persist outcomes into the entity's representation (e.g. a `verified` field), which `dsl.md`'s wording doesn't explicitly forbid at the representation level, only at the "in this execution" lookup level.

**Risk: low** — a documentation inconsistency between the two parts more than a functional ambiguity for the given fixtures, since `dsl.md`'s explicit rule effectively governs.

---

### 12. Multi-valued relations left open, not currently exercised

Quote (`entity-model.md`, Open Questions): "**Multi-valued relations.** How a relation with cardinality greater than one is bound or referenced."

All relations in the given Templates (`adr`, `supersedes`, `superseded-by`) are `0..1`, so this gap is real but not triggered by any fixture entity here.

**Risk: low.**

---

### 13. Entity creation and contract-change handling left open, not needed for the given task

Quote (`entity-model.md`, Open Questions): "**Entity creation.** How a new entity is created within a process, and how its identity is generated. `EMIT` does not create entities." and "**Contract changes.** How existing instances are treated when their Template or Definition changes."

Neither is exercised by operating on the existing `TASK-01xx`/`ADR-01xx` fixtures with their current, unchanging contracts.

**Risk: low.**
