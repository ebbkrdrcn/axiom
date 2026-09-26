# X02 — Authoring: two decisions, only one auto-resolvable (scope)

## Task
Write DSL for the following requirement:

"First ask a human "Short or detailed release notes?". The agent may answer this question itself when the answer is clearly determined. If short, delegate short-notes; if detailed, delegate detailed-notes. Then ask a human "Approve the release?". This approval must always be given by a human, never by the agent. If approved, emit release; if rejected, transition to state "Rework"."

Output the DSL in a code block, then list every assumption you had to make.

## Expected
- D1 AUTO is attached (in the variant's form) to the notes-style HITL only.
- D2 The release-approval HITL carries **no** AUTO. **Critical: AUTO must not be placed so that it could also apply to the approval.**
- D3 Two named HITLs, each followed by its own WHENs on `<name>.<answer>`, in the right order.
### Pass rule
D1–D3 in all probes.
