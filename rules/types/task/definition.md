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

| From       | To         | Precondition       |
|------------|------------|--------------------|
| Todo       | InProgress | none               |
| InProgress | Review     | verified: accepted |
| InProgress | Debugging  | verified: rejected |
| Debugging  | InProgress | none               |
| Review     | InProgress | none               |
| Review     | Done       | human: approved    |

Preconditions use the forms of `dsl.md`, **Entities › Preconditions**.

## Verification

- `accepted`: every Acceptance Criteria item is satisfied, and each item names its evidence (a test, a file, a command output).
- `rejected`: at least one item is not satisfied, and each unsatisfied item is named.

If an item cannot be evaluated (its evidence is unavailable or the item is ambiguous), `VERIFY` fails.

## Relations

- `adr`: the architectural decision that the work must conform to.
- `milestone`: the roadmap stage the work belongs to.

## Permitted changes by delegated work

Delegated work may edit Description, Acceptance Criteria and Notes only while the Task is `Todo`, `InProgress` or `Debugging`. In `Review` and `Done` it may edit only Notes. It never changes `id`, `type`, `status` or `adr`.

## Invariants

- Work on a Task must not contradict its linked ADR.
- A Task in `Done` has no unsatisfied Acceptance Criteria item.
