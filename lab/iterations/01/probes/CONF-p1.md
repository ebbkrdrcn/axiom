# Ambiguities, Contradictions, and Underspecifications in the `go_harness` DSL

Ordered from most to least likely to cause a wrong process definition or wrong execution.

---

## 1. The universal statement grammar contradicts several keyword examples

**Section:** Syntax → Statement

> ```text
> <keyword> <argument>
> ```

**Problem:** This is presented as the general rule for every statement, but `STOP`, `BREAK`, `JOIN`, and `WAIT` are all shown, throughout the "Control" section, with no argument at all:

> `STOP` / `BREAK` / `JOIN` / `WAIT`

**Two readings:**
- **Reader A** treats the grammar rule literally and concludes every statement, including `WAIT` and `STOP`, requires an argument (e.g. `WAIT external-event`, `STOP "done"`), and treats the bare forms in the examples as informal shorthand that a real program must not use.
- **Reader B** treats the four argument-less keywords as a special case ("zero-argument statements") and writes/accepts `WAIT` and `STOP` bare, per the worked examples, ignoring the general grammar rule.

Because this affects the parser/writer for every single process, a mismatch here breaks compatibility between two independently-built tools before any semantic question even arises.

---

## 2. `WHEN` evaluation semantics: exclusive branch vs. independent parallel triggers

**Section:** Control → WHEN

> "Multiple `WHEN` constructs may describe different outcomes of the same process state."
> "`WHEN` is a control construct, not an operation."

**Problem:** The spec never says whether `WHEN` blocks are mutually exclusive alternatives (only the first/one matching condition's flow runs, like `if/else if`), or independent reactive rules that *each* fire their flow whenever their own condition holds — including firing more than one simultaneously if more than one condition is true, or firing none if no condition matches (with no specified fallback).

**Two readings:**
- **Reader A** implements `WHEN` as an if/elif chain: conditions are checked in declaration order, and once one matches, its flow runs and the rest are skipped for that evaluation point.
- **Reader B** implements `WHEN` as a set of independent observers over process state: every `WHEN` whose condition is true fires its flow, so `WHEN tests.passed` and some other true condition could both execute in the same pass, and it's silent about what happens if none of the declared `WHEN`s match.

This is a high-impact ambiguity because the two designs produce materially different execution (single-path vs. potentially concurrent/duplicate side effects, and undefined "no match" behavior).

---

## 3. `FORK`/`JOIN` correspondence and behavior with no `JOIN`

**Section:** Control → FORK / JOIN

> "Waits for the concurrent flows started by **the corresponding `FORK`**."
> "Use `JOIN` when execution must wait for the concurrent flows to complete." (implying it's optional)

**Problem:** "The corresponding FORK" presumes a 1:1 pairing, but nothing defines how a `JOIN` locates its corresponding `FORK` when multiple `FORK`s could have occurred before it (e.g., in a loop that forks each iteration, or two sequential `FORK`s with only one `JOIN` between them). Additionally, since `JOIN` is optional, the spec never states what happens to unfinished forked flows if the enclosing scope ends (e.g., `LOOP` iterates again, or the process reaches `STOP`) without a `JOIN` — are they abandoned, still running in the background, or is this an error?

**Two readings:**
- **Reader A** assumes "the corresponding FORK" means the most recent (innermost/lexically nearest) `FORK` still open, so a `JOIN` after two consecutive `FORK`s only waits on the second.
- **Reader B** assumes it means *all* `FORK`s opened since the last `JOIN` (cumulative), so the same `JOIN` waits on both.
- Separately, one reader assumes omitting `JOIN` means the flow is genuinely fire-and-forget forever (orphaned), while another assumes an implicit join happens at the end of the enclosing scope regardless.

---

## 4. `STOP` inside a `FORK` branch: whole-execution stop vs. branch-local stop

**Section:** Control → STOP, cross-referenced with FORK

> "`STOP` Terminates execution." / "No subsequent statement is executed after `STOP`."
> (FORK) "The branches may execute concurrently."

**Problem:** `STOP` is defined globally ("terminates execution," full stop), but `FORK` explicitly creates concurrent, independent flows. It is not addressed what happens when one concurrent branch reaches `STOP` while sibling branches are still running — whether the *entire* process (including other forked branches) is terminated immediately, or only that branch's flow ends (contradicting the plain reading of "terminates execution").

**Two readings:**
- **Reader A** takes "terminates execution" literally: any `STOP` anywhere, even inside one forked branch, ends the whole process immediately, cancelling sibling branches.
- **Reader B** reasons that since `FORK` branches are "independent flows," a `STOP` inside one branch can only plausibly terminate that flow's own execution (analogous to how `BREAK` is scoped to "the current LOOP"), and the global process continues until all branches finish or a `STOP` occurs outside any fork.

---

## 5. `BREAK` inside a `LOOP` that contains a `FORK` (or nested `LOOP`s)

**Section:** Control → BREAK, LOOP

> "`BREAK` exits the current `LOOP`." / "`BREAK` may only exit a loop scope."
> (LOOP) `LOOP:<name>` — loops are named, but `BREAK` takes no argument/name.

**Problem:** "The current LOOP" is not well-defined in two situations the grammar allows: (a) nested loops, where "current" could mean the innermost loop or could — given that loops are explicitly named — be intended to let `BREAK` reference an outer loop by name (but the `BREAK` syntax shown has no argument to name one); (b) a `LOOP` containing a `FORK`, where `BREAK` inside one forked branch has an unclear effect on the loop that encloses the whole `FORK` (does it break the loop immediately, or only once/if that branch's outcome is joined?).

**Two readings:**
- **Reader A** assumes `LOOP:<name>` naming is purely documentation/labeling with no operational effect, and `BREAK` always means "innermost enclosing loop," full stop.
- **Reader B** assumes the naming exists precisely so that (in some unwritten extension) `BREAK` could target a named outer loop, and treats the current spec as incomplete on this point rather than settled — leading to disagreement about whether unlabeled `BREAK` in a nested-loop process is even well-formed.

---

## 6. `REQUIRE` failure: what must happen instead of proceeding

**Section:** Agentic Operations → REQUIRE

> "If a required condition cannot be satisfied, execution must not proceed as if the requirement were satisfied."

**Problem:** This states a negative constraint (what must *not* happen) but never specifies the required positive behavior: does unmet `REQUIRE` cause `STOP`, an implicit `WAIT`, an automatic `HITL` escalation, or a `WHEN`-style branch (e.g. `WHEN requirement.unmet`) that the author must handle explicitly? Since no such branching condition is defined for `REQUIRE` outcomes (unlike `VERIFY`, which explicitly says "may establish outcomes that can be used by WHEN"), it's unclear whether `REQUIRE` even produces an evaluable outcome at all.

**Two readings:**
- **Reader A** treats an unmet `REQUIRE` as an implicit fatal error equivalent to `STOP`, since there is no other named mechanism to continue safely.
- **Reader B** treats `REQUIRE` as producing a checkable condition, and expects the author to write `WHEN <requirement>.unmet → HITL(...)` explicitly, treating the absence of an automatic behavior as intentional (author's responsibility), not the runtime's.

---

## 7. `DELEGATE`: synchronous (blocking) vs. asynchronous relative to `VERIFY`

**Section:** Agentic Operations → DELEGATE

> ```text
> DELEGATE implementation
> VERIFY implementation
> ```
> "`DELEGATE` does not mean that the work is correct, complete, or accepted."

**Problem:** The example places `VERIFY` immediately after `DELEGATE` with nothing in between, but the spec never states whether `DELEGATE` blocks execution until the delegated actor finishes (so `VERIFY` is guaranteed to have a completed result to evaluate) or is fire-and-forget (in which case `VERIFY` immediately following it could run before the work exists, and a `WAIT` should logically be required in between, yet the canonical example omits one).

**Two readings:**
- **Reader A** assumes `DELEGATE` is implicitly blocking/synchronous — the next statement only executes once the delegate actor returns something — making the two-line example correct and complete as written.
- **Reader B** assumes `DELEGATE` is async by nature (it "assigns work to an actor," it doesn't say "and waits"), and that the example is elliptical — a real process must insert `WAIT` before `VERIFY`, meaning the given example is technically under-specified/incorrect as a template to copy.

---

## 8. `HITL`: does it block execution like `WAIT`?

**Section:** Human Interaction → HITL, cross-referenced with WAIT

> "`HITL` establishes a human decision boundary." / "The human response may determine the subsequent flow."
> (WAIT) "Suspends execution until an external event or response is available."

**Problem:** `WAIT` is explicitly defined as suspending execution; `HITL` is never explicitly said to suspend execution — it only says the response "may determine" subsequent flow, which is consistent with either a blocking wait for the human or a non-blocking request whose eventual response is consumed later (elsewhere, perhaps via a subsequent explicit `WAIT`).

**Two readings:**
- **Reader A** assumes `HITL` implicitly suspends execution just like `WAIT` (it's "a decision boundary," so nothing proceeds until the human decides), so no explicit `WAIT` is ever placed after a `HITL`.
- **Reader B** assumes `HITL` merely issues the request and, being a distinct keyword from `WAIT`, does not itself suspend anything — meaning a correct process must pair `HITL("...")` with a following `WAIT` to actually block, and a process lacking that `WAIT` would (under this reading) race ahead without the human's input.

---

## 9. `AUTO`: no valid syntax is ever shown

**Section:** Human Interaction → AUTO

> "`AUTO` is not a control-flow container. It does not contain `WHEN`, `→`, or an arbitrary flow." plus an explicit example of *invalid* usage.

**Problem:** Every other construct in the spec is given at least one worked example of correct syntax and placement. `AUTO` is defined entirely by negation (what it is *not*, and one invalid example) — there is no example anywhere of a well-formed statement or block using `AUTO`. It is unclear whether `AUTO` is a standalone statement (`AUTO`), a modifier attached to `HITL` (e.g. `HITL("...") → AUTO`), an argument to `HITL` (`HITL("...", AUTO)`), or a prefix keyword (`AUTO HITL("...")`).

**Two readings:**
- **Reader A** writes `AUTO` as a bare statement placed before or after the `HITL` it governs, e.g.:
  ```text
  HITL("Approve deploy?")
  AUTO
  ```
- **Reader B** writes `AUTO` as an inline modifier fused to the `HITL` call itself, e.g. `HITL("Approve deploy?") → AUTO`, treating it structurally like `FALLBACK`'s `→` attachment shown in the next section.
  Since the spec supplies no canonical form, two implementations of the DSL could each consider the other's `AUTO` usage a syntax error.

---

## 10. `FALLBACK`: is it usable only with `HITL`, or with any suspending operation?

**Section:** Human Interaction → FALLBACK

> ```text
> HITL("<message>")
>   → FALLBACK
>       → <flow>
> ```
> "`FALLBACK` is associated with response handling." "The fallback flow is used only when the expected response cannot be used to continue the normal flow."

**Problem:** The general definition ("response handling," "expected response... unavailable or insufficient") is phrased generically enough to plausibly apply to any operation that awaits a response — `WAIT` (an external event that never arrives) or `DELEGATE` (an actor that never completes) — but the only syntax shown attaches `FALLBACK` under `HITL`. It's unclear whether `FALLBACK` is a general-purpose construct usable after any suspending statement, or exclusively an `HITL` sub-clause.

**Two readings:**
- **Reader A** restricts `FALLBACK` to `HITL` only, since that's the sole documented attachment point, and would consider `WAIT → FALLBACK → ...` invalid/undefined.
- **Reader B** reads the prose definition as construct-agnostic ("defines the flow to use when an expected response is unavailable") and freely attaches `FALLBACK` after `WAIT` or `DELEGATE` too, expecting it to behave the same way (timeout/insufficient-result handling).

---

## 11. Undefined grammar for `WHEN` conditions

**Section:** Control → WHEN, and Syntax → Identifier

> `WHEN <condition>` — with examples only like `tests.passed`, `tests.failed`, `implementation.accepted`, `implementation.rejected`, `decision.uncertain` (the last one explicitly disallowed as a *keyword-level* concept, but not necessarily as a general condition string).

**Problem:** Only dotted identifiers appear as example conditions; the spec never defines the actual condition grammar — whether boolean composition (`AND`/`OR`/`NOT`), comparisons, or arbitrary free-form predicate strings are permitted, or whether a "condition" must always be exactly one `<result-or-requirement>.<outcome>` pair as shown.

**Two readings:**
- **Reader A** restricts conditions strictly to the single dotted-pair shape shown in every example (`entity.outcome`), rejecting anything else as invalid.
- **Reader B** treats `<condition>` as an open-ended expression slot (per the generic `<argument>` grammar) and writes compound conditions like `WHEN tests.passed AND review.accepted`, which reader A's tooling would not recognize as a single valid condition.

---

## 12. Indentation/scope mechanics are asserted but not formally defined

**Section:** Syntax → Scope, Forked Flow

> "Indented statements belong to the preceding scoped construct." ... "Indented statements following a branch belong to that branch **until the branch scope ends**."

**Problem:** No indentation unit (spaces vs. tabs, how many columns constitute one nesting level) is specified, and "until the branch scope ends" is circular — it defines scope end in terms of itself rather than in terms of a dedent rule or an explicit terminator. This is especially ambiguous inside `FORK`, where the example shows two levels of indentation under each `→` (the delegate/verify pair), and nothing states whether a *further*-nested construct (e.g., a `WHEN` with its own `→` lines) inside a branch is delimited the same way, or whether reaching another top-level `→` at the branch's original indent always ends the previous branch even if a deeper block was still open due to a formatting slip.

**Two readings:**
- **Reader A** assumes classic dedent-based scoping (like Python): a line's indentation level relative to the opening construct strictly determines nesting, and any consistent indentation scheme (2 spaces, 4 spaces, tabs) is acceptable as long as it's consistent within one document.
- **Reader B** assumes scope is delimited structurally by the next same-level keyword/`→` marker rather than by whitespace column-counting, meaning indentation is cosmetic and only keyword adjacency matters — a materially different parsing strategy that would disagree with Reader A on malformed/irregularly-indented input.

---

## 13. Is `WHEN` a one-time sequential check or a continuously monitored trigger?

**Section:** Control → LOOP, WHEN

> (LOOP) "The loop continues until `BREAK`, `STOP`, or another explicit control flow terminates it." (implying continuous condition-watching)
> (WHEN) shown as a plain sequential statement inside a flow, evaluated presumably once, at the point it's reached.

**Problem:** If `WHEN` is just a sequential statement (like every other statement, executed once in declaration order per the Flow section), then inside a `LOOP` it can only be checked once per iteration, at the specific point it's textually reached — not continuously. But the DSL gives no way to express "continuously watch for tests.failed at any point," and LOOP's own description ("continues until... another explicit control flow terminates it") vaguely gestures at conditions being able to interrupt a loop at any time, which reads as broader than "checked once per pass, at one fixed point in the sequence."

**Two readings:**
- **Reader A** treats `WHEN` strictly as an ordinary sequential statement: evaluated exactly once when control reaches it, exactly like `TRANSITION` or `EMIT`; if the condition isn't true at that specific point in that specific iteration, the branch is simply skipped and there is no re-check until the next loop iteration reaches that same line again.
- **Reader B** treats `WHEN` (at least inside a `LOOP`) as an always-active reactive rule that can fire the moment its condition becomes true anywhere during the iteration, independent of the line's position in the textual sequence — closer to an event handler than a sequential check.

---

## 14. Nesting of control constructs inside `WHEN` flows and `FORK` branches is unaddressed

**Section:** Control → WHEN, FORK

**Problem:** All examples of `WHEN`'s `→` flow and `FORK`'s `→` branch contain only simple operations (`TRANSITION`, `DELEGATE`, `VERIFY`). Nothing states whether a `→` flow may itself contain another full control construct — a nested `LOOP`, another `WHEN`, or a `FORK` — or whether `→` flows are restricted to flat sequences of simple operations only.

**Two readings:**
- **Reader A** assumes `→` flows can contain anything a top-level flow can, including nested `LOOP`/`FORK`/`WHEN`, since nothing forbids it and the grammar is otherwise recursively described.
- **Reader B** assumes, by the absence of any example showing this, that `→` flows are intentionally restricted to sequences of operations (not full control constructs), and would reject a nested `LOOP` inside a `WHEN` branch as outside the documented grammar.

---

## 15. No defined behavior for failure/error propagation across `FORK` branches

**Section:** Control → FORK / JOIN

**Problem:** If one branch's `VERIFY` results in a rejected/failed outcome, or a `DELEGATE`d actor errors out, nothing specifies whether this affects sibling branches (cancel them), affects the `JOIN` (does `JOIN` "complete" only on all-success, or does it complete regardless of each branch's individual outcome and require a subsequent `WHEN` to inspect each result?).

**Two readings:**
- **Reader A** assumes `JOIN` is purely a completion barrier — it waits for branches to finish (however they finish, success or failure) — and any failure handling is entirely the author's job via `WHEN` checks written after the `JOIN`.
- **Reader B** assumes a failure in one branch implicitly cancels/short-circuits the others and causes the whole `FORK`/`JOIN` to behave like a failed operation immediately, without waiting for the rest — since the spec gives no explicit contract, both are defensible.

---

## 16. `TRANSITION` target vocabulary is undefined

**Section:** Agentic Operations → TRANSITION

> `TRANSITION "Code Review"` — "means that the process has moved to the `Code Review` state."

**Problem:** There is no declaration mechanism for valid states (no `STATES:` block or enumeration), so it's unclear whether `TRANSITION` may target *any* arbitrary string freely (loose, stringly-typed state) or whether a conforming process must have implicitly pre-declared/agreed states elsewhere, with `TRANSITION` to an unknown state being an error.

**Two readings:**
- **Reader A** treats state names as free-form labels with no validation — any string is a legal `TRANSITION` target, and typos or synonyms (`"Review"` vs `"Code Review"`) simply create different, unrelated states silently.
- **Reader B** assumes a well-formed process must consistently reuse a closed, if informally agreed, set of state names, and would consider introducing a new unlisted state name mid-process a specification error even though the DSL has no formal way to declare or check that set.

---

## 17. `EMIT`/`VERIFY`/ordering constraints are not addressed

**Section:** Agentic Operations → EMIT, VERIFY

**Problem:** Nothing constrains when `EMIT` may legally occur relative to `VERIFY` (e.g., must an artifact be verified before it is emitted, or can `EMIT` happen pre-verification as a draft output?). This is lower-impact than the items above since it mostly affects process *design quality* rather than causing outright mis-execution, but two authors could reasonably disagree on whether `EMIT` after a rejected `VERIFY` is legal.

**Two readings:**
- **Reader A** assumes `EMIT` should only occur after a successful `VERIFY`, treating "externally meaningful output" as implying it has been accepted.
- **Reader B** assumes `EMIT` is independent of `VERIFY`'s outcome and can represent any output, including provisional/rejected drafts, since nothing ties the two keywords together explicitly.

---

## Note on method

Only the text inside the `<specification>` block was used. Where the specification is silent (e.g., no positive replacement behavior for a failed `REQUIRE`, no canonical `AUTO` syntax), this is called out explicitly above as underspecified rather than resolved by outside assumption — the "two readings" in each case are both textually defensible given only what is written.
