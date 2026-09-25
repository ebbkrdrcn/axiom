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

---

### JOIN

Waits for the concurrent flows started by the corresponding `FORK`.

```text
JOIN
```

Execution continues only after all required forked flows have completed.

---

### BREAK

Exits the current `LOOP`.

```text
BREAK
```

`BREAK` does not terminate the entire execution.

`BREAK` may only exit a loop scope.

Use `STOP` to terminate the entire execution.

---

### WAIT

Suspends execution until an external event or response is available.

```text
WAIT
```

`WAIT` does not make a decision and does not imply success or failure.

After the required event or response becomes available, execution continues according to the surrounding flow.

---

### STOP

Terminates execution.

```text
STOP
```

No subsequent statement is executed after `STOP`.

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
HITL("<message>")
```

`HITL` establishes a human decision boundary.

The human response may determine the subsequent flow.

`HITL` must not be silently replaced by an agent decision unless the surrounding definition explicitly permits automatic resolution through `AUTO`.

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

For example, the following is invalid:

```text
AUTO
  WHEN decision.uncertain
    → HITL("Approve?")
```

The DSL runtime determines uncertainty as part of automatic decision resolution.

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

---

# Syntax

## Statement

```text
<keyword> <argument>
```

---

## Scope

Indented statements belong to the preceding scoped construct.

```text
LOOP:<name>
  <statement>
  <statement>
```

---

## Conditional Flow

```text
WHEN <condition>
  → <statement>
  → <statement>
```

The statements following `→` belong to the conditional flow.

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

---

## Flow

Statements execute in declaration order unless an explicit control construct changes the flow.

```text
<statement>
<statement>
<statement>
```

---

## Identifier

```text
<identifier>
```

Identifiers may be used to refer to requirements, results, states, artifacts, or other process-defined entities.

---

## String

```text
"<string>"
```

Strings may be used where human-readable messages, names, or other literal text are required.

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