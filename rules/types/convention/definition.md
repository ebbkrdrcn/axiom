# Convention Definition

## Meaning

A working rule that contributions to a project must follow. A convention states **how** work is done. An ADR states **why** a decision was taken.

## Statuses

- Proposed (initial)
- Active
- Retired (terminal)

## Transitions

| From     | To      | Precondition                        |
|----------|---------|-------------------------------------|
| Proposed | Active  | verified: accepted; human: approved |
| Proposed | Retired | human: approved                     |
| Active   | Retired | human: approved                     |

Preconditions use the forms of `dsl.md`, **Entities › Preconditions**.

## Verification

- `accepted` means all of the following hold:
  - Rule is one sentence that can be followed without further interpretation.
  - `scope` names where the rule applies.
  - How to check gives:
    - for a `mechanical` check, a command whose result decides compliance;
    - for a `review` check, concrete steps a reviewer follows.
- `rejected`: any of the above does not hold. Each failing point is named.

## Relations

- `adr`: the decision the convention follows from.

## Permitted changes by delegated work

- **While the convention is `Proposed`,** delegated work may edit every section. It must not change `id`, `type` or `status`.
- **On an `Active` convention,** it may edit only Examples and How to check, and only when the rule itself does not change.
- **A changed rule** needs a new convention, and the old one is retired.

## Invariants

- An `Active` convention with `check: mechanical` names a command in How to check.
