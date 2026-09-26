# ADR Template

## Fields

| Field         | Required | Format                                  |
|---------------|----------|-----------------------------------------|
| id            | yes      | `ADR-` followed by four digits          |
| type          | yes      | `ADR`                                   |
| status        | yes      | a status declared by the ADR Definition |
| date          | yes      | `YYYY-MM-DD`                            |
| supersedes    | no       | identity of an ADR                      |
| superseded-by | no       | identity of an ADR                      |

## Sections

| Section                 | Required |
|-------------------------|----------|
| Context                 | yes      |
| Decision                | yes      |
| Consequences            | yes      |
| Alternatives Considered | no       |

## Relations

| Relation      | Field         | Target | Cardinality |
|---------------|---------------|--------|-------------|
| supersedes    | supersedes    | ADR    | 0..1        |
| superseded-by | superseded-by | ADR    | 0..1        |
