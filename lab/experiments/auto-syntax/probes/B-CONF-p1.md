# Ambiguities in `DSL` — HITL / AUTO / FALLBACK / WHEN

Method: I read the spec as an implementer who must execute programs written in it, focusing on how `HITL`, `AUTO`, and `FALLBACK` interact with `WHEN`. Below is every place I found unclear, contradictory, or underspecified, with the section it comes from, the exact text, the problem, and two divergent readings.

---

## 1. What does "the `WHEN <name>.<answer>` constructs that follow" actually range over?

**Section:** `HITL`

**Quote:**
> `<name>` names the decision. The response establishes the outcome `<name>.<answer>`, where `<answer>` is one of the answers tested by the `WHEN <name>.<answer>` constructs that follow.

**Problem:** "follow" is not defined precisely. It could mean (a) the immediately adjacent sibling statements at the same indentation as the `HITL`, (b) any `WHEN` anywhere later in declaration order in the entire program regardless of nesting/branch, or (c) something in between (e.g. only within the enclosing flow/scope of the `HITL`). This matters because it determines the legal "vocabulary" of answers for a decision, which in turn determines what counts as "insufficient" (see item 2).

**Two readings:**
- Reader A: "follow" means textually anywhere later in the program, so a `WHEN merge.approved` written deep inside some unrelated `FORK` branch three pages later still counts toward defining `merge`'s valid answers.
- Reader B: "follow" means only the statements written directly after the `HITL` at the same indentation (as in every example given), i.e. a local syntactic pairing, and a `WHEN` elsewhere with the same name is irrelevant or even a separate, unrelated decision that happens to share an identifier.

---

## 2. Named `HITL` with no `WHEN` that references it — is there a defined vocabulary of answers at all?

**Section:** `HITL`

**Quote:**
> A response that corresponds to none of these answers is insufficient (see `FALLBACK`). The name may be omitted when no `WHEN` refers to the decision.

**Problem:** The rule for the *omitted* case is given ("may be omitted"), but the rule for a *named* `HITL` with zero corresponding `WHEN` statements anywhere is not. If sufficiency is defined purely as "matches one of the answers tested by following `WHEN`s," and there are none, then by the letter of the text **every** response is insufficient (there is nothing to correspond to), which would force `FALLBACK` every time — an absurd result the spec surely doesn't intend, but nothing rules it out or defines an alternative.

**Two readings:**
- Reader A: If no `WHEN` follows, sufficiency is undefined/vacuous, so any non-empty response is accepted as "usable" (the name is just documentation, since nothing consumes the outcome).
- Reader B: Per the literal text, with no answer set to match against, no response can ever be "one of the answers tested," so the `HITL` can never resolve normally and always falls to `FALLBACK` (or waits forever if none is given) — a self-contradiction the program author must avoid but that the DSL does not flag as invalid.

---

## 3. What happens after a `FALLBACK` flow finishes, if it doesn't `STOP`/`BREAK`?

**Section:** `FALLBACK` / `HITL`

**Quote:**
> The flow containing a `HITL` waits at the `HITL` until either a usable response is available or its `FALLBACK` flow is used ... Statements after the `HITL` construct, at the indentation of `HITL`, are the normal flow. They are not part of the fallback flow.

**Problem:** The spec never states what happens *after* the fallback flow completes, if the fallback flow does not explicitly `STOP` or `BREAK`. Since no outcome `<name>.<answer>` was ever established (the response was insufficient/unavailable), does execution then "fall through" into the normal flow after the `HITL` — including any `WHEN <name>.<answer>` checks, all of which would simply fail to match (an unmatched `WHEN` "is not an error")? Or is the fallback flow meant to be a terminal alternative to the wait, such that continuing into the normal post-`HITL` flow is not sanctioned unless the fallback flow itself explicitly returns control there?

**Two readings:**
- Reader A: Ordinary sequential-flow rules apply uniformly: once the fallback flow's last statement completes, execution simply continues with whatever statement follows the `HITL` construct (same as any other flow), so the following `WHEN`s are reached and silently do nothing (since no outcome matches).
- Reader B: A `FALLBACK` exists precisely to *replace* the interrupted decision-dependent continuation; letting execution silently fall through into `WHEN <name>.<answer>` checks that can never match is a degraded/partial continuation of the very decision the `HITL` gates — which the spec's own principle for `REQUIRE` explicitly disallows ("must not proceed as if the requirement were satisfied... does not permit continuing in a degraded or partial mode"). By analogy, a well-formed fallback must always terminate the flow itself (`STOP`, `BREAK`, or an explicit redirect), and a fallback that doesn't is implicitly incomplete — but this constraint is nowhere stated for `HITL`/`FALLBACK`, unlike the explicit ban under `REQUIRE`.

---

## 4. Inconsistency between `REQUIRE`'s explicit anti-degraded-mode rule and the silence on the same issue for `HITL`

**Section:** `REQUIRE` vs. `HITL`/`FALLBACK`

**Quote (REQUIRE):**
> If a required condition cannot be satisfied, execution must not proceed as if the requirement were satisfied... "not as if satisfied" does not permit continuing in a degraded or partial mode.

**Quote (HITL/WHEN):**
> If the condition is not satisfied, the flow is skipped and execution continues with the statement after the `WHEN` construct. An unmatched `WHEN` is not an error.

**Problem:** `REQUIRE` is given an explicit, strong guarantee against silently continuing without its precondition. `HITL` has an analogous precondition-like role ("establishes a human decision boundary"), but when its decision goes unresolved (insufficient response, `FALLBACK` runs but doesn't stop execution — see item 3), nothing prevents the process from continuing past all the `WHEN <name>.<answer>` gates as if the decision boundary didn't exist, because "unmatched WHEN is not an error." The spec gives no equivalent guarantee for `HITL` that this is disallowed.

**Two readings:**
- Reader A: The two constructs are simply different by design — `REQUIRE` is a hard precondition, `HITL`+`WHEN` is explicitly *not* an all-or-nothing gate (each `WHEN` is independent, unmatched is fine), so falling through with no branch taken is intended, ordinary behavior.
- Reader B: This is an inconsistency in the DSL's stated design principles: a human decision boundary should carry the same "don't proceed as if satisfied" guarantee that `REQUIRE` explicitly states, and the omission means well-formed programs must defensively add `WHEN` coverage for every case, with no DSL-level enforcement that they did.

---

## 5. Is `AUTO`'s automatically-resolved answer constrained to the same answer set a human response would be checked against?

**Section:** `AUTO`

**Quote:**
> Automatic resolution is permitted only when the agent can determine a single protocol-compatible decision from the available information and applicable criteria... The outcome `<name>.<answer>` is established exactly as if a human had given that answer.

**Problem:** For a *human* response, sufficiency is explicitly tied to matching "one of the answers tested by the `WHEN <name>.<answer>` constructs that follow" (see item 1). For `AUTO`, the parallel constraint is never restated — the table only says the agent must reach "a single protocol-compatible decision," and "protocol-compatible" is not defined anywhere in the spec (it appears exactly once). It's unclear whether:
(a) the agent's candidate answers are implicitly limited to the same finite set defined by the following `WHEN`s (so `AUTO` can never invent an answer with no corresponding `WHEN`), or
(b) `AUTO` can establish any identifier as `<answer>`, "protocol-compatible" meaning something looser (e.g. consistent with the surrounding process description, not necessarily with the DSL program's own `WHEN` branches), potentially producing an outcome that no `WHEN` in the program tests for, silently vanishing (equivalent to case where none of the WHENs match).

**Two readings:**
- Reader A: "Protocol-compatible" just means "matches one of the finite answers the surrounding `WHEN`s define" — the same closed vocabulary as the human case — since the sentence right before it in the `HITL` section establishes that vocabulary and `AUTO` is described as resolving the same `HITL`.
- Reader B: "Protocol-compatible" is a broader, process-level notion (e.g. compliant with organizational policy/authority) independent of which `WHEN`s happen to appear afterward in this particular program text, so `AUTO` could legitimately resolve to an answer with no matching `WHEN`, and the resulting outcome would simply never be observed by any conditional — behavior the spec doesn't flag as a problem or forbid.

---

## 6. Persistence and scope of `<name>.<answer>` outcomes — across loop iterations, and across the whole program's namespace

**Section:** `HITL`, `LOOP`, `JOIN`

**Quote (JOIN):**
> Outcomes established inside the branches remain available to `WHEN` constructs after the `JOIN`.

**Quote (HITL):**
> `<name>` names the decision.

**Problem:** `JOIN`'s wording strongly implies outcomes are a form of *persistent, program-global* state (like `TRANSITION`'s single current state), available to any later `WHEN` regardless of scope. But nothing says whether:
- a `HITL:<name>` outcome is overwritten each time that `HITL` statement executes (e.g., inside a `LOOP`, once per iteration), the way `TRANSITION` explicitly says "the most recently executed `TRANSITION` ... wins"; and
- if two unrelated `HITL:<name>` statements elsewhere in the program happen to share the same `<name>` identifier, whether they collide in a single global namespace or are somehow scoped separately (nothing in "Identifier" or "Scope" addresses outcome namespacing).

This directly affects `WHEN` correctness: inside a `LOOP` containing `HITL:merge(...)` followed later by `WHEN merge.approved`, does a stale `merge.approved` from a *previous* iteration accidentally satisfy a `WHEN` reached *before* the current iteration's `HITL:merge` has run again?

**Two readings:**
- Reader A: Outcomes behave like `TRANSITION` state — a single named slot, global for the whole execution, overwritten on each new resolution, and readable by any `WHEN` anywhere later in declaration order (including a prior iteration's still-live value if the loop hasn't re-run the `HITL` yet this iteration).
- Reader B: Each execution of a `HITL:<name>` statement creates a fresh, use-once outcome that is only meaningful for the `WHEN`s reached before the next execution of the same `HITL` (or perhaps only within the same loop iteration), so a `WHEN` reached "too early" relative to the `HITL` it's paired with should be treated as not-yet-determined rather than reading a stale prior value — but the DSL gives no mechanism to distinguish "not yet resolved" from "resolved to a value that just doesn't match."

---

## 7. No `FALLBACK` present, and the response is unavailable or insufficient — is the wait indefinite?

**Section:** `HITL` / `FALLBACK`

**Quote:**
> The flow containing a `HITL` waits at the `HITL` until either a usable response is available or its `FALLBACK` flow is used.

**Problem:** The grammar makes `FALLBACK` optional (`[ INDENT , "→" , "FALLBACK" ... ] ]`). If a `HITL` has no `FALLBACK` and the response turns out to be insufficient (e.g., "an off-topic reply"), the spec's own disjunction ("a usable response ... or its FALLBACK flow is used") has neither disjunct available — a usable response didn't arrive, and there is no fallback to use. `WAIT` explicitly says "If the event never becomes available, execution remains suspended at the `WAIT`," but no equivalent explicit statement is made for a `HITL` lacking `FALLBACK`.

**Two readings:**
- Reader A: By analogy with `WAIT`'s explicit indefinite-suspension rule, a `HITL` with no `FALLBACK` and an insufficient/unavailable response simply keeps waiting (presumably re-prompting or continuing to wait) forever, exactly like an unresolved `WAIT`.
- Reader B: Because `FALLBACK` is specifically "the flow to use when an expected response is unavailable or insufficient," a `HITL` with no `FALLBACK` at all might be read as implicitly asserting that only a usable response is possible/expected for that decision, making an insufficient response for such a `HITL` an unmodeled situation the spec simply doesn't define — potentially a defect in the *program*, not something the DSL runtime needs to handle by waiting.

---

## 8. A human response that corresponds to more than one tested answer

**Section:** `HITL`

**Quote:**
> A response that corresponds to none of these answers is insufficient (see `FALLBACK`).

**Problem:** The spec defines insufficiency only for the "zero matches" case. It never addresses a response that plausibly corresponds to *more than one* of the tested answers (e.g., a reply that could reasonably be read as both `merge.approved` and `merge.declined` depending on interpretation). Since `HITL` establishes a single outcome `<name>.<answer>`, it's unclear whether such a response is (a) automatically treated as insufficient by extension of the same principle, (b) resolved by some unstated tie-breaking rule, or (c) simply out of scope for the DSL to define (left to the runtime/human-interface layer).

**Two readings:**
- Reader A: Since a `HITL` can only ever establish one `<answer>`, any response that doesn't cleanly map to exactly one tested answer is "insufficient" by the same logic as a zero-match response — ambiguity is treated the same as absence.
- Reader B: The spec's definition of insufficiency is textually narrow ("corresponds to none of these answers"), so a response matching multiple answers is technically outside the stated definition and not insufficient — leaving genuinely undefined which single `<answer>` outcome (if any) gets established.

---

## 9. Can a `FALLBACK` flow contain another `HITL` (possibly with `AUTO`) to retry the decision?

**Section:** `FALLBACK`, Grammar

**Quote:**
> A fallback may explicitly terminate, defer, request another action, or otherwise handle the unresolved situation according to the surrounding process.

**Problem:** "Request another action" hints that a `FALLBACK` flow could re-ask, but the grammar's `flow` production (`item = "→" , statement , ...`) allows any `statement` — including `hitl` — inside a `FALLBACK`'s flow, since `FALLBACK`'s body is defined as a generic `flow`. Nothing in the `FALLBACK` or `HITL` sections discusses whether a nested `HITL` inside a fallback flow is a fresh, independent decision (with its own name/answers) or is somehow meant to be a "retry" of the outer decision reusing the same `<name>`. If it reuses the same name, item 6's namespace/overwrite question resurfaces; if it must use a different name, that's never stated either.

**Two readings:**
- Reader A: A nested `HITL` inside `FALLBACK` is just an ordinary, independent `HITL` statement like any other, unrelated to the outer decision except by hand-authored convention; the outer `WHEN <name>.<answer>` checks after the original `HITL` are unaffected by whatever the nested one establishes (unless it happens to reuse the same name, which would be an authoring choice, not a DSL-defined "retry").
- Reader B: "Request another action" specifically licenses a retry pattern where the nested `HITL` is expected to reuse the outer `<name>` so that the original `WHEN <name>.<answer>` constructs after the whole `HITL` construct can still pick up the eventual answer — but the DSL provides no syntax or rule distinguishing this "retry" semantics from an ordinary unrelated `HITL`.

---

## 10. `BREAK` inside a `FALLBACK` flow that sits within a `LOOP`

**Section:** `BREAK`, `FALLBACK`

**Quote (BREAK):**
> "The current `LOOP`" is the innermost `LOOP` that encloses the `BREAK`... `BREAK` takes effect immediately: the remaining statements of the current iteration, including any later `WHEN` constructs in the loop body, are not executed.

**Problem:** The `BREAK` rule is illustrated only for loop bodies and `WHEN` flows; the `FALLBACK` section's own example places `BREAK`'s sibling `STOP` (not `BREAK`) inside a fallback flow, and never shows a `FALLBACK` nested inside a `LOOP`. Rule 556 in Scope says "Any statement... may appear inside a loop body, a `WHEN` flow, a fallback flow, or a `FORK` branch, unless a rule in this specification says otherwise," which suggests lexical enclosure should apply uniformly and a `BREAK` inside a `FALLBACK` flow that is itself inside a `LOOP` breaks that innermost enclosing `LOOP`. But because no example or explicit statement confirms this for `FALLBACK` specifically (unlike `WHEN`, which is explicitly cross-referenced in the `BREAK` section), a careful reader could still wonder whether `FALLBACK`'s special "response handling" status (it "does not mean 'execute this flow after the normal flow'") makes it exempt from ordinary lexical-enclosure treatment for control constructs like `BREAK`.

**Two readings:**
- Reader A: `FALLBACK` is just another nested flow like a `WHEN` flow or `FORK` branch for the purposes of lexical scoping; `BREAK` inside it exits the nearest enclosing `LOOP` exactly as it would from anywhere else, per the general Scope rule.
- Reader B: Because `FALLBACK` represents an exceptional "response was unusable" path rather than ordinary sequential continuation, and the spec never explicitly walks through a `LOOP` containing a `HITL`+`FALLBACK`, a reader could reasonably treat this combination as unaddressed by the spec's worked examples and be unsure whether `BREAK` there is even well-formed, or whether it should instead be understood as breaking only out of some implicit "decision-handling" scope rather than the enclosing `LOOP`.

---

## 11. Does an `AUTO`-resolved outcome, once established, behave exactly like a `TRANSITION`'s "latest wins" semantics if the same `HITL:<name>` executes again later?

**Section:** `AUTO`, `TRANSITION`

**Quote (AUTO):**
> The outcome `<name>.<answer>` is established exactly as if a human had given that answer.

**Quote (TRANSITION, for contrast):**
> The process has exactly one current state. Each `TRANSITION` replaces it, so the most recently executed `TRANSITION` determines the current state.

**Problem:** `TRANSITION` explicitly defines overwrite semantics for repeated execution. `HITL`/`AUTO` never states whether re-executing the same named `HITL` (e.g., on a later `LOOP` iteration) replaces a previously established `<name>.<answer>` outcome, leaves both values simultaneously "true" in some multi-valued sense, or is even permitted to differ from the earlier answer. This is a direct extension of item 6 but specifically sharpened for `AUTO`: since `AUTO` can silently resolve differently on different iterations if "the available information" changes, and `WHEN` checks the outcome by name, whether old values are cleared or overwritten materially changes program behavior.

**Two readings:**
- Reader A: By analogy with `TRANSITION`, outcomes are also single mutable slots keyed by `<name>`, so each new resolution (human or `AUTO`) simply overwrites the prior `<answer>` for that name, and only the latest value is visible to subsequent `WHEN`s.
- Reader B: Since the spec never says this for `HITL` outcomes (only for `TRANSITION`'s state), a reader could instead assume each `<name>.<answer>` pair is its own permanent fact once established (multiple distinct outcomes could coexist for the same name across iterations, e.g. `merge.approved` from iteration 1 and `merge.declined` from iteration 2 both being "true" historically), leaving it undefined which one a later `WHEN merge.approved` should test against.

---

## Assumptions made where the specification does not decide

Because the task asks me to flag rather than silently resolve these gaps, I have not assumed a single answer for any of the eleven items above. Where I needed a minimal working assumption just to describe the problem coherently, I assumed:
- Outcomes named by `HITL`/`AUTO` are, at minimum, readable by some `WHEN` after execution reaches it (the disagreement is over *how far* "after" extends and *whether stale values persist*), since the spec plainly intends `WHEN <name>.<answer>` to work at all.
- "Well-formed" analysis (rejecting a program outright) applies only to the explicit `"invalid"/"may only"/"must not contain"` rules given in the spec (per the Programs/fragments/validity section); none of the eleven items above are stated in that explicit vocabulary, so I have treated them as behavioral/semantic ambiguities in an otherwise well-formed program, not as well-formedness violations.
