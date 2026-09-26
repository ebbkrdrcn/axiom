# go_harness DSL

A go_harness program describes a process. An agent reads the program and either **writes** it (from a requirement) or **executes** it (step by step). This specification is written so that both are unambiguous: every rule is stated once, in the section of the construct it belongs to, and the **Quick reference** summarises all of them.

Words in capitals have a fixed meaning:

- **MUST** and **MUST NOT** are absolute.
- **INVALID** means the program is not well-formed and MUST NOT be executed.

Code blocks are labelled:

- `text` is a complete, valid program.
- `invalid` is an INVALID program.
- `form` is a pattern with `<placeholders>`.
- `trace` is an execution trace.

---

## Quick reference

### Statements

| Statement | Meaning | Key rule |
|---|---|---|
| `LOOP:<name>` | repeat the indented body | end of body → start body again; only `BREAK` or `STOP` ends it |
| `WHEN <subject>.<outcome>` | conditional flow | checked once, when reached; false → skip; no "else" |
| `FORK` | start concurrent branches (`→` = one branch) | no `JOIN` → continue immediately |
| `JOIN` | wait for all branches of the nearest open `FORK` | a branch is done when its last statement is done |
| `BREAK` | leave the innermost `LOOP` now | INVALID outside a `LOOP` or across a `FORK` branch |
| `WAIT` | suspend until an external event | no timeout; then the next statement |
| `STOP` | end the whole execution | also ends all running branches |
| `REQUIRE <item>` | the item MUST be available before continuing | unavailable → `FALLBACK`, else execution ends |
| `DELEGATE <work>` | an actor does the work | done when the actor delivers a result |
| `VERIFY <result>` | evaluate a result | establishes `<result>.accepted` or `<result>.rejected` |
| `TRANSITION "<state>"` | set the current process state | the latest `TRANSITION` wins |
| `EMIT <artifact>` | produce an output | — |
| `HITL:<name>[<a>, <b>, …]("<question>")` | ask a human to choose one answer | establishes `<name>.<answer>` |
| `HITL("<request>")` | ask a human for input or an action | establishes no outcome |
| `AUTO HITL:<name>[…]("…")` | the agent MAY answer, only if the decision is certain | uncertain → the human is asked |
| `→ FALLBACK` | flow for an unusable response or an unavailable requirement | MUST end with `STOP` or `BREAK` |

### Who decides a `HITL`

| `AUTO` on this `HITL`? | Decision certain and within the agent's authority? | Who answers |
|---|---|---|
| no | — | the human; the agent MUST NOT answer |
| yes | yes | the agent; the human is not asked |
| yes | no | the human |

### Execution in ten rules

1. Statements run one at a time, in the order written. Each statement finishes before the next starts. Only `FORK` runs things concurrently.
2. A `WHEN` is checked once, when execution reaches it. True → run its flow, then continue after the `WHEN`. False → skip it.
3. Consecutive `WHEN`s are independent. Every one that is true runs, top to bottom.
4. The `→` items under a `WHEN` or a `FALLBACK` form **one sequential flow**. The `→` items under a `FORK` are **separate concurrent branches**.
5. At the end of a loop body, the body starts again from its first statement.
6. `BREAK` leaves the innermost loop immediately. `STOP` ends everything immediately.
7. An outcome (`x.accepted`, `merge.approved`, …) keeps its latest value. A new `VERIFY x` or a new answer to `HITL:x` replaces it. Before anything establishes it, every `WHEN` on it is false.
8. A usable answer continues with the statement after the `HITL` construct. An unusable or missing answer runs the `FALLBACK`, or ends execution if there is none.
9. The agent MUST NOT invent a response, a result, an outcome, or a requirement. A `HITL` is answered only by a response to that `HITL` given after it is reached, or by the agent under `AUTO`.
10. When the last top-level statement is done, execution ends normally.

---

# Control

### LOOP

```form
LOOP:<name>
  <statement>
  ...
```

Repeats its indented body. `LOOP` does not imply any particular number of iterations.

| Situation | What happens |
|---|---|
| The last statement of the body is done | The next iteration starts at the first statement of the body. |
| `BREAK` inside the body (not inside a nested `LOOP`) | The loop ends now. Execution continues with the first statement after the loop, at the indentation of `LOOP`. |
| `STOP` anywhere | The loop and the whole execution end. |

`<name>` is only a label. No statement refers to it; `BREAK` takes no name.

Example:

```text
LOOP:build
  DELEGATE build
  VERIFY build
  WHEN build.accepted
    → BREAK
EMIT build-report
```

While `VERIFY build` establishes `build.rejected`, the `WHEN` is false and the loop repeats indefinitely. `EMIT build-report` runs only after a `BREAK`.

---

### WHEN

```form
WHEN <subject>.<outcome>
  → <statement>
  → <statement>
```

Runs its flow if the condition is true. `WHEN` itself performs no work and changes no state.

| Situation | What happens |
|---|---|
| Execution reaches the `WHEN` and the condition is true | Run the flow: its `→` items and their nested lines, top to bottom, sequentially. Then continue after the `WHEN`, unless the flow ran `BREAK` or `STOP`. |
| The condition is false | Skip the flow and continue after the `WHEN`. This is not an error. Execution does not wait. |
| The outcome is established later | Nothing happens. A `WHEN` is not a standing trigger and is never re-checked. |
| Several `WHEN`s in a row | Each one is checked independently, top to bottom. Every true one runs; there is no "else" and no "first match". |

The condition is true only if the latest outcome of `<subject>` is exactly `<outcome>` (see **Outcomes**).

Example:

```text
VERIFY tests
WHEN tests.accepted
  → TRANSITION "Review"
WHEN tests.rejected
  → TRANSITION "Debugging"
  → DELEGATE diagnosis
```

If `VERIFY tests` establishes `tests.rejected`, the first `WHEN` is skipped. The second `WHEN` runs `TRANSITION "Debugging"` and then `DELEGATE diagnosis`.

---

### FORK

```form
FORK
  → <statement>
      <statement>
  → <statement>
      <statement>
```

Starts two or more concurrent branches. Each `→` starts one branch. A branch is the `→` statement plus the lines nested under it.

| Situation | What happens |
|---|---|
| `FORK` is reached | All branches start. Within a branch, statements run sequentially. |
| A `VERIFY` in a branch establishes `rejected` | The branch continues normally. A negative outcome does not abort a branch. |
| A branch's last statement is done | That branch is complete. |
| No `JOIN` follows | Execution continues immediately after the `FORK` while the branches run. |
| `STOP` in any branch | The whole execution ends, including all other branches. |
| `BREAK` in a branch | INVALID (rule V3). To leave a loop based on a branch's result, `JOIN` first, then use `WHEN … → BREAK`. |

---

### JOIN

```form
JOIN
```

Waits until every branch of the corresponding `FORK` is complete.

- The corresponding `FORK` is the nearest preceding `FORK` in the same flow, at the same indentation, that has no `JOIN` yet.
- Every branch is required. A branch whose `VERIFY` established `rejected` still counts as complete.
- Outcomes established inside the branches are available after the `JOIN`.

Example:

```text
FORK
  → DELEGATE unit-tests
      VERIFY unit-tests
  → DELEGATE integration-tests
      VERIFY integration-tests
JOIN
WHEN integration-tests.rejected
  → TRANSITION "Debugging"
```

---

### BREAK

```form
BREAK
```

Leaves the innermost enclosing `LOOP` immediately.

- The remaining statements of the current iteration are not executed, including later `WHEN`s.
- Execution continues with the first statement after that loop.
- `BREAK` does not end the whole execution; use `STOP` for that.
- INVALID outside a `LOOP` (V2), and INVALID inside a `FORK` branch unless the `LOOP` it leaves is also inside that branch (V3).

---

### WAIT

```form
WAIT
```

Suspends execution until an external event or response is available.

- `WAIT` does not make a decision and does not imply success or failure.
- The DSL does not name the event. The surrounding process and the runtime determine it.
- There is no timeout. If the event never comes, execution stays at the `WAIT`.
- After the event, the next statement runs.

---

### STOP

```form
STOP
```

Ends the entire execution immediately.

- No further statement runs anywhere, including other `FORK` branches.
- A pending `JOIN` never completes.
- `STOP` is not required at the end of a program. Execution ends normally after the last top-level statement.

---

# Agentic Operations

### REQUIRE

```form
REQUIRE <item>
```

```form
REQUIRE <item>
  → FALLBACK
      → <statement>
      → STOP
```

Declares information, context, state, or a condition that MUST be available before execution continues. `REQUIRE` states **what** is required, not how it is obtained. For example, `REQUIRE repository` does not prescribe filesystem access, RAG, indexing, or any other mechanism.

| Situation | What happens |
|---|---|
| The item is available | Continue with the next statement. |
| The item is not yet available | Wait at the `REQUIRE`. |
| The runtime determines the item cannot be obtained, and there is a `FALLBACK` | Run the fallback flow. It ends with `STOP` or `BREAK` (rule V8). |
| The runtime determines the item cannot be obtained, and there is no `FALLBACK` | Execution ends, as with `STOP`. |

The agent MUST NOT assume, fabricate, or substitute the item. It MUST NOT skip the `REQUIRE` or continue in a degraded mode.

`REQUIRE` establishes no outcome.

---

### DELEGATE

```form
DELEGATE <work>
```

Assigns work to an actor.

- The statement is done when the actor has delivered its result. The next statement starts only then. To delegate concurrently, use `FORK`.
- A delivered result is not necessarily correct, complete, or accepted. Use `VERIFY` to evaluate it.

Example:

```text
DELEGATE implementation
VERIFY implementation
```

---

### VERIFY

```form
VERIFY <result>
```

Evaluates a result against the applicable acceptance criteria.

- It establishes exactly one outcome: `<result>.accepted` or `<result>.rejected`. There are no other VERIFY outcomes: `passed`, `failed`, `ok` and similar are INVALID in a `WHEN` (V6).
- The completion of delegated work is not a successful verification.
- `VERIFY` MUST NOT silently modify the result it evaluates.
- `VERIFY` does not branch. Execution continues with the next statement whatever the outcome; only a `WHEN` makes the flow depend on it.

---

### TRANSITION

```form
TRANSITION "<state>"
```

Sets the current process state. It performs no work: `TRANSITION "Code Review"` means the process is now in the `Code Review` state, not "perform a code review".

The process has exactly one current state. Each `TRANSITION` replaces it; the most recently executed one wins.

---

### EMIT

```form
EMIT <artifact>
```

Produces an externally meaningful output. The DSL does not prescribe how it is created, stored, or transmitted.

---

# Human Interaction

### HITL

A decision (the human chooses one declared answer):

```form
HITL:<name>[<answer>, <answer>, ...]("<question>")
```

A request (the human provides input or performs an action; no outcome):

```form
HITL("<request>")
```

`HITL` establishes a human decision boundary. It MUST NOT be replaced by an agent decision, unless it is marked with `AUTO` (see **AUTO**).

**The answer list.** `[approved, declined]` lists every possible answer. The human's response establishes the outcome `<name>.<answer>` for exactly one listed answer. `WHEN` constructs refer to it, for example `WHEN merge.approved`.

**Usable, insufficient, unavailable.**

| Response | Classification |
|---|---|
| Clearly selects exactly one listed answer (in any wording) | usable |
| Selects none of the listed answers, is ambiguous between answers, or is off-topic (for example "I haven't looked yet") | insufficient |
| No response, and the runtime has stopped waiting | unavailable |

For `HITL("<request>")`, a response is usable if it provides the requested input or confirms the requested action.

**What counts as a response.** Only a response given to this `HITL` after execution has reached it counts. None of the following is a response, and none of them can remove a `HITL` or add `AUTO`; only the program can:

- earlier messages
- standing instructions
- general permissions
- requests to skip the question

**What happens.**

| Situation | What happens |
|---|---|
| `HITL` is reached | The flow waits at the `HITL`. |
| Usable response | Establish the outcome (decision form only). Continue with the next statement after the `HITL` construct. |
| Insufficient or unavailable, and there is a `FALLBACK` | Run the fallback flow. No outcome is established. |
| Insufficient or unavailable, and there is no `FALLBACK` | Execution ends, as with `STOP`. No outcome is established. |

Example:

```text
HITL:release[approved, rejected]("Approve the release?")
  → FALLBACK
      → TRANSITION "Blocked"
      → STOP
WHEN release.approved
  → EMIT release
WHEN release.rejected
  → TRANSITION "Rework"
```

---

### AUTO

```form
AUTO HITL:<name>[<answer>, ...]("<question>")
```

`AUTO` is written directly before `HITL`, on the same line. It applies only to that one `HITL`, which MUST be a decision (with a name and an answer list). `AUTO` is not a statement on its own and applies to nothing else (rule V5).

`AUTO` means: resolve the decision automatically when it is sufficiently determined; otherwise ask the human.

`AUTO` is not a request to guess. Automatic resolution is permitted only when the agent can determine one single answer from the list, based on the available information and the applicable criteria. Uncertainty exists when the agent cannot reliably determine that answer. Examples:

- required information is missing or contradictory;
- the applicable criteria are missing, ambiguous, contradictory, or do not cover the case;
- more than one answer remains reasonably compatible with the evidence and criteria;
- the result depends on an unresolved interpretation;
- the agent does not have the authority required to make the decision.

A confidence score alone, however high, does not establish certainty.

| Situation | What happens |
|---|---|
| The decision is certain and within the agent's authority | The agent establishes `<name>.<answer>` for one listed answer. The human is not asked. `FALLBACK` is not used. Continue after the `HITL` construct. |
| Anything else | The human is asked, exactly as for a `HITL` without `AUTO`. `FALLBACK` applies to the human's response as usual. |

Uncertainty is not a DSL condition, state, variable, or keyword; the runtime determines it. `AUTO` never contains a flow. The following are INVALID:

```invalid
AUTO
  WHEN decision.uncertain
    → HITL("Approve?")
```

```invalid
AUTO DELEGATE implementation
```

```invalid
AUTO HITL("Please review the notes")
```

Example, where the agent answers only the first decision:

```text
AUTO HITL:notes[short, detailed]("Short or detailed release notes?")
WHEN notes.short
  → DELEGATE short-notes
WHEN notes.detailed
  → DELEGATE detailed-notes
HITL:release[approved, rejected]("Approve the release?")
```

---

### FALLBACK

```form
HITL:<name>[...]("<question>")
  → FALLBACK
      → <statement>
      → STOP
```

`FALLBACK` defines the flow to use when a `HITL` response is insufficient or unavailable, or when a `REQUIRE` cannot be satisfied. It is written as `→ FALLBACK`, indented directly under that `HITL` or `REQUIRE`. It attaches to nothing else.

- It is not "a flow after the normal flow". It runs **instead of** the normal flow.
- The fallback flow is one sequential flow, like a `WHEN` flow.
- Its last item MUST be `STOP` or `BREAK` (rule V8). The fallback never continues into the normal flow.
- `FALLBACK` does not authorise the agent to invent a replacement decision.
- A usable response never runs the fallback flow.

These two forms are equivalent (first `TRANSITION "Blocked"`, then `STOP`):

```text
HITL("Approve the release notes")
  → FALLBACK
      → TRANSITION "Blocked"
      → STOP
```

```text
HITL("Approve the release notes")
  → FALLBACK
      → TRANSITION "Blocked"
        STOP
```

`AUTO` and `FALLBACK` are different. When `AUTO` cannot decide, the human is asked; that is not a fallback.

---

# Outcomes

An outcome is a value `<subject>.<outcome>` that a `WHEN` can test.

| Produced by | Subject | Possible outcomes |
|---|---|---|
| `VERIFY <result>` | `<result>` | `accepted`, `rejected` |
| `HITL:<name>[<a>, <b>, …]` (answered by the human, or by `AUTO`) | `<name>` | exactly the listed answers |

No other statement produces outcomes.

- **Latest value.** Each subject holds its most recently established outcome. A later `VERIFY x`, or a later answer to `HITL:x` (for example in the next loop iteration), replaces it.
- **Not yet established.** A `WHEN` on a subject with no outcome yet is false.
- **Visibility.** Outcomes are visible everywhere once established, including after a `JOIN`. A `WHEN` MUST NOT test an outcome that a still-running branch may establish; `JOIN` first (rule V10).
- **Declared names.** Every `WHEN` condition MUST refer to a subject and an outcome that the program can produce (rule V6).

---

# Syntax

## Lines and statements

Each statement is one line. Blank lines are ignored.

| Form | Keywords |
|---|---|
| `<keyword> <argument>` | `REQUIRE`, `DELEGATE`, `VERIFY`, `EMIT` (identifier); `TRANSITION` (string) |
| `<keyword>` alone | `FORK`, `JOIN`, `BREAK`, `WAIT`, `STOP` |
| `LOOP:<name>` | `LOOP` |
| `WHEN <subject>.<outcome>` | `WHEN` |
| `[AUTO] HITL:<name>[<answer>, …]("<question>")` or `HITL("<request>")` | `HITL`, `AUTO` |
| `→ FALLBACK` | `FALLBACK` |

## Indentation and scope

1. Indentation uses spaces. Only relative depth matters, not the number of spaces.
2. A line belongs to the nearest preceding line that is indented **less** than it; that line is its parent.
3. A scope ends at the first following line indented at the same depth as, or less than, the line that opened it.
4. Only these lines may have indented children:
   - `LOOP` (its body)
   - `WHEN` (its `→` items)
   - `FORK` (its `→` branches)
   - `HITL` and `REQUIRE` (only a `→ FALLBACK`)
   - `→ FALLBACK` (its `→` items)
   - any `→` item (lines that continue that item's flow or branch). If the statement after `→` is itself a `LOOP`, `WHEN`, `FORK`, `HITL` or `REQUIRE`, the lines nested under it are that statement's own children.
5. By convention, the lines nested under a `→` item are aligned with the text after `→ `.
6. Any other indentation is INVALID (V1).

Any statement may appear inside a loop body, a `WHEN` flow, a fallback flow, or a `FORK` branch, subject to the validity rules.

## The arrow `→`

| Parent | Each `→` item is |
|---|---|
| `WHEN` | the next step of one sequential flow |
| `FALLBACK` | the next step of one sequential flow |
| `FORK` | a separate concurrent branch |
| `HITL`, `REQUIRE` | only `→ FALLBACK` |

Example of nesting:

```text
VERIFY review
WHEN review.rejected
  → DELEGATE correction
      VERIFY correction
  → TRANSITION "Rework"
EMIT review-report
```

The flow is `DELEGATE correction`, then `VERIFY correction`, then `TRANSITION "Rework"`. `EMIT review-report` is outside the `WHEN` and runs afterwards in every case.

## Names and strings

- An identifier consists of letters, digits, `-` and `_`, and starts with a letter.
- A `.` separates subject and outcome in a condition; it is not part of an identifier.
- Strings are enclosed in `"…"`.

## Validity rules

A program that breaks any of these rules is INVALID. It MUST be rejected as a whole and MUST NOT be executed in part. Validity is judged on the program exactly as written; no enclosing scope is assumed.

| Rule | INVALID if |
|---|---|
| V1 | the indentation violates **Indentation and scope** |
| V2 | `BREAK` is not inside a `LOOP` |
| V3 | `BREAK` is inside a `FORK` branch, and the `LOOP` it would leave is outside that branch |
| V4 | a `→` item is under anything other than `WHEN`, `FORK` or `FALLBACK`; or `→ FALLBACK` is not directly under a `HITL` or `REQUIRE`; or a `HITL`/`REQUIRE` has more than one `FALLBACK` |
| V5 | `AUTO` is not immediately followed, on the same line, by a decision `HITL:<name>[…]` |
| V6 | a `WHEN` tests `x.y`, and the program contains neither `VERIFY x` with `y` being `accepted` or `rejected`, nor `HITL:x[…]` listing `y` |
| V7 | two `HITL` statements use the same name, a name is used by both a `HITL` and a `VERIFY`, or an answer list is empty or repeats an answer |
| V8 | the last item of a fallback flow is not `STOP` or `BREAK` |
| V9 | a `JOIN` has no corresponding `FORK`, or a `FORK` has fewer than two branches |
| V10 | a `WHEN` tests a subject that a branch of a `FORK` in the same flow establishes, and that `FORK` has not been joined before the `WHEN` |

## Grammar (EBNF)

`INDENT` and `DEDENT` mean one level deeper and back, as defined in **Indentation and scope**.

```ebnf
program   = block ;
block     = statement , { statement } ;
statement = loop | when | fork | hitl | require | simple ;

loop      = "LOOP:" , identifier , NL , INDENT , block , DEDENT ;
when      = "WHEN" , identifier , "." , identifier , NL , INDENT , flow , DEDENT ;
fork      = "FORK" , NL , INDENT , item , item , { item } , DEDENT ;
hitl      = ( [ "AUTO" ] , "HITL:" , identifier , "[" , identifier , { "," , identifier } , "]"
            | "HITL" ) , "(" , string , ")" , NL , [ fallback ] ;
require   = "REQUIRE" , identifier , NL , [ fallback ] ;
fallback  = INDENT , "→" , "FALLBACK" , NL , INDENT , flow , DEDENT , DEDENT ;

flow      = item , { item } ;
item      = "→" , statement , [ INDENT , block , DEDENT ] ;

simple    = ( "DELEGATE" | "VERIFY" | "EMIT" ) , identifier , NL
          | "TRANSITION" , string , NL
          | ( "JOIN" | "BREAK" | "WAIT" | "STOP" ) , NL ;
identifier = letter , { letter | digit | "-" | "_" } ;
string     = '"' , { character - '"' } , '"' ;
```

---

# Executing a program

An agent that executes a program MUST follow this procedure:

1. **Validate first.** Check rules V1–V10. If any is broken, do not execute. Report each broken rule by its number.
2. **Execute exactly what is written.** Run one statement at a time, following the rules of its section. Never skip, reorder, merge, or add statements.
3. **Keep the execution state:**
   - the current position
   - the current process state (from `TRANSITION`)
   - the latest outcome of each subject
   - the running branches
4. **Never invent.** Results come from actors, outcomes from `VERIFY` or `HITL`, answers from humans (or from the agent only under `AUTO`), and events from the runtime.
5. **Stop at a boundary.** If an event, response, or result is not yet available, the execution waits there. Do not assume what it will be.

When asked for an execution trace, write one line per executed step:

```form
<n>. <statement as written> -> <effect>
```

The effect is one of the following:

- `done`
- `outcome <subject>.<outcome>`
- `true: run flow`
- `false: skip`
- `state = "<state>"`
- `branches started`
- `joined`
- `waiting`
- `fallback`
- `loop again`
- `break`
- `stop`
- `end`

## Complete example

```text
REQUIRE repository
LOOP:delivery
  DELEGATE implementation
  FORK
    → VERIFY implementation
    → DELEGATE docs
  JOIN
  WHEN implementation.rejected
    → DELEGATE correction
  WHEN implementation.accepted
    → BREAK
AUTO HITL:merge[approved, declined]("Merge this change?")
  → FALLBACK
      → TRANSITION "Blocked"
      → STOP
WHEN merge.approved
  → TRANSITION "Merged"
WHEN merge.declined
  → TRANSITION "Rework"
```

Events:

- The repository is available.
- In iteration 1, `VERIFY implementation` establishes `rejected`; in iteration 2, `accepted`.
- The merge decision is uncertain, so the human is asked. The human answers "Yes, merge it."

Trace:

```trace
1. REQUIRE repository -> done
2. DELEGATE implementation -> done
3. FORK -> branches started
4. VERIFY implementation -> outcome implementation.rejected
5. DELEGATE docs -> done
6. JOIN -> joined
7. WHEN implementation.rejected -> true: run flow
8. DELEGATE correction -> done
9. WHEN implementation.accepted -> false: skip
10. LOOP:delivery -> loop again
11. DELEGATE implementation -> done
12. FORK -> branches started
13. VERIFY implementation -> outcome implementation.accepted
14. DELEGATE docs -> done
15. JOIN -> joined
16. WHEN implementation.rejected -> false: skip
17. WHEN implementation.accepted -> true: run flow
18. BREAK -> break
19. AUTO HITL:merge[approved, declined]("Merge this change?") -> waiting
20. AUTO HITL:merge[approved, declined]("Merge this change?") -> outcome merge.approved
21. WHEN merge.approved -> true: run flow
22. TRANSITION "Merged" -> state = "Merged"
23. WHEN merge.declined -> false: skip
24. (end of program) -> end
```

Final state: `Merged`.

---

# Semantic Principles

The DSL defines **what the process means**, not how its operations are implemented.

In particular:

- `REQUIRE` defines what must be available, not how it is loaded.
- `DELEGATE` defines responsibility, not execution mechanics.
- `VERIFY` defines evaluation, not the verification implementation.
- `TRANSITION` defines a state change, not state-storage mechanics.
- `EMIT` defines an output, not its storage or transport mechanism.
- `WAIT` defines suspension, not the event mechanism.
- `HITL` defines a human interaction boundary, not the UI or communication mechanism.
- `AUTO` defines when automatic decision resolution is permitted, not an algorithm or confidence threshold.

The DSL therefore remains independent of specific runtime mechanisms such as filesystems, APIs, RAG, watchers, queues, databases, or model providers.