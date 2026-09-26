# Task Template

## Fields

| Field     | Required | Format                                   |
|-----------|----------|------------------------------------------|
| id        | yes      | `TASK-` followed by four digits          |
| type      | yes      | `Task`                                   |
| status    | yes      | a status declared by the Task Definition |
| adr       | no       | identity of an ADR                       |
| milestone | no       | identity of a Milestone                  |

## Sections

| Section             | Required               |
|---------------------|------------------------|
| Description         | yes                    |
| Acceptance Criteria | yes, at least one item |
| Notes               | no                     |

## Relations

| Relation  | Field     | Target    | Cardinality |
|-----------|-----------|-----------|-------------|
| adr       | adr       | ADR       | 0..1        |
| milestone | milestone | Milestone | 0..1        |
