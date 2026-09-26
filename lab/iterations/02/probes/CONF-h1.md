# Ambiguities and Underspecifications in DSL

## Critical Issues (High Risk of Wrong Execution)

### 1. FALLBACK Flow Termination with Nested Constructs
**Section:** Syntax → Validity rules (Rule V8, line 448)

**Quote:** "Its last item MUST be `STOP` or `BREAK` (rule V8). The fallback never continues into the normal flow."

**Problem:** The rule is ambiguous about what "last item" means when the fallback contains nested constructs. Two interpretations:

- **Interpretation A:** The textually last line of the fallback must be `STOP` or `BREAK`.
- **Interpretation B:** The last statement that could execute in the fallback must be `STOP` or `BREAK`.

**Example causing different execution:**
```
HITL:x[a]("?")
  → FALLBACK
    → LOOP:l
      → DELEGATE work
      → WHEN work.accepted
        → BREAK
```
The textually last line is `BREAK`, which satisfies A. But the BREAK only exits the loop, not the fallback. The fallback then ends—but was this the intended behavior? If the loop never executes (work is never accepted), the fallback terminates with no STOP or BREAK at the fallback level, violating B.

**Result:** Unclear whether this program is valid or where execution stops.

---

### 2. Outcome Visibility and Race Conditions in FORK Branches
**Section:** Outcomes (line 485-486), Execution in ten rules (Rule 7), and Validity rules (Rule V10)

**Quote:** "Outcomes are visible everywhere once established, including after a `JOIN`. A `WHEN` MUST NOT test an outcome that a still-running branch may establish; `JOIN` first (rule V10)."

**Problem:** "Once established" and "still-running branch may establish" are ambiguous about timing:

- **Interpretation A:** An outcome is established the instant a `VERIFY` or `HITL` statement finishes execution. Any `WHEN` reached after that moment sees the outcome, even if the branch is still running.
- **Interpretation B:** An outcome is established only when the branch completes (its last statement is done), making it safe to test after `JOIN`.

**Example causing different behavior:**
```
FORK
  → DELEGATE build
    VERIFY build
    → (more statements in branch)
  → DELEGATE other
    JOIN
  WHEN build.accepted
    → TRANSITION "Success"
```
In interpretation A, the `JOIN` might complete (since `other` finishes), but `build.accepted` was never checked yet, and the WHEN might be tested while the branch is still running additional statements. In interpretation B, `JOIN` waits for both the build verification AND all remaining statements before proceeding.

**Result:** V10 cannot be reliably validated without knowing exactly when establishment occurs.

---

### 3. BREAK and Nested Loop/FORK Relationships
**Section:** Control → BREAK (line 195-200, Rule V3)

**Quote:** "`BREAK` is inside a `FORK` branch, and the `LOOP` it would leave is outside that branch" is INVALID.

**Problem:** The rule is stated as a constraint on BREAK, but it's unclear how it handles multiple levels of nesting:

- **Interpretation A:** BREAK is invalid only if the immediate enclosing loop is outside the FORK.
- **Interpretation B:** BREAK is invalid if ANY enclosing loop (at any nesting depth) is outside the FORK.

**Example causing different validity judgments:**
```
FORK
  → LOOP:inner
    → WHEN x.y
      → LOOP:outer
        → (statement)
        → BREAK
```
Is the BREAK invalid? It would exit `outer`, which is inside the branch. But is there also a reference to `inner` or some outer loop? The rule mentions "the `LOOP` it would leave" (singular) but doesn't specify how to identify it among nested loops.

**Result:** Programs may be incorrectly validated or rejected.

---

### 4. AUTO HITL Resolution Certainty Standards
**Section:** Human Interaction → AUTO (lines 391-404)

**Quote:** "Automatic resolution is permitted only when the agent can determine one single answer from the list, based on the available information and the applicable criteria. Uncertainty exists when... A confidence score alone, however high, does not establish certainty."

**Problem:** "Sufficiently determined" and "certainty" are undefined. Different agents apply different standards:

- **Interpretation A:** Certainty requires 100% confidence that one answer is correct (logical certainty).
- **Interpretation B:** Certainty requires high confidence (e.g., >95%) plus reasonable authority to make the decision.
- **Interpretation C:** Certainty requires that exactly one answer is compatible with the program logic, regardless of external factors.

**Example causing different outcomes:**
```
AUTO HITL:deploy[yes, no]("Deploy to production?")
```
Agent A might determine from CI status that "yes" is correct with 98% confidence but ask the human anyway (interpretation A is conservative). Agent B might auto-answer "yes". Agent C might ask because the program logic doesn't determine either answer.

**Result:** The same program behaves differently depending on the agent's interpretation of "certainty."

---

### 5. Outcome Establishment Timing Within a Statement
**Section:** Executing a program (lines 619-630, trace format)

**Quote:** The trace shows outcomes and statement execution as a single effect: `VERIFY build -> outcome build.rejected`. But the exact moment is not specified.

**Problem:** Two interpretations of when an outcome becomes available:

- **Interpretation A:** The outcome is established after the statement finishes and before the next statement begins.
- **Interpretation B:** The outcome is established during statement execution, potentially visible if another branch reads it mid-statement.

**Example causing race conditions:**
```
FORK
  → VERIFY build
    WHEN build.accepted
      → DELEGATE publish
  → (waiting branch)
    WHEN build.accepted
      → TRANSITION "Ready"
```
If the WHEN in the first branch is evaluated mid-VERIFY (interpretation B), it might see the outcome before it's fully established. If WHEN waits until VERIFY finishes (interpretation A), the behavior is deterministic.

**Result:** Concurrent execution behavior becomes unpredictable.

---

### 6. HITL and DELEGATE Parameter Matching
**Section:** Agentic Operations (lines 266-279)

**Quote:** "`DELEGATE <work>`" and "`VERIFY <result>`" use identifiers, but the spec doesn't define the relationship.

**Problem:** Three interpretations:

- **Interpretation A:** `<work>` and `<result>` can be any identifiers; VERIFY doesn't need to match DELEGATE.
- **Interpretation B:** `VERIFY <result>` must follow `DELEGATE <result>` with matching names (by convention or rule).
- **Interpretation C:** `VERIFY <result>` applies to the most recent DELEGATE, regardless of name.

**Example causing ambiguity:**
```
DELEGATE build
DELEGATE docs
VERIFY build
```
Does VERIFY apply to the build from line 1 (matching name) or docs from line 2 (most recent)? If names are unrelated, which DELEGATE is being verified?

**Result:** Programs are ambiguous about what is being verified.

---

## High-Risk Issues

### 7. Loop Iteration and WHEN Re-evaluation
**Section:** Execution in ten rules (Rule 2, line 58) and Execution rules (Rule 5, line 61)

**Quote:** "A `WHEN` is checked once, when execution reaches it... At the end of a loop body, the body starts again from its first statement."

**Problem:** Does "checked once, when execution reaches it" mean:

- **Interpretation A:** A WHEN is checked every time execution reaches it, including in subsequent loop iterations.
- **Interpretation B:** A WHEN is checked only the first time the program reaches it, and never again (even if the loop iterates).

**Example producing different results:**
```
LOOP:test
  DELEGATE work
  VERIFY work
  WHEN work.accepted
    → TRANSITION "Success"
    → BREAK
TRANSITION "Done"
```
In iteration 1, VERIFY establishes `work.rejected`. The WHEN is false, loop repeats. In iteration 2, VERIFY establishes `work.accepted`. 

Under A: The WHEN is re-checked and is now true, so BREAK executes.
Under B: The WHEN was already checked in iteration 1 and never re-evaluated, so the loop runs forever.

**Result:** Infinite loop vs. correct termination.

---

### 8. Initial Process State
**Section:** Agentic Operations → TRANSITION (line 304-306)

**Quote:** "The process has exactly one current state. Each `TRANSITION` replaces it; the most recently executed one wins."

**Problem:** No initial state is defined.

- **Interpretation A:** Initial state is undefined (null or empty).
- **Interpretation B:** Initial state is an empty string `""`.
- **Interpretation C:** Initial state is implicitly defined by the first TRANSITION in the program.

**Example revealing the ambiguity:**
```
EMIT status-report
```
If EMIT includes the current state and no TRANSITION has run, what state is emitted? Different agents might produce different outputs.

**Result:** Initial execution behavior is undefined.

---

### 9. REQUIRE and Runtime Determination
**Section:** Agentic Operations → REQUIRE (line 248-259)

**Quote:** "Declares information, context, state, or a condition that MUST be available before execution continues... The agent MUST NOT assume, fabricate, or substitute the item. It MUST NOT skip the `REQUIRE` or continue in a degraded mode."

**Problem:** "Available" is ambiguous:

- **Interpretation A:** An item is available if the runtime has it ready now (synchronously).
- **Interpretation B:** An item is available if the runtime can obtain it (asynchronously, with waiting).
- **Interpretation C:** An item is available if it exists anywhere (filesystem, database, cache, etc.).

**Example causing hangs vs. errors:**
```
REQUIRE repository
REQUIRE database-credentials
LOOP:process
  DELEGATE update
```
If repository exists but database-credentials must be fetched from a slow service:
- Interpretation A: WAIT at the credentials requirement.
- Interpretation B: Continue with repository, fetch credentials asynchronously.
- Interpretation C: Assume the runtime will figure it out.

**Result:** Programs may hang, fail prematurely, or proceed with missing data.

---

### 10. Blank Line Handling in Indentation
**Section:** Syntax (line 494)

**Quote:** "Each statement is one line. Blank lines are ignored."

**Problem:** Unclear interaction with indentation parsing:

- **Interpretation A:** Blank lines are removed before parsing; indentation is determined only by non-blank lines.
- **Interpretation B:** Blank lines preserve indentation context; a blank line at a certain indentation level marks a scope boundary.

**Example causing ambiguity:**
```
WHEN x.y
  → DELEGATE a

  → DELEGATE b
EMIT result
```
Is the second arrow (with blank line separation) part of the WHEN flow or a sibling statement?

Interpretation A: Both arrows are part of the WHEN flow (blank lines ignored).
Interpretation B: The blank line breaks the flow; the second arrow might be invalid (no parent).

**Result:** Ambiguous program validity.

---

### 11. FORK with Exactly One Branch
**Section:** Control → FORK (line 149, Rule V9)

**Quote:** "Starts two or more concurrent branches... `fork = "FORK" , NL , INDENT , item , item , { item } , DEDENT`" (Grammar, line 578)

**Problem:** The EBNF grammar requires at least two items, but Rule V9 also lists "a `FORK` has fewer than two branches" as invalid. These are redundant at the syntactic level but the grammar might be implemented differently:

- **Interpretation A:** The parser rejects `FORK` with one branch at parse time (grammar rule).
- **Interpretation B:** Parsing succeeds, but semantic validation catches it (Rule V9).

**Example:**
```
FORK
  → DELEGATE x
```
Interpretation A: Parse error.
Interpretation B: Semantic validation error.

**Result:** Different error reporting and handling.

---

## Medium-Risk Issues

### 12. Multiple Outcomes for Same Subject
**Section:** Outcomes (line 483, Rule V7)

**Quote:** "Each subject holds its most recently established outcome. A later `VERIFY x`, or a later answer to `HITL:x` replaces it... Two `HITL` statements use the same name... or a name is used by both a `HITL` and a `VERIFY`" is invalid.

**Problem:** Rule V7 forbids two HITLs with the same name or mixing HITL and VERIFY for the same subject. But:

- **Interpretation A:** This means you cannot have `VERIFY x` and `HITL:x[...]` in the same program.
- **Interpretation B:** You can have both, but the most recent one wins (outcome replacement).

**Example with ambiguity:**
```
VERIFY build
LOOP:retry
  DELEGATE fix
  HITL:build[fixed]("Fixed?")
  WHEN build.fixed
    → BREAK
```
Does Rule V7 reject this (VERIFY and HITL both named `build`)? Or is this allowed because the HITL outcome replaces the VERIFY outcome dynamically?

**Result:** Valid programs may be incorrectly rejected, or invalid programs accepted.

---

### 13. Outcome Declared Names Rule V6
**Section:** Outcomes (line 486, Rule V6)

**Quote:** "Every `WHEN` condition MUST refer to a subject and an outcome that the program can produce... `a `WHEN` tests `x.y`, and the program contains neither `VERIFY x` with `y` being `accepted` or `rejected`, nor `HITL:x[…]` listing `y`."

**Problem:** This rule is complex and two interpretations exist:

- **Interpretation A:** A WHEN can only test outcomes that are explicitly produced by the program (strict).
- **Interpretation B:** A WHEN can test outcomes if the structure allows it (loose).

**Example causing ambiguity:**
```
WHEN build.accepted
  → DELEGATE publish
VERIFY build
```
The WHEN precedes the VERIFY. Does Rule V6 allow this? 

Interpretation A: No, because the VERIFY comes after the WHEN.
Interpretation B: Yes, because the VERIFY is in the program.

**Result:** Validation order becomes important and ambiguous.

---

### 14. WAIT Event Specification
**Section:** Control → WAIT (line 214)

**Quote:** "The DSL does not name the event. The surrounding process and the runtime determine it... There is no timeout."

**Problem:** An underspecification, not an ambiguity, but it prevents complete execution traces:

- **Interpretation A:** WAIT is a named event; the trace can identify what is being awaited.
- **Interpretation B:** WAIT is abstract; the trace shows only that execution is waiting, not why.

**Example:**
```
WAIT
DELEGATE next-step
```
An execution trace might show:
```
5. WAIT -> waiting
6. WAIT -> (event received, but what event?)
7. DELEGATE next-step -> done
```

**Result:** Incomplete execution traces and insufficient debugging information.

---

### 15. Nested REQUIRE and HITL Fallbacks
**Section:** Syntax → Indentation (Rule V4, line 560)

**Quote:** "`→ FALLBACK` is not directly under a `HITL` or `REQUIRE`; or a `HITL`/`REQUIRE` has more than one `FALLBACK`."

**Problem:** The rule doesn't explicitly forbid fallback-within-fallback, creating ambiguity:

- **Interpretation A:** A fallback flow can contain a HITL with its own fallback (nested fallbacks allowed).
- **Interpretation B:** Fallback flows should not contain HITLs with fallbacks (only one level of fallback).

**Example:**
```
HITL:x[a]("?")
  → FALLBACK
    → HITL:y[b]("?")
      → FALLBACK
        → STOP
    → STOP
```
Is the inner FALLBACK allowed? Rule V4 doesn't explicitly forbid it.

**Result:** Programs with nested error handling may be ambiguously valid or invalid.

---

### 16. Consecutive WHEN Independence and Outcome Replacement
**Section:** Execution in ten rules (Rule 3, line 59)

**Quote:** "Consecutive `WHEN`s are independent. Every one that is true runs, top to bottom."

**Problem:** How does this interact with outcome replacement?

- **Interpretation A:** Each WHEN is evaluated on the outcomes available when it is reached.
- **Interpretation B:** All WHEN conditions are evaluated on a fixed snapshot of outcomes, then executed.

**Example causing different behavior:**
```
VERIFY x
WHEN x.accepted
  → VERIFY x  (changes to rejected)
WHEN x.rejected
  → TRANSITION "Error"
```
In iteration A: The first WHEN is true and runs, which changes the outcome. The second WHEN is then evaluated on the new outcome (rejected) and is true.
In interpretation B: Both WITHs are evaluated on the original outcome (accepted), so only the first runs.

**Result:** Different control flow.

---

### 17. EMIT Result Validation
**Section:** Agentic Operations → EMIT (line 316)

**Quote:** "Produces an externally meaningful output. The DSL does not prescribe how it is created, stored, or transmitted."

**Problem:** No validation mechanism for EMIT:

- **Interpretation A:** EMIT always succeeds; there's no way to know if the output was actually produced.
- **Interpretation B:** The runtime may fail to EMIT and execution should halt (but this isn't specified).

**Example causing silent failures:**
```
EMIT release-notes
EMIT release-artifact
TRANSITION "Released"
```
If EMIT release-artifact fails, does the program:
- Continue to TRANSITION anyway (A)?
- Halt and report an error (B)?

**Result:** Silent failures or undefined error handling.

---

### 18. AUTO and Authority Definition
**Section:** Human Interaction → AUTO (line 397)

**Quote:** "The agent does not have the authority required to make the decision" is an example of uncertainty.

**Problem:** "Authority" is not defined:

- **Interpretation A:** Authority is determined by explicit permissions in the system.
- **Interpretation B:** Authority is inferred from the agent's role or scope.
- **Interpretation C:** Authority is assumed unless explicitly denied.

**Example revealing ambiguity:**
```
AUTO HITL:delete[yes, no]("Delete all data?")
```
Agent without explicit delete permission:
- A: Cannot auto-answer (no authority).
- B: Cannot auto-answer (inferred role restriction).
- C: Can auto-answer (no explicit denial).

**Result:** Different agents make different decisions on the same program.

---

### 19. FORK Branch Completion Definition
**Section:** Control → FORK (line 155)

**Quote:** "A branch is complete when its last statement is done."

**Problem:** "Last statement" is ambiguous in the presence of nested structures:

- **Interpretation A:** The last statement is the textually final line of the branch.
- **Interpretation B:** The last statement that executes (depends on branching within the branch).

**Example:**
```
FORK
  → LOOP:l
    → DELEGATE work
    → WHEN work.done
      → BREAK
  → DELEGATE other
```
Branch 1: Is it complete when the LOOP exits (via BREAK) or when all LOOP statements are processed?
Branch 2: Completes after DELEGATE other.

**Result:** Unclear when JOIN actually waits.

---

### 20. STOP and Awaiting Branches
**Section:** Control → STOP (line 228)

**Quote:** "No further statement runs anywhere, including other `FORK` branches. A pending `JOIN` never completes."

**Problem:** Timing of STOP across asynchronous branches:

- **Interpretation A:** STOP immediately halts all branches synchronously.
- **Interpretation B:** STOP signals all branches to stop, but they may be waiting and the signal is asynchronous.

**Example:**
```
FORK
  → WAIT
  → DELEGATE work
    STOP
```
Branch 1 is waiting at WAIT. Branch 2 executes STOP. Does:
- Interpretation A: Branch 1 stops immediately, awaiting nothing.
- Interpretation B: Branch 1 remains waiting (no signal received in-flight).

**Result:** Unclear termination semantics.

---

## Lower-Risk Issues (Underspecifications with Less Impact)

### 21. LOOP Name Usage
**Section:** Control → LOOP (line 88)

**Quote:** "`<name>` is only a label. No statement refers to it; `BREAK` takes no name."

**Problem:** Why mention the name at all if it's not used?

- **Interpretation A:** The name is purely documentary.
- **Interpretation B:** The name might be used in future DSL extensions or debugging.

**Result:** Minimal impact; the behavior is clear (BREAK exits innermost loop). But it's an unnecessary language feature.

---

### 22. WHEN and Later Outcome Establishment
**Section:** Control → WHEN (line 119)

**Quote:** "The outcome is established later → Nothing happens. A `WHEN` is not a standing trigger and is never re-checked."

**Problem:** "Later" is ambiguous about timing:

- **Interpretation A:** If outcome is established after the WHEN statement, the WHEN was false (not re-checked).
- **Interpretation B:** If outcome is established later in execution, the WHEN is not re-checked even if the loop repeats.

**Result:** Mostly clear from context, but could confuse users about loop behavior.

---

### 23. HITL Request vs. Decision Forms
**Section:** Human Interaction → HITL (line 325-348)

**Quote:** Two forms exist: decision (with answers) and request (no answers). Responses for requests must "provide the requested input or confirms the requested action," but this is vague.

**Problem:**
- **Interpretation A:** Request responses are strictly defined by the request.
- **Interpretation B:** Request responses have broad interpretation (any input is acceptable).

**Example:**
```
HITL("Approve the release notes?")
  → FALLBACK
    → TRANSITION "Blocked"
    → STOP
```
A human response of "I haven't looked yet" (insufficient for a decision form) might or might not be considered sufficient for a request form.

**Result:** Different agents handle insufficient responses differently.

---

### 24. Execution State Persistence
**Section:** Executing a program (line 602-607)

**Quote:** "Keep the execution state: the current position, the current process state (from `TRANSITION`), the latest outcome of each subject, the running branches."

**Problem:** Unclear whether execution state persists across external interruptions or suspensions.

- **Interpretation A:** All state persists if execution is suspended and resumed.
- **Interpretation B:** Only some state (outcomes, state) persists; position is reset.

**Result:** Recovery from interruption is ambiguous.

---

### 25. DELEGATE Result Semantics
**Section:** Agentic Operations → DELEGATE (line 270-272)

**Quote:** "A delivered result is not necessarily correct, complete, or accepted. Use `VERIFY` to evaluate it."

**Problem:** What is a "result" from DELEGATE?

- **Interpretation A:** A result is any output from the delegated work (success or failure).
- **Interpretation B:** A result is only a successful outcome; failure might STOP execution.

**Result:** Unclear error handling in DELEGATE.

