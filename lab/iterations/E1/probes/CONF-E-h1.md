# Ambiguities, Contradictions, and Missing Rules in DSL Entities

## HIGH RISK

### 1. Concurrent entity modification (Open Question)
**Quote (Part 2, line 1644):**
"Concurrent changes. What happens when concurrent `FORK` branches change the same entity."

**Ambiguity:** Two branches in a `FORK` may both perform operations on the same entity. The specification explicitly lists this as an "Open Question" with no resolution. Two interpreters could:
- Treat the first change as binding and reject/fail the second
- Queue both changes and apply them in some order
- Apply them concurrently and leave the result undefined

**Risk: HIGH** — This directly affects which entity states are reachable and which outcomes are established.

---

### 2. Outcome persistence (Open Question)
**Quote (Part 2, line 1646):**
"Outcome persistence. Whether a verification outcome is part of the entity's Data, recorded in its representation, or exists only within an execution."

**Ambiguity:** Outcomes (e.g., `task.accepted` from `VERIFY task`) are established and kept during execution (DSL line 65), but it's unspecified where they live:
- In memory only (lost when execution ends)?
- In the entity's authoritative representation (persist forever)?
- In a separate outcome log?

Two interpreters executing the same process twice could establish different outcomes the second time if one checks persistent storage and one doesn't.

**Risk: HIGH** — This affects whether subsequent executions depend on previous verification outcomes.

---

### 3. Entity creation (Open Question)
**Quote (Part 2, line 1641-1642):**
"Entity creation. How a new entity is created within a process, and how its identity is generated. `EMIT` does not create entities."

**Ambiguity:** The DSL provides no statement to create an entity. `EMIT` explicitly does not create entities. But can delegated work create entities?

Reading 1: Processes can only operate on pre-existing entities; no process can create a new entity.
Reading 2: Delegated work may create entities, but the DSL doesn't describe the mechanism.

**Risk: HIGH** — This determines whether a category of processes (those that generate new work) can be expressed.

---

### 4. When is binding satisfied checked — once only, or continuously?
**Quote (Part 1, line 510-513):**
"| Exactly one entity has the identity, it is of type `<Type>`, and it is structurally valid (for a relation: the relation has exactly one target) | The name refers to that entity until execution ends. |
| Anything else | Execution ends, as with `STOP`. No statement after the bindings runs. |"

**Ambiguity:** The binding section implies checking at the start of execution and states "No statement after the bindings runs" if unsatisfied. But what if the entity is deleted, or changes type, during execution? What if structural validity changes after `WAIT`, `HITL`, or `DELEGATE`?

Reading 1: Bindings are verified once at the start; if an entity becomes invalid later, operations on it fail.
Reading 2: Bindings are continuously re-verified; if an entity becomes invalid during execution, execution ends immediately.

**Risk: HIGH** — This affects whether an execution can continue and whether entity loss is detected early or late.

---

### 5. Multi-valued relations (Open Question)
**Quote (Part 2, line 1645):**
"Multi-valued relations. How a relation with cardinality greater than one is bound or referenced."

**Ambiguity:** The binding form (line 501) shows only single-target relations: `<name>:<Type> = <bound-name>.<relation>`. If a relation has cardinality 0..*, the form is undefined. Two interpreters could:
- Reject such bindings as invalid
- Bind a collection and allow indexing
- Bind only if exactly one target exists

**Risk: HIGH** — This determines whether relationships with multiple targets can be used in processes.

---

## MEDIUM RISK

### 6. Structural validity timing and scope
**Quote (Part 1, line 521-522):**
"An entity that is no longer structurally valid is `rejected`."

**Quote (Part 1, line 510-513 — binding):**
"structurally valid (for a relation: the relation has exactly one target)"

**Ambiguity:** Structural validity is required at binding time, but when else is it checked?
- Only when `VERIFY` is called?
- At every operation (VERIFY, TRANSITION)?
- After every external event (DELEGATE, HITL, WAIT)?

Two interpreters could disagree on whether a task with a missing Acceptance Criteria section (violates template) is rejected at binding, at first use, or only at VERIFY.

**Risk: MEDIUM** — Affects error detection timing and whether invalid entities can be operated on.

---

### 7. Current status definition for precondition checking
**Quote (Part 1, line 534-535; Entity Model line 1311-1315):**
"the change from the current status to `<status>` is declared by the Definition"

**Ambiguity:** "Current status" is ambiguous:
- The status when TRANSITION is reached?
- The status last read from the authoritative representation?
- The status after the most recent TRANSITION in this execution?

These could differ if delegated work modifies the entity, or if another process modifies it concurrently.

Reading 1: Use the status at the moment TRANSITION statement is reached.
Reading 2: Re-read the entity before checking the transition.

**Risk: MEDIUM** — Affects which transitions are allowed and whether concurrent changes cause failure.

---

### 8. When is TRANSITION "done"?
**Quote (Part 1, line 531-537):**
"Then the entity's authoritative representation (for example its file) records the new status; the step is done only when it has."

**Ambiguity:** "the step is done only when it has" — does "it" refer to:
- The status change is recorded (the TRANSITION statement completes after the file is updated)?
- The status change is applied (the TRANSITION statement completes once the status is updated, file may follow)?

Two interpreters could disagree on whether the next statement can assume the file has been updated.

**Risk: MEDIUM** — Affects whether a delegated task can immediately read the updated entity status.

---

### 9. TRANSITION precondition checking timing
**Quote (Entity Model line 1311-1315):**
"An entity transition is valid only when:
1. the target status is declared by the Definition;
2. the change from the current status to the target status is declared by the Definition;
3. the precondition of that change is satisfied."

**Ambiguity:** The preconditions include `verified: accepted` and `field <field> is set`. But when are these checked?

- At the moment the TRANSITION statement is reached?
- After the preceding statement completes?
- After the entity data is re-read?

If a `VERIFY` establishes `accepted`, and then delegated work changes the entity, is the precondition `verified: accepted` still satisfied?

**Risk: MEDIUM** — Affects whether preconditions remain stable or must be re-evaluated.

---

### 10. "Human" precondition scope in FALLBACK
**Quote (Entity Model line 1321):**
"`human: <answer>` holds only when the `TRANSITION` is inside the flow of `WHEN <h>.<answer>` for a `HITL:<h>` without `AUTO`."

**Ambiguity:** "Inside the flow of" refers to parse-tree nesting, but execution-wise:

Reading 1: If the WHEN condition is false, the `→ FALLBACK` is not "inside the flow" and a `TRANSITION` in the fallback cannot use `human:` precondition.
Reading 2: If the TRANSITION is textually nested under the WHEN, even if in a FALLBACK, it counts as "inside the flow."

Example: If `WHEN task.accepted` is false and its `→ FALLBACK` contains `TRANSITION task "Rework" [human: approved]`, does the precondition hold?

**Risk: MEDIUM** — Affects whether transitions in fallbacks can depend on earlier decisions.

---

### 11. Evidence availability and ambiguity in VERIFY
**Quote (Part 2 fixture, line 1954-1955; DSL line 1957):**
"every Acceptance Criteria item is satisfied, and each item names its evidence (a test, a file, a command output)."

"If an item cannot be evaluated (its evidence is unavailable or the item is ambiguous), `VERIFY` fails."

**Ambiguity:** What counts as "unavailable" or "ambiguous"?

Reading 1: If evidence is mentioned but not located, VERIFY fails.
Reading 2: If evidence is located but insufficient, VERIFY fails.

Example: Task criterion "After 5 failed attempts, return HTTP 429." One interpreter runs a test; another reads code. Different evidence, potentially different verification outcomes.

**Risk: MEDIUM** — Affects whether verification is reproducible and objective.

---

### 12. Field precondition interpretation
**Quote (Part 2, line 551-552):**
"`field <field> is set | the entity's field `<field>` has a value`"

**Ambiguity:** "Has a value" could mean:
- The field key exists in YAML (even if null)?
- The field exists and is non-empty?
- The field exists and is not explicitly missing?

Example: In YAML, `adr:` (null value) vs. `adr: ADR-0100` vs. missing `adr` key.

Two interpreters could disagree on which satisfies `field adr is set`.

**Risk: MEDIUM** — Affects whether optional fields can be used as preconditions.

---

### 13. Entity data refresh scope
**Quote (Part 2, line 1401-1405 — Interpretation Rule 7):**
"After `WAIT`, `HITL`, `DELEGATE`, or `JOIN`, the data may have changed. Re-read the authoritative representation before depending on it."

**Ambiguity:** "Before depending on it" is vague. Does this mean:
- Re-read before the next statement?
- Re-read before the next operation on the entity?
- Re-read only if the operation requires it?

Also, this rule is in "Interpretation Rules" but is not reflected in the DSL execution rules. Is an interpreter required to follow it, or is it advisory?

**Risk: MEDIUM** — Affects whether stale data is detected and whether processes are reproducible.

---

## LOW RISK

### 14. When binding errors occur vs. when operations fail
**Quote (Part 1, line 510-513; line 559-563 — Failures table):**
"Execution ends, as with `STOP`. No statement after the bindings runs."

"| binding | it is not satisfied | execution ends, as with `STOP` |"

**Ambiguity:** What is the difference between "binding is not satisfied" (line 510) and "binding fails" (line 559)?
- Are they the same?
- Can a binding be unsatisfied later and then fail?

Two interpreters might name the same state differently, but the effect (`STOP`) is the same.

**Risk: LOW** — The effect is clear even if terminology differs.

---

### 15. Entity type immutability guarantee
**Quote (Part 2, line 1010):**
"An entity's type never changes."

**Ambiguity:** Is this:
- A rule the system enforces?
- An assumption processes can make?
- A contract the entity model declares?

If delegated work attempts to change an entity's type field, does it:
- Fail silently?
- Fail with an error?
- Succeed?

Two interpreters could handle this differently, but the spec assumes type is immutable.

**Risk: LOW** — Delegated work is governed by the Definition, which can forbid type changes. The assumption is backed by a contract.

---

### 16. ADR supersession invariant responsibility
**Quote (Part 2 fixture, line 1872-1875 — ADR Definition):**
"An ADR with `superseded-by` set is `Superseded`, and the target ADR has `supersedes` pointing back."

**Ambiguity:** Who maintains this bidirectional invariant?
- The process must update both ADRs?
- The runtime maintains it automatically?
- It's assumed to be true but not enforced?

If a process updates ADR-0100 to set `superseded-by: ADR-0101`, must it also update ADR-0101 to set `supersedes: ADR-0100`?

Reading 1: The process must do both, or the invariant fails and VERIFY rejects.
Reading 2: The runtime maintains the invariant automatically.

**Risk: LOW** — The Definition doesn't declare transitions for bidirectional updates, so the process would need to handle it or the invariant is aspirational.

---

### 17. Identity uniqueness enforcement
**Quote (Part 2, line 988-989):**
"An identity: is unique within the execution environment;"

**Ambiguity:** Is the execution environment:
- Global across all processes?
- Local to one process execution?
- A namespace declared by the process?

Two interpreters might disagree on whether the same identity can exist in different processes or scopes.

**Risk: LOW** — This is primarily a deployment concern, not a DSL behavior concern.

---

### 18. What counts as an entity "operation"
**Quote (Part 2, line 1371-1377):**
"Before the first operation on an entity, read: its authoritative representation, its Template, its Definition."

**Ambiguity:** Is an "operation" only:
- VERIFY and TRANSITION?
- Also conditions that test the entity (e.g., `WHEN entity.outcome`)?
- Also binding the entity?

Two interpreters might read the entity at different times.

**Risk: LOW** — The effect (reading when needed) is consistent; the exact timing differs slightly but doesn't change outcomes.

---

### 19. Closed vocabulary enforcement
**Quote (Part 2, line 1106-1108):**
"Every name a process may use for an entity — status, outcome, relation — must be declared by its Definition or Template.

An interpreter must not use, infer, or accept an undeclared name."

**Ambiguity:** What happens if a process refers to an undeclared name?
- Reject the program as invalid?
- Fail at execution time?
- Ignore and return false?

Two interpreters might detect the error at different phases.

**Risk: LOW** — Either way, the process doesn't succeed with the wrong name. The detection timing differs.

---

### 20. Delegated work and entity field modifications
**Quote (Part 2, line 1341-1345):**
"Delegated work may concern an entity. Delegated work may change an entity's fields and sections only as its Definition permits. Delegated work does not change the entity's status."

**Ambiguity:** "Only as its Definition permits" — but the Definition's "Permitted changes" section (fixture line 1963-1965) is not consistently defined across entity types. If a Definition is silent on a field, can it be changed?

Reading 1: Silence means no change is permitted.
Reading 2: Silence means any change not forbidden is permitted.

**Risk: LOW** — The fixture examples provide "Permitted changes" sections. If Definition is missing this section, the process should fail or interpret strictly (no changes).

---

### 21. Representation vs. Data for identity
**Quote (Part 2, line 1363-1369 — Interpretation Rule 1):**
"Locate the representation whose declared identity equals the bound identity. Do not infer identity from a file name or path."

**Note:** Fixture file `docs/tasks/TASK-0105.md` has `id: TASK-0106` (line 1817). 

**Ambiguity:** Is this intentional test data, showing the file name is ignored? Or is it an error?

Reading 1: The identity is TASK-0106 (from the id field); the file name is ignored.
Reading 2: There's an inconsistency and the entity is malformed.

**Risk: LOW** — The rule is clear (use the id field), but the fixture example is confusing. This tests whether interpreters follow the rule despite contradictory metadata.

---

### 22. Definition is not Implementation
**Quote (Part 2, line 1112-1117):**
"A Definition states **what** and **why**.

For example, it may state when a task counts as verified.

It does not state which command, tool, or program performs the verification."

**Ambiguity:** If a Definition says "every Acceptance Criteria item is satisfied," but doesn't specify how to check, two interpreters could:
- Require explicit evidence (a test file, log output)?
- Infer satisfaction from code inspection?
- Ask the human?

**Risk: LOW** — The interpreter must find a way to evaluate the criteria; if it cannot, VERIFY fails. The interpretation is flexible but the outcome is deterministic.

