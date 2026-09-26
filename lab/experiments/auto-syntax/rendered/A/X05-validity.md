# X05 — Interpretation: validity of AUTO placements

## Task
For each snippet, answer VALID or INVALID and cite the rule from the specification.

Snippet 1:
```text
AUTO HITL:deploy("Deploy to production?")
WHEN deploy.yes
  → EMIT deployment
```

Snippet 2:
```text
AUTO DELEGATE implementation
VERIFY implementation
```

Snippet 3:
```text
HITL:deploy("Deploy to production?") AUTO
WHEN deploy.yes
  → EMIT deployment
```

Snippet 4:
```text
AUTO
  WHEN decision.uncertain
    → HITL("Approve?")
```

## Expected
- D1 Snippet 1 VALID (the variant's form).
- D2 Snippet 2 INVALID (AUTO applies only to HITL).
- D3 Snippet 3 INVALID (not the variant's form).
- D4 Snippet 4 INVALID (AUTO contains no flow; uncertainty is not a condition).
### Pass rule
D1–D4 in all probes.
