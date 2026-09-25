# go_harness DSL

## Control

### LOOP

Defines a repeated execution scope.

```text
LOOP:<name>
  ...
```

All statements inside the scope belong to the loop.

The loop continues until `BREAK`, `STOP`, or another explicit control flow terminates it.

`LOOP` does not imply any particular number of iterations.

Execution rules:

- One iteration executes the loop body from its first statement to its last, in declaration order.
- When the last statement of the body has completed, the next iteration starts again at the first statement of the body.
- `BREAK` ends the loop immediately. Execution continues with the first statement after the loop (at the indentation of `LOOP`).
- `STOP` ends the loop and the entire execution.
- `<name>` is a label that documents the loop. No statement refers to it; in particular, `BREAK` takes no loop name.

Example:

```text
LOOP:build
  DELEGATE build
  VERIFY build
  WHEN build.accepted
    → BREAK
EMIT build-report
```

If `VERIFY build` never establishes `build.accepted`, the loop repeats indefinitely and `EMIT build-report` is never reached.

---

### WHEN

Defines a conditional flow.

```text
WHEN <condition>
  → <statement>
  → <statement>
```

The statements following `→` form the flow executed when the condition is satisfied.

`WHEN` is a control construct, not an operation.

`WHEN` does not itself perform work, change state, delegate work, or produce an artifact.

Multiple `WHEN` constructs may describe different outcomes of the same process state.

Execution rules:

- A `WHEN` is evaluated once, when execution reaches it in declaration order. It is not a standing trigger and does not wait for its condition to become true.
- If the condition is satisfied, the statements of its flow execute in order. Afterwards, execution continues with the statement after the `WHEN` construct, unless the flow executed `BREAK` or `STOP`.
- If the condition is not satisfied, the flow is skipped and execution continues with the statement after the `WHEN` construct. An unmatched `WHEN` is not an error; it does not stop, wait, or escalate.
- Each `WHEN` is independent. There is no implicit "else" and no "first match wins": consecutive `WHEN` constructs are evaluated one after another, and every one whose condition is satisfied executes its flow.
- If no `WHEN` matches, no conditional flow executes and execution simply continues.
- The statements after `→` form **one sequential flow**. Several `→` lines under the same `WHEN` do not run concurrently; only `FORK` creates concurrent flows.

Example:

```text
WHEN tests.passed
  → TRANSITION "Review"

WHEN tests.failed
  → TRANSITION "Debugging"
```

---

### FORK

Starts multiple concurrent flows.

```text
FORK
  → <statement>
  → <statement>
```

Each `→` starts an independent flow.

A forked flow consists of the statement associated with that branch and its nested statements.

Example:

```text
FORK
  → DELEGATE security-review
      VERIFY security-review

  → DELEGATE readiness-verification
      VERIFY readiness-verification
```

The branches may execute concurrently.

Use `JOIN` when execution must wait for the concurrent flows to complete.

Execution rules:

- Within one branch, statements execute sequentially in declaration order.
- A branch has completed when its last statement has completed. A `VERIFY` inside a branch that establishes a negative outcome (for example `rejected`) does not abort the branch; the branch still runs to its end.
- If no `JOIN` follows the `FORK`, execution continues immediately with the statement after the `FORK`, while the branches keep running.
- `STOP` inside a branch terminates the entire execution, including all other branches (see `STOP`).

---

### JOIN

Waits for the concurrent flows started by the corresponding `FORK`.

```text
JOIN
```

Execution continues only after all required forked flows have completed.

Execution rules:

- A `JOIN` corresponds to the nearest preceding `FORK` at the same indentation in the same flow that has not already been joined.
- Every branch of that `FORK` is required. The DSL has no syntax for optional branches.
- A branch counts as completed when its last statement has completed, whatever outcomes its `VERIFY` statements established.
- Outcomes established inside the branches remain available to `WHEN` constructs after the `JOIN`.

Example:

```text
FORK
  → DELEGATE unit-tests
      VERIFY unit-tests
  → DELEGATE integration-tests
      VERIFY integration-tests
JOIN
WHEN unit-tests.accepted
  → TRANSITION "Ready"
```

`JOIN` waits until both branches have completed, including a branch whose `VERIFY` established `rejected`. Then the `WHEN` is evaluated.

---

### BREAK

Exits the current `LOOP`.

```text
BREAK
```

`BREAK` does not terminate the entire execution.

`BREAK` may only exit a loop scope.

Use `STOP` to terminate the entire execution.

Rules:

- "The current `LOOP`" is the innermost `LOOP` that encloses the `BREAK`. With nested loops, only the innermost loop is exited.
- `BREAK` takes effect immediately: the remaining statements of the current iteration, including any later `WHEN` constructs in the loop body, are not executed.
- A `BREAK` that is not inside any `LOOP` is invalid. A program containing it is not well-formed.

Invalid:

```text
VERIFY implementation
WHEN implementation.rejected
  → BREAK
```

(There is no enclosing `LOOP`.)

---

### WAIT

Suspends execution until an external event or response is available.

```text
WAIT
```

`WAIT` does not make a decision and does not imply success or failure.

After the required event or response becomes available, execution continues according to the surrounding flow.

Clarifications:

- `WAIT` takes no argument. The DSL does not name the awaited event; the surrounding process and the runtime determine it (see Semantic Principles).
- After `WAIT` ends, the next statement in declaration order executes.
- The DSL defines no timeout for `WAIT`. If the event never becomes available, execution remains suspended at the `WAIT`.

---

### STOP

Terminates execution.

```text
STOP
```

No subsequent statement is executed after `STOP`.

`STOP` terminates the **entire** execution, not only the flow that contains it:

- inside a `LOOP`, it ends the loop and everything after it;
- inside a `FORK` branch, it also ends every other running branch. A pending `JOIN` never completes, and no statement after it executes.

`STOP` is not required at the end of a process. When the last top-level statement has completed, execution ends normally.

---

# Agentic Operations

### REQUIRE

Declares information, context, state, or another condition required for subsequent execution.

```text
REQUIRE <requirement>
```

`REQUIRE` describes **what is required**, not how it is obtained.

For example:

```text
REQUIRE repository
```

does not prescribe filesystem access, RAG, indexing, a watcher, or any other implementation mechanism.

The requirement must be satisfied before execution continues.

If a required condition cannot be satisfied, execution must not proceed as if the requirement were satisfied.

This means:

- no statement after the `REQUIRE` in the same flow executes while the requirement is unsatisfied;
- the agent must not assume, fabricate, or substitute the required item, and must not skip the `REQUIRE`;
- "not as if satisfied" does not permit continuing in a degraded or partial mode.

---

### DELEGATE

Assigns work to an actor.

```text
DELEGATE <work>
```

The statement describes work that another actor is responsible for performing.

`DELEGATE` does not mean that the work is correct, complete, or accepted.

A delegated result may subsequently be evaluated by `VERIFY`.

Example:

```text
DELEGATE implementation
VERIFY implementation
```

---

### VERIFY

Evaluates a result against the applicable acceptance criteria.

```text
VERIFY <result>
```

`VERIFY` is an evaluation operation.

Completion of delegated work is not equivalent to successful verification.

Verification may establish outcomes that can be used by `WHEN`.

Example:

```text
VERIFY implementation

WHEN implementation.accepted
  → BREAK

WHEN implementation.rejected
  → DELEGATE correction
```

`VERIFY` must not silently modify the result it evaluates.

`VERIFY` does not branch by itself. Execution continues with the next statement whatever the outcome; only a `WHEN` makes the flow depend on the outcome. A `VERIFY` with no `WHEN` after it does not gate the process.

---

### TRANSITION

Changes the current process state.

```text
TRANSITION <state>
```

`TRANSITION` represents a state change, not execution of work.

For example:

```text
TRANSITION "Code Review"
```

means that the process has moved to the `Code Review` state.

It does not mean "perform code review".

The process has exactly one current state. Each `TRANSITION` replaces it, so the most recently executed `TRANSITION` determines the current state. Two `TRANSITION` statements executed in sequence are not a conflict: the second one wins.

---

### EMIT

Produces an output or artifact defined by the surrounding process.

```text
EMIT <artifact>
```

`EMIT` represents an externally meaningful output.

The DSL does not prescribe how the artifact is created, stored, or transmitted.

Example:

```text
EMIT source-code
EMIT test-report
```

---

# Human Interaction

### HITL

Requests a decision, input, or action from a human.

```text
HITL:<name>("<message>")
HITL("<message>")
```

`HITL` establishes a human decision boundary.

The human response may determine the subsequent flow.

`<name>` names the decision. The response establishes the outcome `<name>.<answer>`, where `<answer>` is one of the answers tested by the `WHEN <name>.<answer>` constructs that follow. A response that corresponds to none of these answers is insufficient (see `FALLBACK`). The name may be omitted when no `WHEN` refers to the decision.

`HITL` must not be silently replaced by an agent decision unless that `HITL` is explicitly marked with `AUTO` (see `AUTO`).

The flow containing a `HITL` waits at the `HITL` until either a usable response is available or its `FALLBACK` flow is used (see `FALLBACK`). With a usable response, execution continues with the next statement after the `HITL` construct.

---

### AUTO

Allows a decision to be resolved automatically when the decision is sufficiently determined by the available information, criteria, and authority.

`AUTO` is not a request to guess.

Automatic resolution is permitted only when the agent can determine a single protocol-compatible decision from the available information and applicable criteria.

Uncertainty exists when the agent cannot reliably determine that decision.

Examples include:

- required information is missing or contradictory;
- applicable criteria are missing, ambiguous, or contradictory;
- multiple materially different decisions remain reasonably compatible with the available evidence and criteria;
- the result depends on an unresolved interpretation;
- the agent does not have the authority required to make the decision.

A confidence score alone does not establish certainty.

When the decision is uncertain or outside the agent's authority, human input is required.

Therefore, `AUTO` means:

> Resolve automatically when sufficiently determined; otherwise require human input.

`AUTO` is not a control-flow container.

It does not contain `WHEN`, `→`, or an arbitrary flow.

Uncertainty is not a DSL condition, state, variable, or keyword.

Syntax:

```text
AUTO HITL:<name>("<message>")
```

`AUTO` is written directly before `HITL`, on the same line. It marks that one `HITL` as automatically resolvable. `AUTO` is not a statement of its own and applies to no other statement. `AUTO` applies only to `HITL`.

Execution:

| `AUTO` on this `HITL`? | Decision sufficiently determined? | What happens |
|---|---|---|
| no | — | The human is asked. The agent must not decide. |
| yes | yes | The agent resolves the decision. The human is **not** asked. The outcome `<name>.<answer>` is established exactly as if a human had given that answer. |
| yes | no (uncertain, or outside the agent's authority) | The human is asked, as for a `HITL` without `AUTO`. |

After the decision is made, by the agent or by the human, execution continues with the statement after the `HITL` construct. `FALLBACK` is used only if the human is asked and the response is unavailable or insufficient.

Example:

```text
DELEGATE dependency-upgrade
VERIFY dependency-upgrade
AUTO HITL:merge("Merge the dependency upgrade?")
WHEN merge.approved
  → TRANSITION "Merged"
WHEN merge.declined
  → TRANSITION "Deferred"
```

- If the process's merge criteria clearly determine "approve", the agent establishes `merge.approved` without asking anyone. Then `TRANSITION "Merged"` executes.
- If the information is contradictory or the criteria do not cover the case, the human is asked "Merge the dependency upgrade?". Their answer establishes `merge.approved` or `merge.declined`.

Invalid, because `AUTO` applies only to `HITL`:

```text
AUTO DELEGATE implementation
```

Also invalid, because `AUTO` never contains a flow and uncertainty is not a condition:

```text
AUTO
  WHEN decision.uncertain
    → HITL("Approve?")
```

The DSL runtime determines uncertainty as part of automatic decision resolution.

`AUTO` and `FALLBACK` are different mechanisms. When `AUTO` cannot resolve a decision, the decision goes to the human through the normal `HITL`; this is not a fallback. `FALLBACK` applies only afterwards, if the human's response is unavailable or insufficient.

---

### FALLBACK

Defines the flow to use when an expected response is unavailable or insufficient.

```text
HITL("<message>")
  → FALLBACK
      → <flow>
```

`FALLBACK` is associated with response handling.

It does not mean "execute this flow after the normal flow".

The fallback flow is used only when the expected response cannot be used to continue the normal flow.

`FALLBACK` does not authorize the agent to invent a replacement decision.

A fallback may explicitly terminate, defer, request another action, or otherwise handle the unresolved situation according to the surrounding process.

When the fallback flow is used:

- **Unavailable** means no response arrives. The DSL has no timeout syntax; the runtime decides when a missing response counts as unavailable.
- **Insufficient** means a response arrives but does not provide the requested decision or input. Examples are "I haven't looked yet", an off-topic reply, or an answer to a different question.
- A usable response never triggers the fallback flow.

Form: the fallback flow is written like a `WHEN` flow. It is one sequential flow, and the statements run in order. The following two forms are equivalent:

```text
HITL("Approve the release notes?")
  → FALLBACK
      → TRANSITION "Blocked"
      → STOP
```

```text
HITL("Approve the release notes?")
  → FALLBACK
      → TRANSITION "Blocked"
        STOP
```

Both mean: first `TRANSITION "Blocked"`, then `STOP`. Several `→` lines under `FALLBACK` are **not** concurrent branches.

Statements after the `HITL` construct, at the indentation of `HITL`, are the normal flow. They are not part of the fallback flow.

---

# Syntax

## Statement

Each statement occupies one line and starts with a keyword. The statement forms are:

| Form | Keywords |
|---|---|
| `<keyword> <argument>` | `REQUIRE`, `DELEGATE`, `VERIFY`, `TRANSITION`, `EMIT` |
| `<keyword>` (no argument) | `JOIN`, `BREAK`, `WAIT`, `STOP`, `FORK` |
| `LOOP:<name>` | `LOOP` |
| `WHEN <condition>` | `WHEN` |
| `[AUTO] HITL[:<name>]("<message>")` | `HITL`, `AUTO` |
| `→ FALLBACK` (only directly under a `HITL`) | `FALLBACK` |

An `<argument>` is an identifier or a string.

---

## Scope

Indented statements belong to the preceding scoped construct.

```text
LOOP:<name>
  <statement>
  <statement>
```

Indentation rules:

1. Indentation uses spaces. Only relative depth matters, not the number of spaces.
2. A line belongs to the nearest preceding line that is indented **less** than it. That line is its parent.
3. A scope ends at the first following line indented at the same depth as, or less than, the line that opened it.
4. These lines may have indented children: `LOOP`, `WHEN`, `FORK`, `HITL` (only for `→ FALLBACK`), `→ FALLBACK`, and every `→` item.
5. Lines indented under a `→` item belong to that item. They continue the item's flow (under `WHEN`/`FALLBACK`) or the item's branch (under `FORK`). By convention they are aligned with the text after `→ `.
6. Any other indentation is invalid. This includes an indented line under a plain statement that is not a `→` item, and a `→` line that is not directly under `WHEN`, `FORK`, `FALLBACK`, or `HITL`.

Any statement, including `LOOP`, `WHEN`, `FORK`, `JOIN`, and `HITL`, may appear inside a loop body, a `WHEN` flow, a fallback flow, or a `FORK` branch, unless a rule in this specification says otherwise.

---

## The arrow `→`

`→` introduces an item under a construct. What it means depends on that construct:

| Parent | Meaning of each `→` item |
|---|---|
| `WHEN` | the next step of **one sequential** conditional flow |
| `FALLBACK` | the next step of **one sequential** fallback flow |
| `FORK` | the start of a **separate concurrent** branch |
| `HITL` | only `→ FALLBACK`, which attaches the fallback |

---

## Conditional Flow

```text
WHEN <condition>
  → <statement>
  → <statement>
```

The statements following `→` belong to the conditional flow.

Nested lines under a `→` item also belong to the conditional flow and run in order. Given:

```text
WHEN review.rejected
  → DELEGATE correction
      VERIFY correction
  → TRANSITION "Rework"
EMIT review-report
```

the conditional flow is `DELEGATE correction`, `VERIFY correction`, `TRANSITION "Rework"`, executed sequentially in that order. `EMIT review-report` is outside the `WHEN` and executes afterwards in either case.

`<condition>` has the form `<identifier>.<identifier>`, for example `implementation.accepted`.

---

## Forked Flow

```text
FORK
  → <statement>
      <statement>
      ...
  → <statement>
      <statement>
      ...
```

Each `→` introduces one independent branch.

Indented statements following a branch belong to that branch until the branch scope ends.

A `JOIN` is written after the `FORK` block, at the indentation of `FORK`.

---

## Flow

Statements execute in declaration order unless an explicit control construct changes the flow.

```text
<statement>
<statement>
<statement>
```

A statement starts only after the previous statement in the same flow has completed. Only `FORK` creates concurrency.

---

## Identifier

```text
<identifier>
```

Identifiers may be used to refer to requirements, results, states, artifacts, or other process-defined entities.

An identifier consists of letters, digits, `-`, and `_`, and starts with a letter. A `.` is not part of an identifier; it separates the two parts of a condition.

---

## String

```text
"<string>"
```

Strings may be used where human-readable messages, names, or other literal text are required.

---

## Programs, fragments, and validity

- A **program** is a complete DSL text. Validity is judged on the program as written. A construct is not assumed to be enclosed in a scope that is not shown.
- Templates written with `<...>` placeholders show a form; they are not programs.
- A program that violates a rule stated as "invalid", "may only", or "must not contain" in this specification is **not well-formed**. It must be rejected as a whole; it is not executed with the offending part skipped.

---

## Grammar (EBNF)

`INDENT` and `DEDENT` stand for "one level deeper" and "back to the enclosing level", as defined by the indentation rules in **Scope**.

```ebnf
program     = block ;
block       = statement , { statement } ;               (* same indentation *)
statement   = loop | when | fork | hitl | simple ;

loop        = "LOOP:" , identifier , NL , INDENT , block , DEDENT ;
when        = "WHEN" , condition , NL , INDENT , flow , DEDENT ;
fork        = "FORK" , NL , INDENT , branch , { branch } , DEDENT ;
hitl        = [ "AUTO" ] , "HITL" , [ ":" , identifier ] , "(" , string , ")" , NL ,
              [ INDENT , "→" , "FALLBACK" , NL , INDENT , flow , DEDENT , DEDENT ] ;

flow        = item , { item } ;                          (* items run sequentially *)
branch      = item ;                                     (* each branch runs concurrently *)
item        = "→" , statement , [ INDENT , block , DEDENT ] ;

simple      = ( "REQUIRE" | "DELEGATE" | "VERIFY" | "TRANSITION" | "EMIT" ) , argument , NL
            | ( "JOIN" | "BREAK" | "WAIT" | "STOP" ) , NL ;
argument    = identifier | string ;
condition   = identifier , "." , identifier ;
identifier  = letter , { letter | digit | "-" | "_" } ;
string      = '"' , { character - '"' } , '"' ;
```

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