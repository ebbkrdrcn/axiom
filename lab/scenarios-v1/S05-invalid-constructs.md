# S05 — Interpretation: validity of WHEN inside AUTO, BREAK outside LOOP

Type: interpretation · Edge cases: invalid construct (WHEN inside AUTO), BREAK scope

## Task
For each of the following go_harness DSL snippets, answer VALID or INVALID, cite the rule from the specification, and explain what is wrong or what would happen.

Snippet A:
```text
HITL("Approve release?")
AUTO
  WHEN decision.uncertain
    → HITL("Approve release?")
```

Snippet B:
```text
DELEGATE implementation
VERIFY implementation
WHEN implementation.rejected
  → BREAK
```

## Expected
### Determined by spec
- D1 A is INVALID: AUTO is not a control-flow container and cannot contain WHEN or `→`; uncertainty is not a DSL condition/state/variable; the runtime determines uncertainty. The spec shows this exact pattern as invalid. (AUTO)
- D2 B is INVALID: BREAK exits the current LOOP and "may only exit a loop scope"; there is no enclosing LOOP. (BREAK)

### Underdetermined (→ findings)
- U1 What the correct replacement for A looks like (AUTO syntax) (F-01). Not required for pass.
- U2 The spec does not literally say "BREAK outside a loop is invalid"; probes may read it as a no-op or a runtime error (F-14).

### Pass rule
D1 and D2 in all probes.
