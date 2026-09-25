# X01 — Authoring: one auto-resolvable decision

## Task
Write go_harness DSL for the following requirement:

"Delegate the implementation and verify it. Then a merge decision is needed. The agent may make the merge decision itself when it is clearly determined by the available information and criteria; otherwise a human must be asked "Merge this change?". If the decision is to merge, transition to state "Merged". If the decision is not to merge, transition to state "Rework". If the human gives no usable answer, transition to state "Blocked" and stop."

Output the DSL in a code block, then list every assumption you had to make.

## Expected
Canonical (variant form):
```text
DELEGATE implementation
VERIFY implementation
AUTO HITL:merge("Merge this change?")
  → FALLBACK
      → TRANSITION "Blocked"
      → STOP
WHEN merge.approved
  → TRANSITION "Merged"
WHEN merge.rejected
  → TRANSITION "Rework"
```
- D1 AUTO is written in exactly the variant's form and is attached to the merge HITL. **Critical: any other placement is a form error.**
- D2 The HITL is named, and two WHENs test `<name>.<answer>` for the same name. The answer words are free (approved/rejected, merge/no-merge…).
- D3 FALLBACK under the HITL, with TRANSITION "Blocked" then STOP. For variant C, `→ AUTO` comes before `→ FALLBACK`.
- D4 No uncertainty condition, and no WHEN or flow inside AUTO.
### Pass rule
D1–D4 in all probes; same structural form.
