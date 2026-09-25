# Ambiguities, Contradictions, and Underspecifications in the go_harness DSL Spec

Ordered from most likely to cause a wrong process or wrong execution to least likely. Each item cites the section, quotes the relevant text, explains the problem, and gives two divergent readings.

---

## 1. `AUTO` has no valid syntax shown anywhere

**Section:** `AUTO`

**Quote:**
> `AUTO` is not a control-flow container. It does not contain `WHEN`, `→`, or an arbitrary flow. ... For example, the following is invalid: `AUTO / WHEN decision.uncertain / → HITL("Approve?")`

**Problem:** The spec devotes an entire section to what `AUTO` *means* and gives one explicit example of *invalid* syntax, but never once shows a *valid* statement using `AUTO`. Every other keyword (`LOOP`, `WHEN`, `FORK`, `JOIN`, `BREAK`, `WAIT`, `STOP`, `REQUIRE`, `DELEGATE`, `VERIFY`, `TRANSITION`, `EMIT`, `HITL`, `FALLBACK`) has a `<keyword> <argument>` form or a worked example. `AUTO` does not. It's impossible to write a compliant process that actually uses `AUTO` from the spec alone.

**Divergent readings:**
- Reader A: `AUTO` is a standalone statement, e.g. `AUTO <decision>`, functioning like a decision-resolution operation parallel to `VERIFY`.
- Reader B: `AUTO` is a modifier suffix attached to `HITL`, e.g. `HITL("Approve?") AUTO`, since the "Human Interaction" prose ties it directly to whether a `HITL` "may be silently replaced." Under this reading `AUTO` never appears as its own line at all.

These produce structurally different documents (a new top-level statement type vs. an annotation on existing statements), so a parser built on one assumption will reject or misinterpret programs written under the other.

**Assumption made:** None resolvable from the spec; flagged as unresolvable without further information.

---

## 2. `WHEN` — no specified behavior when no branch matches, or when multiple branches match

**Section:** `WHEN`

**Quote:**
> Multiple `WHEN` constructs may describe different outcomes of the same process state.

**Problem:** The spec never states what happens if (a) no `WHEN` condition currently holds, or (b) more than one `WHEN` condition holds simultaneously. It only says multiple `WHEN`s "may describe different outcomes," implying but never guaranteeing mutual exclusivity and exhaustiveness.

**Divergent readings:**
- Reader A: `WHEN` blocks are evaluated once, in order; if none match, execution simply falls through to the next statement after the group of `WHEN`s (like an if-chain with no `else`).
- Reader B: A `WHEN` group is a synchronization point — if no condition is yet satisfied, the process implicitly waits (similar to `WAIT`) until one becomes true, since "the human response may determine the subsequent flow" language elsewhere in the spec suggests conditions are awaited, not merely polled once.

Reader A risks silently skipping required handling; Reader B risks an implementer building in blocking behavior nowhere authorized by the spec. Which one is "correct" changes whether an unhandled state hangs forever or is silently ignored — a major behavioral divergence.

**Assumption made:** None; flagged as unresolved.

---

## 3. `FORK` / `JOIN` — "corresponding FORK" and "required forked flows" are undefined

**Section:** `FORK`, `JOIN`

**Quote:**
> "Waits for the concurrent flows started by the **corresponding** `FORK`." ... "Execution continues only after all **required** forked flows have completed."

**Problem:** Two separate underspecified terms:
1. "corresponding `FORK`" — if a process contains two `FORK` blocks (sequential or nested) before a `JOIN`, there's no rule for which `FORK`(s) that `JOIN` pairs with.
2. "required forked flows" — the word "required" implies some forked flows are optional (need not be waited on), but nothing defines which are required vs. optional, or how a flow is marked as such.

**Divergent readings:**
- Reader A: `JOIN` always corresponds to the nearest preceding unmatched `FORK` in the same scope (like a stack-based pairing), and "required" just means "all of them" (the word is stylistic, not a filter).
- Reader B: `JOIN` waits on *every* `FORK` opened earlier in the entire process that hasn't yet been joined, and "required" implies the process definition elsewhere can mark specific branches as optional/best-effort, which `JOIN` then skips.

This directly changes concurrency correctness: under Reader B, a process author could believe a `JOIN` waits for a branch that Reader A's runtime doesn't wait for, or vice versa.

**Assumption made:** None; flagged as unresolved.

---

## 4. `STOP` and `BREAK` inside a `FORK` branch — no interaction rule with sibling branches

**Section:** `FORK`, `BREAK`, `STOP`

**Quote:**
> "`BREAK` does not terminate the entire execution." ... "`STOP` Terminates execution. No subsequent statement is executed after `STOP`." ... (FORK) "Each `→` starts an independent flow... The branches may execute concurrently."

**Problem:** Nothing addresses what happens when a statement inside one forked branch is `BREAK` or `STOP`. Does `STOP` in one branch immediately terminate the whole process, including sibling branches still running concurrently (contradicting their "independence")? Does `BREAK` inside a branch break a `LOOP` that only encloses that one branch, or the `LOOP` that encloses the entire `FORK`?

**Divergent readings:**
- Reader A: Control-flow statements are strictly local to their own flow; `STOP` in one branch ends only that branch (effectively acting like a branch-local halt), and the overall process is only fully terminated once `JOIN` observes all branches ended somehow.
- Reader B: `STOP` always means "terminate execution" globally, per its own section's literal wording, so `STOP` in any branch immediately kills all concurrently executing sibling branches too, regardless of `FORK`'s "independent flow" language.

This is a real correctness hazard: a process author relying on Reader A's semantics to have one branch stop while another finishes cleanup would see Reader B's runtime silently abort that other branch's work.

**Assumption made:** None; flagged as unresolved.

---

## 5. `BREAK` in nested `LOOP`s, and the unused purpose of `LOOP:<name>`

**Section:** `LOOP`, `BREAK`

**Quote:**
> "`BREAK` Exits the current `LOOP`." ... (LOOP syntax) `LOOP:<name>` ... "All statements inside the scope belong to the loop."

**Problem:** `LOOP` is given a name (`<name>`), but no statement in the spec (including `BREAK`) ever references a loop by name. If loops can nest, "the current `LOOP`" is ambiguous without a defined scoping rule, and the presence of a name strongly implies (to a careful reader) that targeted breaking (`BREAK <name>`) should be possible — yet the `BREAK` syntax shown takes no argument at all.

**Divergent readings:**
- Reader A: "current" means the innermost enclosing `LOOP` only (standard nested-loop-break semantics); the `<name>` is purely a label for logging/readability and has no runtime effect on `BREAK`.
- Reader B: The name exists precisely so `BREAK` (or some unshown extended form) can target an outer loop by name in nested-loop scenarios; the given `BREAK` syntax is just the simple/default case, and its absence of an argument is an omission rather than a deliberate restriction.

Under Reader A, a nested-loop process can never break an outer loop directly (must propagate via flags/state); under Reader B, an implementer might add unauthorized syntax to compensate. This affects how nested-loop processes must be authored.

**Assumption made:** Treat "current" as innermost enclosing loop, and the name as a non-functional label, since no addressed-break syntax is given — but flagged as an assumption, not a spec guarantee.

---

## 6. `WAIT` — its relationship to `HITL`, `DELEGATE`, and `REQUIRE` is not defined

**Section:** `WAIT`, `HITL`, `FALLBACK`

**Quote:**
> (WAIT) "Suspends execution until an external event or response is available. ... After the required event or response becomes available, execution continues according to the surrounding flow." ... (FALLBACK example) `HITL("<message>") / → FALLBACK / → <flow>` — with no `WAIT` statement anywhere in the example.

**Problem:** `WAIT` is presented as a free-standing statement, yet the worked `HITL`/`FALLBACK` example never uses it — suspension for a human response appears to happen implicitly inside `HITL` itself. This leaves it unclear whether `WAIT` is (a) a general-purpose, independently usable suspension statement that must be explicitly written after any `DELEGATE`/`HITL`/`REQUIRE` to actually pause, or (b) suspension is already implicit in those operations and `WAIT` is reserved for some other, unstated kind of external event (e.g., a webhook or timer) that isn't tied to any other keyword at all.

**Divergent readings:**
- Reader A: `DELEGATE`/`HITL` do not themselves block; a process must explicitly write `WAIT` afterward to suspend until the delegated/human response arrives. Omitting `WAIT` after `DELEGATE` means the very next statement runs immediately, possibly before the delegated work is done.
- Reader B: `HITL` (and perhaps `DELEGATE`) already implies suspension per their own descriptions ("the human response may determine the subsequent flow"), and `WAIT` is a separate, rarely-needed primitive for arbitrary external events unrelated to those two keywords.

This changes whether omitting `WAIT` after a `DELEGATE`/`HITL` is a bug (Reader A) or normal (Reader B) — a significant correctness question for almost every real process.

**Assumption made:** None; flagged as unresolved.

---

## 7. `FALLBACK` — is it exclusive to `HITL`, or usable after any response-producing construct?

**Section:** `FALLBACK`

**Quote:**
> "`FALLBACK` is associated with response handling. It does not mean 'execute this flow after the normal flow.' The fallback flow is used only when the expected response cannot be used to continue the normal flow."

**Problem:** The only syntax example attaches `FALLBACK` to `HITL`. But the prose speaks generically of "response handling" and "the expected response," which could equally describe `DELEGATE` (an actor's returned work) or `WAIT` (an external event/response). The spec never states whether `FALLBACK` is a `HITL`-only annotation or a general pattern attachable to any construct that can produce or await a response.

**Divergent readings:**
- Reader A: `FALLBACK` syntax is only ever legal directly beneath `HITL`, since that's the only construct it's shown attached to and the only one under the "Human Interaction" heading.
- Reader B: `FALLBACK` is a general response-handling attachment usable after `DELEGATE` or `WAIT` too (e.g., "delegate timed out or actor unavailable → fallback"), since nothing in the generic wording restricts it to human interaction specifically.

This affects whether a process author can legitimately write a timeout/fallback flow for a `DELEGATE` or `WAIT`, or must awkwardly route everything through `HITL` to get fallback behavior.

**Assumption made:** None; flagged as unresolved.

---

## 8. Dot-notation conditions/outcomes (`tests.passed`, `implementation.accepted`) are never defined by the grammar

**Section:** `WHEN`, `VERIFY`, `Identifier`

**Quote:**
> (WHEN example) `WHEN tests.passed` / `WHEN tests.failed` ... (VERIFY example) `WHEN implementation.accepted` / `WHEN implementation.rejected` ... (Identifier syntax) "`<identifier>` ... Identifiers may be used to refer to requirements, results, states, artifacts, or other process-defined entities."

**Problem:** The `Identifier` grammar rule shows only a bare `<identifier>`, with no mention of dotted/namespaced identifiers (`name.outcome`). The examples throughout use dot-notation freely (`tests.passed`, `implementation.accepted`), and `VERIFY`'s prose says it "may establish outcomes that can be used by `WHEN`" — but never defines what the fixed vocabulary of outcomes is (`accepted`/`rejected`? `passed`/`failed`? something else per-result?), nor whether the dot is a formal operator or just illustrative prose text treated as one opaque condition string.

**Divergent readings:**
- Reader A: `<identifier>.<identifier>` is a formal "result.outcome" grammar construct, and every `VERIFY <result>` implicitly defines exactly two canonical outcomes, `<result>.accepted` and `<result>.rejected`, usable in `WHEN`.
- Reader B: The dotted forms are just example condition text with no special grammar status; `WHEN <condition>` takes an arbitrary opaque string/identifier defined entirely by the surrounding process description, and outcome names are process-specific (could be `.passed`/`.failed` for one result and `.accepted`/`.rejected` for another, or something else entirely) with no fixed vocabulary at all.

This matters because Reader A's parser would expect a consistent, checkable naming scheme tied to `VERIFY`, while Reader B's would accept (and not validate) arbitrary condition text, risking undetected typos/mismatches between what `VERIFY` "establishes" and what `WHEN` checks for.

**Assumption made:** Treated dot-notation as illustrative, non-formal text (Reader B), since the `Identifier` grammar section does not define it — flagged as an assumption.

---

## 9. `REQUIRE` — scope, duration, and failure-handling are all left open

**Section:** `REQUIRE`

**Quote:**
> "The requirement must be satisfied before execution continues." ... "If a required condition cannot be satisfied, execution must not proceed as if the requirement were satisfied."

**Problem:** Two gaps:
1. **Scope/duration** — is a `REQUIRE` satisfied once for the whole process, or must it be re-checked every time control re-enters its enclosing scope (e.g., each `LOOP` iteration if `REQUIRE` is declared inside a loop body)?
2. **Failure handling** — the spec states what must *not* happen ("must not proceed as if satisfied") but never states what *should* happen instead: does execution `STOP`? Escalate to `HITL`? Retry indefinitely? All three are consistent with "must not proceed," so the spec doesn't determine actual failure behavior.

**Divergent readings:**
- Reader A: `REQUIRE` is checked once, at first encounter; once satisfied it stays satisfied for the remainder of execution (including later loop iterations), and failure to satisfy it should route to `HITL` since that's the DSL's designated boundary for situations the agent can't resolve on its own.
- Reader B: `REQUIRE` inside a `LOOP` is re-evaluated every iteration (since "all statements inside the scope belong to the loop," and `REQUIRE` is a statement), and failure should simply `STOP` the process outright, since no continuation path is authorized.

This changes both performance/behavior (repeated checks vs. one-time) and what a process author must additionally write to handle a failed requirement (nothing, under Reader A's HITL default, vs. an explicit `STOP` or recovery flow under Reader B).

**Assumption made:** None; flagged as unresolved.

---

## 10. Scope/indentation grammar has no formal unit or nesting-resolution rule

**Section:** `Scope`, `Forked Flow`

**Quote:**
> "Indented statements belong to the preceding scoped construct." ... "Indented statements following a branch belong to that branch until the branch scope ends."

**Problem:** No indentation unit is defined (spaces? tabs? how many?), and "until the branch scope ends" is circular — it doesn't say what event/marker ends a branch scope (e.g., a decrease in indentation to a specific level, a blank line, an explicit end keyword). With constructs that can nest arbitrarily (`FORK` containing `WHEN` containing more `→` flows, `LOOP` containing `FORK`, etc.), different indentation choices by different authors could be parsed inconsistently by different implementations, since there's no formal (e.g., BNF/column-based) rule.

**Divergent readings:**
- Reader A: Scope is purely a function of relative indentation depth (like Python) — any statement indented more than its parent belongs to it, regardless of exact column, and scope ends at the first line indented at or above the parent's level.
- Reader B: Scope requires a *consistent, fixed* indentation unit throughout a document and any deviation is a syntax error — i.e., a stricter, whitespace-sensitive grammar closer to YAML.

This determines whether the same visually-plausible document is valid under one implementation and rejected (or mis-nested) under another.

**Assumption made:** None; flagged as unresolved.

---

## 11. Reused `→` token across `WHEN`, `FORK`, and `FALLBACK` creates structural ambiguity when nested

**Section:** `WHEN`, `FORK`, `FALLBACK`, `Conditional Flow`, `Forked Flow`

**Quote:**
> (WHEN) `→ <statement>` ... (FORK) `→ <statement>` starts "an independent flow" ... (FALLBACK) `→ FALLBACK / → <flow>`

**Problem:** The same `→` glyph is overloaded with at least three different semantics: "the consequence of a satisfied condition" (WHEN), "the start of an independent concurrent branch" (FORK), and "the fallback flow to use on a bad/missing response" (FALLBACK). The spec disambiguates these only by which keyword happens to precede the `→` block. When constructs nest (e.g., a `WHEN` inside a `FORK` branch, itself containing another `WHEN`), a reader/parser must infer, purely from context and indentation, which semantic a given `→` carries — the grammar never gives a rule for resolving this beyond "the preceding scoped construct," which is itself underspecified (see #10).

**Divergent readings:**
- Reader A: `→` always attaches to the nearest enclosing keyword found by walking up the indentation chain, so nested `→`s never conflict since each is unambiguously scoped to one `WHEN`/`FORK`/`FALLBACK`.
- Reader B: Because `→` has no distinct visual/keyword marking per meaning, a `→` immediately following a branch's nested `WHEN` could plausibly be read as still belonging to the outer `FORK`'s branch-list (i.e., the reader might parse it as a sibling concurrent branch rather than that `WHEN`'s conditional consequence) when documents are only loosely indented.

This is a source of genuine parser/human misreading in realistically complex (deeply nested) processes, even though simple examples in the spec are unambiguous.

**Assumption made:** None; flagged as unresolved.

---

## 12. Concurrent `TRANSITION` calls across `FORK` branches — no conflict-resolution rule

**Section:** `FORK`, `TRANSITION`

**Quote:**
> (FORK) "The branches may execute concurrently." ... (TRANSITION) "Changes the current process state... means that the process has moved to the `Code Review` state."

**Problem:** If two concurrently executing forked branches each contain a `TRANSITION` to a different state, the spec has no rule for the resulting state (last-write-wins? error? both states held simultaneously — which would contradict "the current process state" being singular?).

**Divergent readings:**
- Reader A: Process state is a single global value; concurrent `TRANSITION`s race, and whichever completes last silently wins — this is an accepted (if unstated) risk of concurrency the process author must avoid by design (e.g., not transitioning inside forked branches).
- Reader B: `TRANSITION` inside a `FORK` branch is implicitly disallowed/invalid, since the DSL models state as singular ("the current process state") and mutating it concurrently is undefined behavior the spec silently assumes won't be written.

Under Reader A a validator would accept such a process (and produce nondeterministic results); under Reader B a validator should reject it — a real difference in what counts as a "valid" process.

**Assumption made:** None; flagged as unresolved.

---

## 13. No ordering constraint between `DELEGATE`/`VERIFY`/`EMIT` — nothing stops emitting unverified work

**Section:** `DELEGATE`, `VERIFY`, `EMIT`

**Quote:**
> (DELEGATE) "A delegated result may subsequently be evaluated by `VERIFY`." ... (EMIT) "Produces an output or artifact defined by the surrounding process."

**Problem:** "May subsequently" (not "must") leaves verification optional even where it seems intended (e.g., emitting delegated work). Nothing in the syntax or semantics prevents a process from writing `DELEGATE implementation` followed directly by `EMIT source-code` with no intervening `VERIFY`, nor does anything forbid `EMIT` appearing before a `VERIFY` of the same result completes/succeeds.

**Divergent readings:**
- Reader A: This is intentional flexibility — not all delegated work requires verification (e.g., trivial or low-stakes work), so a process is free to skip `VERIFY` before `EMIT`, and the DSL imposes no ordering discipline beyond declaration order.
- Reader B: Given `VERIFY`'s statement that "completion of delegated work is not equivalent to successful verification," any well-formed process *should* be read as requiring `VERIFY` (with an `accepted` outcome via `WHEN`) to gate any subsequent `EMIT` of that same result — even though nothing in the syntax enforces it — making an unverified `EMIT` a process-design bug even though it's not a syntax error.

This matters for how strictly a linter/reviewer should treat processes that emit without verifying: a genuine defect (Reader B) or a legitimate shortcut (Reader A)?

**Assumption made:** None; flagged as unresolved.

---

## 14. `DELEGATE` never specifies how the actor is identified or selected

**Section:** `DELEGATE`

**Quote:**
> "Assigns work to an actor... The statement describes work that another actor is responsible for performing." (syntax: `DELEGATE <work>`, no actor argument)

**Problem:** The syntax `DELEGATE <work>` has no slot for naming or selecting the actor at all — only the work is expressed. The semantic principles section confirms this is deliberate ("`DELEGATE` defines responsibility, not execution mechanics"), but this still leaves genuinely ambiguous, in any real process, *who or what class of actor* (a specific human, any available agent, a specific tool/service) a given `DELEGATE` targets, with no way to express or infer that from the DSL text itself.

**Divergent readings:**
- Reader A: Actor selection is entirely out-of-band/implementation-defined per deployment (e.g., configured once for the whole runtime), so all `DELEGATE` statements in a document implicitly target the same, singularly-configured actor pool — the DSL simply has no notion of multiple distinct actors.
- Reader B: Different `DELEGATE` statements in the same process are expected to route to different actors based on the nature of the `<work>` identifier (e.g., `DELEGATE security-review` vs. `DELEGATE readiness-verification` in the FORK example clearly go to different reviewers), meaning actor routing is implied by convention/naming even though the grammar has no explicit field for it.

This affects whether a runtime needs a single fixed delegate target or a routing table keyed by work identifiers — a significant implementation design decision the spec doesn't settle.

**Assumption made:** Treated as intentionally implementation-defined (semantic principles support this), but flagged since the practical routing question remains genuinely open.

---

## Summary of unresolved items (assumptions where made)

| # | Item | Resolution used here (if any) |
|---|------|-------------------------------|
| 1 | `AUTO` valid syntax | None possible — unresolved |
| 2 | `WHEN` no-match / multi-match behavior | None — unresolved |
| 3 | `FORK`/`JOIN` correspondence & "required" flows | None — unresolved |
| 4 | `STOP`/`BREAK` inside `FORK` branches | None — unresolved |
| 5 | `BREAK` + nested `LOOP` naming | Assumed innermost-loop scoping; name treated as non-functional |
| 6 | `WAIT` vs. implicit suspension in `HITL`/`DELEGATE` | None — unresolved |
| 7 | `FALLBACK` scope (HITL-only vs. general) | None — unresolved |
| 8 | Dot-notation outcome identifiers | Assumed informal/non-formal grammar |
| 9 | `REQUIRE` scope/duration and failure path | None — unresolved |
| 10 | Indentation grammar unit/rule | None — unresolved |
| 11 | Overloaded `→` token across constructs | None — unresolved |
| 12 | Concurrent `TRANSITION` conflicts | None — unresolved |
| 13 | `EMIT` without prior `VERIFY` | None — unresolved |
| 14 | `DELEGATE` actor identification | Assumed implementation-defined, per explicit semantic principle |
