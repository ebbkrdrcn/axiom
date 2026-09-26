# Milestone Template

## Fields

| Field    | Required | Format                                        |
|----------|----------|-----------------------------------------------|
| id       | yes      | `MS-` followed by four digits                 |
| type     | yes      | `Milestone`                                   |
| status   | yes      | a status declared by the Milestone Definition |
| code     | yes      | a short label, for example `M0`               |
| requires | no       | identities of Milestones, comma-separated     |

## Sections

| Section       | Required               |
|---------------|------------------------|
| Goal          | yes                    |
| Delivers      | yes                    |
| Exit Criteria | yes, at least one item |
| Notes         | no                     |

## Relations

| Relation | Field    | Target    | Cardinality |
|----------|----------|-----------|-------------|
| requires | requires | Milestone | 0..n        |
