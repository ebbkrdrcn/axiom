# Convention Template

## Fields

| Field  | Required | Format                                         |
|--------|----------|------------------------------------------------|
| id     | yes      | `CONV-` followed by four digits                |
| type   | yes      | `Convention`                                   |
| status | yes      | a status declared by the Convention Definition |
| scope  | yes      | paths relative to the project root, comma-separated, or `all` |
| check  | yes      | `mechanical` or `review`                       |
| adr    | no       | identity of an ADR                             |

## Sections

| Section      | Required |
|--------------|----------|
| Rule         | yes      |
| Rationale    | yes      |
| How to check | yes      |
| Examples     | no       |

## Relations

| Relation | Field | Target | Cardinality |
|----------|-------|--------|-------------|
| adr      | adr   | ADR    | 0..1        |
