# go_harness Entity Model

## Purpose

This document defines the entities that go_harness DSL processes operate on: what an entity is, which contracts govern it, and how a process refers to it.

go_harness has no mandatory runtime.

The interpreter of a process is the model executing it. The model is in the same position as a developer following a team's methodology: a developer produces consistent results not because a program enforces them, but because the work, its context, and the rules are explicitly defined.

The Entity Model serves the same purpose. It tells the interpreter:

- which context to read,
- which contract applies,
- which changes are meaningful,
- where a change must be recorded.

The goal is **behavioral determinism**.

Two interpreters executing the same process against the same entities may produce different text. They must reach the same statuses, outcomes, and decisions.

Consequently, every rule in this document is written to be followed by reading, not enforced by a program.

Where a rule leaves a choice open, interpreters diverge. Such a choice must be resolved by a contract or by a human, never by guessing.

---

# Overview

The Entity Model separates six concepts:

**Entity**

A distinguishable thing with an identity, on which meaningful operations are performed.

**Entity Type**

The kind of an entity.

**Template**

The structural contract of an Entity Type.

**Definition**

The semantic and behavioral contract of an Entity Type.

**Data**

The current condition of a specific entity: its field and section values, including its status.

**Representation**

The form in which an entity's data is expressed in some medium.

```text
Entity Type
    │
    ├── Template        structural contract
    │
    └── Definition      semantic / behavioral contract
                │
                ▼
          Entity Instance
                │
                ├── Identity
                │
                └── Data
                       │
                       ▼
                Representation
```

This diagram describes relationships between concepts. It is not syntax.

None of these concepts may be used in place of another:

> Entity ≠ Template  
> Entity ≠ Definition  
> Entity ≠ Data  
> Entity ≠ Representation  
> Template ≠ Definition  
> Data ≠ Representation

---

# Entity

An **Entity** is a conceptual and operational thing within the execution environment that has an identity, can be distinguished from other entities, and can be the subject of meaningful operations.

Examples include a task and an architectural decision record (ADR).

**An entity is not an artifact.**

A file, a database row, an index entry, a cache entry, or an in-memory object is not the entity. Each may be a representation of the entity or a means of accessing it.

For example, the file `docs/tasks/TASK-0001.md` may represent the task `TASK-0001`. The file is not the task.

---

# Identity

Every entity has exactly one identity.

```text
TASK-0001
ADR-0003
```

An identity:

- is unique within the execution environment;
- never changes during the life of the entity;
- is never reused for another entity;
- is independent of any representation.

The following may change without changing identity:

- file path or file name,
- storage location,
- serialization format,
- index position.

An identity does not by itself determine the entity's type. A `TASK-` prefix is a naming convention, not evidence of type.

---

# Entity Type

Every entity belongs to exactly one **Entity Type**.

An entity's type never changes.

An Entity Type has a name:

```text
Task
ADR
```

An Entity Type has exactly one Template and exactly one Definition.

An Entity Type is not an entity. It is the level at which contracts are defined.

---

# Template

A **Template** is the structural contract of an Entity Type.

It answers:

> "What structure must an entity of this type have?"

A Template defines:

- the fields of an entity, and whether each is required or optional;
- the permitted format or values of each field;
- the sections of an entity, and whether each is required or optional;
- the relations an entity can express, their target type, and their cardinality.

A Template does not define:

- what the entity means;
- which status changes are permitted;
- how work concerning the entity is performed.

## Structural Validity

An entity is **structurally valid** when every required field and section is present and every value conforms to the Template.

A structurally invalid entity must not be treated as valid by any operation.

---

# Definition

A **Definition** is the semantic and behavioral contract of an Entity Type.

It answers:

> "What does this entity mean, what can be done with it, and under which rules?"

A Definition defines:

**Meaning**

What an entity of this type is.

**Statuses**

The closed list of lifecycle statuses, the initial status, and the terminal statuses.

**Transitions**

The closed list of permitted status changes, and the precondition of each. Preconditions are written in the forms defined by the DSL (`dsl.md`, **Entities › Preconditions**): `none`, `verified: accepted`, `verified: rejected`, `human: <answer>`, `field <field> is set`.

**Verification**

The criteria and the required evidence for the two verification outcomes, `accepted` and `rejected`. A Definition cannot declare other outcomes.

**Relations**

What each relation declared in the Template means.

**Invariants**

Conditions that must hold in every state of the entity.

## Explicit Rules and Judgment Criteria

A Definition contains two kinds of rules.

**Explicit rules** can be decided by reading data alone.

Examples: the list of statuses, the transition table, which outcome a transition requires.

Explicit rules must be applied exactly.

**Judgment criteria** require evaluation.

Example: "every acceptance criterion is satisfied".

Judgment criteria are applied only through `VERIFY`, and must state what evidence satisfies them.

## Closed Vocabulary

Every name a process may use for an entity — status, outcome, relation — must be declared by its Definition or Template.

An interpreter must not use, infer, or accept an undeclared name.

## Definition Is Not Implementation

A Definition states **what** and **why**.

For example, it may state when a task counts as verified.

It does not state which command, tool, or program performs the verification.

---

# Entity Instance

An **Entity Instance** is a specific entity.

An instance has:

- an identity,
- an Entity Type,
- Data.

Through its type, an instance is governed by a Template and a Definition.

Three levels are therefore distinguished:

**Type level**

What kind of entity it is.

**Contract level**

The Template and Definition that govern it.

**Instance level**

Its identity and its current Data.

---

# Data

**Data** is the current condition of a specific entity: the current values of its fields and sections.

Data belongs to the instance. Template and Definition belong to the type.

**Status** is the part of Data governed by the Definition's transitions.

Data may change while Template and Definition stay the same.

A change of Data does not change the entity's identity or type.

The word **state** is reserved for the process state of the DSL (`TRANSITION "<state>"`). An entity has data and a status, not a state.

---

# Representation

A **Representation** is the form in which an entity's data is expressed in some medium.

The same entity may be represented:

- as a file,
- in memory,
- in a database,
- in an index or cache,
- in an API response,
- in the interpreter's context.

For each Entity Type, the environment designates exactly one **authoritative representation**.

Every other representation is derived and may be stale.

Templates and Definitions may themselves have representations, such as files. Those files are representations of contracts. They are not entities.

## Synchronization

The relationship between Data and representation is defined as follows:

- The authoritative representation expresses the entity's Data. Reading the Data means reading the authoritative representation.
- A data change performed by a process is complete only when the authoritative representation has been updated.
- A change to the authoritative representation is a data change, whoever makes it. A human editing the file changes the entity.
- A change to a derived representation, including the interpreter's own context, is not a data change.

---

# Entities in the DSL

The DSL forms below (binding, `VERIFY <name>`, `TRANSITION <name> "<status>"`), their validity rules (V11, V12) and their failure behaviour are defined normatively in `dsl.md`, section **Entities**. This section explains them in terms of the Entity Model.

## Binding

A binding gives an entity a name within a process.

```text
<name>:<Type> = <identity>
```

Example:

```text
t1:Task = TASK-0001
```

This means:

> Within this process, `t1` refers to the entity whose identity is `TASK-0001`, which must be of type `Task`.

A binding is a **reference**, not a copy.

It does not load or freeze data. Data is read from the authoritative representation when it is needed.

A binding may also follow a single-valued relation of an already bound entity:

```text
<name>:<Type> = <name>.<relation>
```

Example:

```text
a1:ADR = t1.adr
```

### A Binding Is a Requirement

A binding is satisfied only when:

1. exactly one entity with that identity exists;
2. that entity is of the declared type;
3. that entity is structurally valid.

For a relation binding, the relation must also have exactly one target.

If a binding cannot be satisfied, execution ends, as with `STOP`. No statement after the bindings runs. This is an execution failure, not a validity error: the program itself stays valid.

Bindings are resolved once, at the start. They are not re-checked; later changes to an entity are seen by re-reading it (Interpretation Rule 7).

### Binding Rules

- A binding is immutable. The name refers to the same identity until the process ends.
- A name may be bound only once in a process.
- Bindings appear at the top of a process, unindented, before every other statement. A binding anywhere else is invalid (V11).
- A bound name must not be used as a `HITL` name (V12).
- A bound name is visible in every scope that follows it.

---

## Referring to an Entity

A bound name may be used as the argument of a DSL operation:

```text
VERIFY t1
TRANSITION t1 "Review"
```

and in conditions:

```text
WHEN t1.accepted
```

---

## Operations on Entities

The DSL defines the generic meaning of an operation.

The Definition defines what that operation means for its Entity Type and under which rules it may be applied.

### VERIFY

```text
VERIFY <name>
```

Evaluates the entity against the verification criteria of its Definition.

`VERIFY`:

- establishes exactly one outcome, `accepted` or `rejected`;
- names the evidence on which the outcome rests;
- does not modify the entity.

A structurally invalid entity is `rejected`.

If the criteria do not determine a single outcome, no outcome is established and the interpreter must not choose one. The `VERIFY` fails: its `FALLBACK` runs, or execution ends if it has none.

### TRANSITION

```text
TRANSITION <name> "<status>"
```

Changes the status of the entity.

This is distinct from:

```text
TRANSITION "<state>"
```

which changes the state of the process, as defined by the DSL.

An entity transition is valid only when:

1. the entity is structurally valid;
2. the target status is declared by the Definition;
3. the change from the current status to the target status is declared by the Definition;
4. the precondition of that change is satisfied.

An invalid transition is not performed.

Execution must not proceed as if it were performed, and the interpreter must not substitute a different status or insert intermediate transitions. The `TRANSITION` fails: its `FALLBACK` runs, or execution ends if it has none.

A precondition `human: <answer>` holds only when the `TRANSITION` is inside the flow of `WHEN <h>.<answer>` for a `HITL:<h>` without `AUTO` whose question contains the entity's identity. A human decision is therefore always obtained through a `HITL` in the process, about that entity.

A precondition `verified: accepted` (or `rejected`) holds only if the entity's data has not changed since that `VERIFY`, other than by `TRANSITION`. After any other change, the entity must be verified again.

A valid transition is complete only when the authoritative representation records the new status.

The status of an entity changes only through `TRANSITION`.

### Outcome Conditions

```text
WHEN <name>.<outcome>
```

is satisfied when the most recent `VERIFY <name>` in the current execution established `<outcome>`.

Before any `VERIFY <name>` has been executed, no outcome condition on `<name>` is satisfied.

`<outcome>` is `accepted` or `rejected`.

### DELEGATE

Delegated work may concern an entity.

Delegated work may change an entity's fields and sections only as its Definition permits.

Delegated work does not change the entity's status. Status changes only through `TRANSITION`.

Completion of delegated work does not establish a verification outcome.

### EMIT

An artifact produced by `EMIT` is not an entity.

`EMIT` does not create an entity.

---

# Interpretation Rules

There is no runtime between the process and the entities. The interpreter resolves, validates, and persists.

The interpreter must follow these rules.

**1. Resolve by identity.**

Locate the representation whose declared identity equals the bound identity.

Do not infer identity from a file name or path.

If no representation, or more than one, declares that identity, the binding is not satisfied.

**2. Read before acting.**

Before the first operation on an entity, read:

- its authoritative representation,
- its Template,
- its Definition.

**3. Validate.**

Check the declared type and structural validity before using the entity.

**4. Apply contracts exactly.**

Apply explicit rules exactly as written.

Do not extend a closed vocabulary.

**5. Persist changes.**

Record a data change in the authoritative representation as part of the operation that makes it.

Change only what the operation concerns.

**6. Make no silent changes.**

Reading and `VERIFY` do not modify an entity.

Unrelated content is not reformatted or rewritten.

**7. Refresh after external activity.**

After `WAIT`, `HITL`, `DELEGATE`, or `JOIN`, the data may have changed.

Re-read the authoritative representation before depending on it.

**8. Fail what the contracts do not decide.**

When a contract does not determine an answer, do not guess.

The operation fails: its `FALLBACK` runs, or execution ends if it has none. The report names the missing or conflicting rule. When a process needs a human decision, it asks for it with a `HITL`.

---

# Filesystem Representation

In a documentation environment, the authoritative representation of an entity is a Markdown file.

## Layout

```text
docs/
  types/
    <type>/
      template.md
      definition.md
      representation.md
  <collection>/
    <identity>.md
```

`docs/types/<type>/` holds the contracts of one Entity Type. `<type>` is the type name in lowercase.

- `template.md` represents the Template.
- `definition.md` represents the Definition.
- `representation.md` states where instances of the type are stored and how identity, type, and status are encoded.

The representation mapping is kept separate from both contracts, because representation is neither structure nor meaning.

## Instance Format

An instance is a Markdown file with YAML front matter:

```markdown
---
id: TASK-0001
type: Task
status: InProgress
adr: ADR-0003
---
# Fix the login flow

## Description
...

## Acceptance Criteria
- ...
```

- `id` is the identity.
- `type` is the Entity Type.
- `status` is the current status.
- Other front matter fields and sections are defined by the Template.

The file name `<identity>.md` is a convention that makes an entity easy to find. The `id` field is authoritative.

---

# Example

## Task Template

`docs/types/task/template.md`:

```markdown
# Task Template

## Fields

| Field  | Required | Format                                    |
|--------|----------|-------------------------------------------|
| id     | yes      | `TASK-` followed by four digits           |
| type   | yes      | `Task`                                    |
| status | yes      | a status declared by the Task Definition  |
| adr    | no       | identity of an ADR                        |

## Sections

| Section             | Required                   |
|---------------------|----------------------------|
| Description         | yes                        |
| Acceptance Criteria | yes, at least one item     |
| Notes               | no                         |

## Relations

| Relation | Field | Target | Cardinality |
|----------|-------|--------|-------------|
| adr      | adr   | ADR    | 0..1        |
```

## Task Definition

`docs/types/task/definition.md`:

```markdown
# Task Definition

## Meaning

A unit of work with an explicitly verifiable result.

## Statuses

- Todo (initial)
- InProgress
- Debugging
- Review
- Done (terminal)

## Transitions

| From       | To         | Precondition                                 |
|------------|------------|----------------------------------------------|
| Todo       | InProgress | none                                         |
| InProgress | Review     | verified: accepted                           |
| InProgress | Debugging  | verified: rejected                           |
| Debugging  | InProgress | none                                         |
| Review     | InProgress | none                                         |
| Review     | Done       | human: approved                              |

## Verification

Outcomes: `accepted`, `rejected`.

- `accepted`: every Acceptance Criteria item is satisfied, and each item
  names its evidence (a test, a file, a command output).
- `rejected`: at least one item is not satisfied; each unsatisfied item
  is named.

## Relations

- `adr`: the architectural decision the work must conform to.

## Invariants

- Work on a Task must not contradict its linked ADR.
- A Task in `Done` has no unsatisfied Acceptance Criteria item.
```

## Process

```text
t1:Task = TASK-0001
a1:ADR = t1.adr

LOOP:work
  DELEGATE implementation
  VERIFY t1

  WHEN t1.accepted
    → TRANSITION t1 "Review"
    → BREAK

  WHEN t1.rejected
    → TRANSITION t1 "Debugging"
    → DELEGATE diagnosis
    → TRANSITION t1 "InProgress"
```

## Interpretation

Assume `TASK-0001` is in status `InProgress` and links `ADR-0003`.

1. `t1:Task = TASK-0001`: the interpreter finds the single file whose `id` is `TASK-0001`, confirms `type: Task`, reads the Task Template and Definition, and confirms structural validity.
2. `a1:ADR = t1.adr`: the `adr` field holds `ADR-0003`; the interpreter resolves it the same way against the ADR contracts. If `adr` were absent, the binding would not be satisfied.
3. `DELEGATE implementation`: work is performed. `t1`'s status does not change.
4. `VERIFY t1`: the interpreter re-reads `t1` (rule 7), evaluates each Acceptance Criteria item, names its evidence, and establishes `accepted` or `rejected`.
5. On `accepted`: `InProgress → Review` is declared and its precondition holds. The interpreter writes `status: Review` to the file, and the loop ends.
6. On `rejected`: `InProgress → Debugging` is performed and recorded, diagnosis is delegated, and `Debugging → InProgress` is performed and recorded before the next iteration.

---

# Invalid Usage

Type mismatch. The program is well-formed, but the binding is not satisfied, so execution ends before any other statement:

```text
t1:Task = ADR-0003
```

Undeclared transition. The program is well-formed, but from `InProgress` the Task Definition does not declare `Done`, so the `TRANSITION` fails when executed:

```text
TRANSITION t1 "Done"
```

Undeclared outcome. `VERIFY` establishes only `accepted` or `rejected` (V6):

```text
WHEN t1.approved
  → BREAK
```

Rebinding a name (V11):

```text
t1:Task = TASK-0001
t1:Task = TASK-0002
```

Binding inside a scoped construct (V11):

```text
LOOP:work
  t1:Task = TASK-0001
```

---

# Semantic Principles

The Entity Model separates the entity, its contracts, its data, and its representation.

In particular:

- A binding refers to an entity by identity, not to a file.
- The Template defines structure, not meaning.
- The Definition defines meaning and permitted behavior, not implementation.
- Data belongs to the instance; contracts belong to the type.
- The authoritative representation expresses the Data; every other representation is derived.
- The DSL defines the generic meaning of an operation; the Definition defines what it means for a specific Entity Type.

A process that refers to `t1` does not change if the representation of Task moves from Markdown to another medium. Only the representation mapping changes.

---

# Open Questions

The following are not yet defined:

- **Entity creation.** How a new entity is created within a process, and how its identity is generated. `EMIT` does not create entities.
- **Status conditions.** How a `WHEN` condition tests an entity's current status. This depends on the DSL condition grammar.
- **Concurrent changes.** What happens when concurrent `FORK` branches change the same entity.
- **Multi-valued relations.** How a relation with cardinality greater than one is bound or referenced.
- **Outcome persistence.** Whether a verification outcome is part of the entity's Data, recorded in its representation, or exists only within an execution.
- **Contract changes.** How existing instances are treated when their Template or Definition changes.
