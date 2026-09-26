# Milestone Definition

## Meaning

A stage of a project's roadmap. It is a set of deliverables with exit criteria, which Tasks work towards through their `milestone` relation.

## Statuses

- Planned (initial)
- Active
- Done (terminal)
- Dropped (terminal)

## Transitions

| From    | To      | Precondition                        |
|---------|---------|-------------------------------------|
| Planned | Active  | none                                |
| Active  | Done    | verified: accepted; human: approved |
| Planned | Dropped | human: approved                     |
| Active  | Dropped | human: approved                     |

Preconditions use the forms of `dsl.md`, **Entities › Preconditions**.

## Verification

- `accepted` means both of the following hold:
  - every Exit Criteria item is satisfied, and each item names its evidence;
  - every Task whose `milestone` is this Milestone is `Done`.
- `rejected`: at least one item or Task does not hold. Each one is named.

## Relations

- `requires`: Milestones that must be `Done` before this one can become `Active`.

## Permitted changes by delegated work

- **While `Planned` or `Active`,** delegated work may edit Delivers, Exit Criteria and Notes. It never changes `id`, `type`, `status` or `code`.
- **In `Done` or `Dropped`,** it may edit only Notes.

## Invariants

- A Milestone that another Milestone `requires` is `Done` before that one is `Active`.
