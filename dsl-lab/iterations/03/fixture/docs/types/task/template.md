# Task Template

## Fields

| Field  | Required | Format                                   |
|--------|----------|------------------------------------------|
| id     | yes      | `TASK-` followed by four digits          |
| type   | yes      | `Task`                                   |
| status | yes      | a status declared by the Task Definition |
| adr    | no       | identity of an ADR                       |

## Sections

| Section             | Required               |
|---------------------|------------------------|
| Description         | yes                    |
| Acceptance Criteria | yes, at least one item |
| Notes               | no                     |

## Relations

| Relation | Field | Target | Cardinality |
|----------|-------|--------|-------------|
| adr      | adr   | ADR    | 0..1        |
