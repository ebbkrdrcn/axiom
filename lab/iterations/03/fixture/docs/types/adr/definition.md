# ADR Definition

## Meaning

An architectural decision record: one decision that governs the project, with its context and consequences. An ADR records **why** a rule exists. The rule itself lives in the document it governs (for example `dsl.md`); where the two differ, that document wins and the ADR is superseded.

## Statuses

- Proposed (initial)
- Accepted
- Rejected (terminal)
- Superseded (terminal)

## Transitions

| From     | To         | Precondition                                       |
|----------|------------|----------------------------------------------------|
| Proposed | Accepted   | verified: accepted; human: approved                |
| Proposed | Rejected   | human: rejected                                    |
| Accepted | Superseded | field superseded-by is set; human: approved        |

Preconditions use the forms of `dsl.md`, **Entities › Preconditions**.

## Verification

- `accepted`: Context, Decision and Consequences are present; the Decision states one decision in a form that can be followed without further interpretation; the Consequences name at least one effect on the project.
- `rejected`: any of the above does not hold; each failing point is named.

## Relations

- `supersedes`: the earlier ADR that this ADR replaces.
- `superseded-by`: the later ADR that replaces this ADR.

## Permitted changes by delegated work

Delegated work may edit an ADR while it is `Proposed`, and must not change `id`, `type`, `status` or `date`. On an `Accepted` ADR it may only set `superseded-by`; the Decision is never edited, the ADR is superseded by a new ADR instead.

## Invariants

- An ADR with `superseded-by` set is `Superseded`, and the target ADR has `supersedes` pointing back.
- An `Accepted` ADR's Decision does not change.
