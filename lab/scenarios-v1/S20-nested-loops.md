# S20 — Interpretation: BREAK in nested loops

Type: interpretation · Edge cases: BREAK target, LOOP names (F-14)

## Task
Consider this DSL:
```text
LOOP:release
  LOOP:fix
    DELEGATE fix
    VERIFY fix
    WHEN fix.accepted
      → BREAK
  TRANSITION "Fixed"
  VERIFY release-candidate
  WHEN release-candidate.accepted
    → BREAK
EMIT release
```
1. When `VERIFY fix` establishes `accepted`, which loop does the `BREAK` exit and which statement executes next?
2. Could the author write `BREAK release` inside `LOOP:fix` to leave both loops at once?
3. If `VERIFY release-candidate` establishes `rejected`, what executes next?

## Expected
### Determined by spec
- D1 (Q1) It exits `LOOP:fix` only (innermost); next is `TRANSITION "Fixed"`. (BREAK rules)
- D2 (Q2) No: `BREAK` takes no loop name; the name is only a label. (LOOP, Syntax/Statement)
- D3 (Q3) The WHEN is skipped; the body of `LOOP:release` ends, so the next iteration starts at `LOOP:fix` (i.e. `DELEGATE fix`). (WHEN, LOOP rules)

### Pass rule
D1–D3 in all probes.
