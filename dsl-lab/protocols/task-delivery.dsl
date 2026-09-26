t:Task = TASK-0100
a:ADR = t.adr
TRANSITION "Specifying"
LOOP:specification
  LOOP:drafting
    DELEGATE spec
    VERIFY spec
      → FALLBACK
          → TRANSITION "Blocked"
          → STOP
    WHEN spec.accepted
      → BREAK
  HITL:spec-review[approved, revise]("Approve the spec of TASK-0100?")
    → FALLBACK
        → TRANSITION "Waiting"
        → STOP
  WHEN spec-review.approved
    → BREAK
TRANSITION t "InProgress"
  → FALLBACK
      → TRANSITION "Blocked"
      → STOP
TRANSITION "Building"
LOOP:delivery
  DELEGATE implementation
  LOOP:check
    VERIFY t
      → FALLBACK
          → TRANSITION "Blocked"
          → STOP
    WHEN t.rejected
      → TRANSITION t "Debugging"
      → DELEGATE diagnosis
      → DELEGATE fix
      → TRANSITION t "InProgress"
    WHEN t.accepted
      → TRANSITION t "Review"
      → BREAK
  TRANSITION "Reviewing"
  HITL:review[approved, changes]("Is TASK-0100 done?")
    → FALLBACK
        → TRANSITION "Waiting"
        → STOP
  WHEN review.approved
    → TRANSITION t "Done"
    → TRANSITION "Done"
    → BREAK
  WHEN review.changes
    → TRANSITION t "InProgress"
    → TRANSITION "Building"
EMIT report
