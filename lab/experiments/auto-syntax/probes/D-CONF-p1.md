# Ambiguities in `go_harness` DSL — HITL / AUTO / FALLBACK / WHEN

Scope note: per the task, this list draws only on the `<specification>` block given. No implementation choice is assumed beyond what the text requires; every point below is a place where the text itself under-determines behavior for someone who has to write or execute a process with it.

---

## 1. `WHEN` conditions can't distinguish a `VERIFY` outcome from a `HITL` outcome

**Sections:** `VERIFY`, `HITL`, `Conditional Flow`

**Quotes:**
- VERIFY: "Verification may establish outcomes that can be used by `WHEN`." (example: `implementation.accepted`, `implementation.rejected`)
- HITL: "The response establishes the outcome `<name>.<answer>`..."
- Conditional Flow: "`<condition>` has the form `<identifier>.<identifier>`, for example `implementation.accepted`."

**Problem:** Both `VERIFY <result>` and `HITL:<name>(...)` establish outcomes using the exact same `identifier.identifier` shape, and nothing in the grammar or semantics tags an outcome with its origin (verification vs. human/AUTO decision). If a process reuses the same identifier for both — e.g. `VERIFY review` and `HITL:review("Approve?")` — a later `WHEN review.accepted` is structurally indistinguishable from `WHEN review.approved` in provenance, and if the two happen to share an answer word (unlikely but not forbidden, e.g. both could plausibly use `.rejected`), there is no rule for which source's value a `WHEN` reads, or whether the two outcome namespaces are meant to be entirely separate.

**Two readings:**
- (A) Outcomes are name-scoped global state regardless of origin; `VERIFY x` and `HITL:x` targeting the same name is a program bug the DSL doesn't need to guard against, and authors are simply expected never to collide names.
- (B) The DSL implicitly maintains two separate outcome namespaces (verification results vs. decision names), so `review.rejected` from a `VERIFY` and `review.declined` from a `HITL:review` can coexist safely under the same base identifier — but this separation is never stated, so a runtime author could just as easily implement (A).

---

## 2. Scope of "the `WHEN <name>.<answer>` constructs that follow"

**Section:** `HITL`

**Quote:** "The response establishes the outcome `<name>.<answer>`, where `<answer>` is one of the answers tested by the `WHEN <name>.<answer>` constructs that follow."

**Problem:** "That follow" is never defined precisely. It could mean only the `WHEN`s immediately after the `HITL` at the same indentation (the "normal flow" per the later line "Statements after the `HITL` construct, at the indentation of `HITL`, are the normal flow"), or it could mean anywhere later in the program text, including inside nested scopes, other branches after a `JOIN`, or even inside a different `LOOP` iteration. This matters because it defines the entire accepted-answer vocabulary for the decision. Compare this to the `JOIN` section's explicit statement that "Outcomes established inside the branches remain available to `WHEN` constructs after the `JOIN`" — i.e., for `VERIFY`, outcome visibility is explicitly non-local/persistent. `HITL` never gets an equivalent explicit persistence statement; it only says answers are "tested by... constructs that follow," which reads as a narrower, more local notion of scope.

**Two readings:**
- (A) "Follow" just means "textually after, anywhere in the program" — establishing the outcome makes `<name>.<answer>` available like `VERIFY` results, persisting indefinitely, checkable in any later `WHEN` no matter how far or how nested.
- (B) "Follow" means the immediate sibling `WHEN`s in the normal flow right after the `HITL`; the outcome is only guaranteed meaningful there, and a `WHEN` testing it elsewhere (a different branch, after a loop iteration boundary, etc.) is undefined behavior since it's outside what the spec calls "the constructs that follow."

---

## 3. What counts as a response "corresponding" to a tested answer

**Section:** `HITL`, `FALLBACK`

**Quote:** "A response that corresponds to none of these answers is insufficient (see `FALLBACK`)." / FALLBACK: "**Insufficient** means a response arrives but does not provide the requested decision or input. Examples are 'I haven't looked yet', an off-topic reply, or an answer to a different question."

**Problem:** "Corresponds to" is not defined — is it exact string match against the `<answer>` tokens used in the following `WHEN`s (e.g. literally the word `approved`), or semantic equivalence (e.g. a human replying "yes, go ahead" corresponding to `merge.approved`)? The two given FALLBACK examples of "insufficient" ("I haven't looked yet", an off-topic reply) are clearly non-answers, but they don't resolve the harder boundary case: a response that answers the question but in different words than the literal `<answer>` identifier.

**Two readings:**
- (A) Correspondence is syntactic: the response must map to one of the literal answer identifiers (perhaps via some UI that offers exactly those choices), so anything not exactly one of them is insufficient by construction.
- (B) Correspondence is semantic: the runtime/agent must interpret free-form human replies and map them onto the closest matching declared answer, only falling back when no reasonable mapping exists — meaning what counts as "insufficient" is a judgment call left entirely to the implementation.

---

## 4. No stated rule for repeated/duplicate `HITL` names (contrast with `TRANSITION`)

**Section:** `HITL`, `TRANSITION`

**Quote:** TRANSITION: "The process has exactly one current state. Each `TRANSITION` replaces it, so the most recently executed `TRANSITION` determines the current state." HITL has no analogous statement.

**Problem:** The spec is careful to state an explicit "most recent wins" rule for `TRANSITION` state, but gives no equivalent rule for what happens if the same `<name>` is used by more than one `HITL` construct (e.g., inside a `LOOP` body executed on each iteration, or in two different branches). Does each execution of `HITL:merge(...)` overwrite a single persistent `merge.<answer>` outcome (analogous to TRANSITION), or does each `HITL:merge` execution produce an independent, freshly-scoped outcome that only the immediately following `WHEN`s can see (per ambiguity #2)? The silence is conspicuous given the spec explicitly addressed the analogous question for `TRANSITION`.

**Two readings:**
- (A) By analogy with `TRANSITION`, HITL outcomes are global and the latest resolution of a given `<name>` overwrites any prior one.
- (B) HITL outcomes are local to each execution/flow instance (like a fresh local variable each time), so re-running `HITL:merge` in a loop doesn't affect or get confused with a previous iteration's `merge.approved`/`merge.declined`, and there's no shared global slot at all.

---

## 5. `WHEN` referencing a `HITL` name that was never declared (or whose `HITL` is unnamed)

**Section:** `HITL`, `Programs, fragments, and validity`

**Quote:** "The name may be omitted when no `WHEN` refers to the decision." / Validity: "A program that violates a rule stated as 'invalid', 'may only', or 'must not contain' in this specification is not well-formed."

**Problem:** The spec states the converse condition for when a name may be *omitted*, but never states what happens if a `WHEN <name>.<answer>` appears with no corresponding `HITL:<name>` anywhere in the program (a dangling reference), or if a `HITL` is left unnamed while a `WHEN` elsewhere still references some identifier that happens to match nothing. Because this isn't phrased as "invalid," "may only," or "must not contain," it doesn't fall under the well-formedness rule quoted above — leaving it unclear whether such a program is simply rejected, or is well-formed and the dangling `WHEN` is just permanently unsatisfied.

**Two readings:**
- (A) A `WHEN` referencing a name with no matching `HITL` anywhere is a static error, making the whole program not well-formed (by the spirit, if not the letter, of the naming rule).
- (B) It is perfectly well-formed; conditions are just identifiers evaluated against whatever outcomes happen to exist at runtime, and one that was never established is simply "not satisfied" like any other unmet `WHEN` condition — no different from a typo.

---

## 6. Parsing of "must not be **silently** replaced ... unless marked `AUTO`"

**Section:** `HITL`

**Quote:** "`HITL` must not be silently replaced by an agent decision unless that `HITL` is explicitly marked with `AUTO`."

**Problem:** The sentence is structurally ambiguous about what the `AUTO` exception attaches to. Does `AUTO` license replacement *and* silence together, or does it only license the replacement while the "not silently" requirement still stands (i.e., even an `AUTO`-resolved decision must be recorded/announced somewhere, just not asked of a human)? The rest of the `AUTO` section never uses the word "silent" again, so this is never resolved.

**Two readings:**
- (A) Without `AUTO`: never replace a `HITL` with an agent decision, period. With `AUTO`: the agent may resolve it, and doing so silently (no notice to anyone) is fine — `AUTO` cancels the whole prohibition.
- (B) "Silently" is the operative word throughout: an agent must never resolve a `HITL` without some observable trace of having done so; `AUTO` only grants permission to *make* the decision without asking a human, but the resolution must still be non-silent (e.g., logged/exposed) exactly as if a human decision were recorded.

---

## 7. `AUTO` on an unnamed `HITL`: what, if anything, gets resolved?

**Section:** `AUTO`, `HITL`, `Statement` grammar

**Quote:** Grammar: `hitl = [ "AUTO", NL ], "HITL", [ ":", identifier ], "(", string, ")", NL, ...` — the name is optional even when `AUTO` is present. AUTO: "The outcome `<name>.<answer>` is established exactly as if a human had given that answer."

**Problem:** The grammar permits `AUTO` directly before an *unnamed* `HITL("...")`. But the entire description of what `AUTO` *does* is phrased in terms of establishing `<name>.<answer>`. If there is no `<name>`, it's unclear what "sufficiently determined" even means (determined to be *what*, if there's no answer variable to set and, per the HITL naming rule, presumably no following `WHEN` cares about the answer) — and it's unclear whether `AUTO` on an unnamed `HITL` is simply a no-op degenerate case ("just don't ask, since nothing downstream reads the result") or a malformed combination the spec forgot to forbid.

**Two readings:**
- (A) `AUTO` on an unnamed `HITL` is legitimate and simply means "resolve without asking a human whenever possible," with no outcome recorded anywhere (consistent with unnamed HITL never needing an outcome) — the only effect is skipping/not-skipping the human interaction itself.
- (B) `AUTO`'s defined behavior is meaningless without a `<name>` to bind an answer to, so `AUTO` combined with an unnamed `HITL` is implicitly invalid even though the grammar as written doesn't forbid it — an unstated grammar/semantics mismatch.

---

## 8. "Protocol-compatible decision" is used but never defined

**Section:** `AUTO`

**Quote:** "Automatic resolution is permitted only when the agent can determine a single protocol-compatible decision from the available information and applicable criteria."

**Problem:** This is the only occurrence of the phrase "protocol-compatible decision" in the entire specification. No other section defines "the protocol," so it's unclear what a decision must be compatible *with* — the enclosing process definition generally, the specific set of answers named by the following `WHEN <name>.<answer>` constructs, some external contract not modeled in the DSL at all, or just a loose synonym for "valid."

**Two readings:**
- (A) "Protocol-compatible" just means "one of the answers the surrounding `WHEN` constructs are prepared to handle" (tying back into ambiguity #2/#9) — i.e., AUTO must land on a value some `WHEN` actually tests.
- (B) "Protocol" refers to some broader, unstated governance/authorization framework external to the DSL text (consistent with "the agent does not have the authority required to make the decision" appearing right after as a separate uncertainty example) — meaning compatibility can't be checked from the DSL program alone at all.

---

## 9. Is `AUTO`'s resolved answer required to be one of the answers tested by the following `WHEN`s?

**Section:** `AUTO`, `HITL`

**Quote:** HITL: "...`<answer>` is one of the answers tested by the `WHEN <name>.<answer>` constructs that follow." AUTO: "The outcome `<name>.<answer>` is established exactly as if a human had given that answer."

**Problem:** The vocabulary-of-valid-answers rule ("one of the answers tested by the `WHEN`s that follow") is stated in the `HITL` section talking about *human* responses. `AUTO` says its resolution is established "exactly as if a human had given that answer," which could be read as inheriting that same constraint (the agent may only resolve to a value some following `WHEN` tests), or could be read more loosely as only describing the *mechanism* of establishment (no human asked) without inheriting the vocabulary restriction, potentially letting `AUTO` set an answer no `WHEN` ever checks (which would then just never match anything, silently).

**Two readings:**
- (A) `AUTO` inherits the same constraint as a human response: it may only resolve to one of the answers explicitly tested by a following `WHEN`; anything else isn't "a single protocol-compatible decision" and must fall through to asking a human.
- (B) `AUTO` is only constrained by "sufficiently determined," independent of what `WHEN`s happen to test afterward; it could validly establish an answer that isn't tested by any `WHEN`, in which case downstream `WHEN`s simply never fire — arguably still "resolved," just not actionable.

---

## 10. The uncertainty threshold ("sufficiently determined") is inherently open-ended

**Section:** `AUTO`

**Quote:** "Uncertainty exists when the agent cannot reliably determine that decision. Examples include: ... A confidence score alone does not establish certainty."

**Problem:** "Examples include" signals a non-exhaustive list, and "reliably determine" / "sufficiently determined" are never given operational criteria. The one concrete guardrail offered is negative ("a confidence score alone does not establish certainty") but no positive test is given for what *does* establish certainty. This is presumably intentional (the DSL disclaims prescribing "an algorithm or confidence threshold" under Semantic Principles), but it directly means two implementers/agents following the same spec, same inputs, and same criteria could reach opposite conclusions about whether a given decision is "sufficiently determined," with no way to arbitrate which one is DSL-compliant.

**Two readings:**
- (A) This vagueness is deliberate and delegates the threshold entirely to the surrounding process/organization's judgment; any reasonable, explainable threshold an agent applies is spec-compliant by design.
- (B) The list of uncertainty examples, though introduced with "include," is meant to be treated as effectively exhaustive/definitive for compliance purposes (i.e., only these situations count as disqualifying), so an agent that invents *additional* reasons to treat a decision as uncertain (or as certain) is going beyond or short of what the spec intends.

---

## 11. Does execution rejoin the normal flow after a `FALLBACK` that doesn't `STOP`/`BREAK`?

**Section:** `FALLBACK`

**Quote:** "The fallback flow is used only when the expected response cannot be used to continue the normal flow." / "A fallback may explicitly terminate, defer, request another action, or otherwise handle the unresolved situation according to the surrounding process." / Both worked examples end in `STOP`.

**Problem:** The phrase "cannot be used to continue the normal flow" suggests the fallback is a *replacement* for continuing, implying that once a fallback runs, the normal post-`HITL` flow is not resumed. But the only two examples given both explicitly `STOP`, so neither example clarifies what happens if the fallback flow runs to completion *without* `STOP` or `BREAK` (e.g., a fallback that only does `TRANSITION "Deferred"` and then ends). Per the general `WHEN`-flow rule these `→` flows are modeled after ("Afterwards, execution continues with the statement after the `WHEN` construct, unless the flow executed `BREAK` or `STOP`"), one could argue by analogy that after a non-terminating `FALLBACK` flow, execution *does* continue with the statement after the `HITL` construct — which would then let subsequent `WHEN <name>.<answer>` checks run against a `<name>` that was never established (see ambiguity #5), silently matching nothing. The spec never says whether that's what's supposed to happen, or whether a `FALLBACK` implicitly halts the containing flow (as if it were its own terminal branch) regardless of whether it explicitly `STOP`s.

**Two readings:**
- (A) `FALLBACK` is structurally just another `→`-flow (per the grammar, which reuses `flow` for it), so the general flow-continuation rule applies uniformly: after the fallback flow finishes (without `STOP`/`BREAK`), execution proceeds to the statement after the whole `HITL` construct, and any following `WHEN <name>.<answer>` simply won't match since no answer was established.
- (B) Because "insufficient/unavailable" means the decision could not be made at all, a `FALLBACK` flow that doesn't itself `STOP`/`BREAK` is nonetheless a dead end for that decision — the surrounding process is expected to design fallbacks that always exit (via `STOP`, `BREAK`, or leading into an unrelated part of the process), and running past a `HITL` construct whose decision was never resolved into the same normal flow that assumed resolution would be a modeling error, even though the grammar doesn't forbid it.

---

## 12. Can a `FALLBACK` flow itself contain a `HITL` (possibly re-asking, possibly under the same name)?

**Section:** `FALLBACK`

**Quote:** "`FALLBACK` does not authorize the agent to invent a replacement decision." / "A fallback may explicitly ... request another action, or otherwise handle the unresolved situation according to the surrounding process."

**Problem:** Nothing in the grammar (`flow = item, { item }`) forbids a `HITL` statement from appearing inside a `FALLBACK` flow — it's an ordinary `statement`, and `FALLBACK`'s flow is just a `flow`. "Request another action" even suggests re-engaging a human is an expected fallback pattern. But it's unclear whether such a nested `HITL` could legitimately target the *same* decision name (effectively "ask again") — which seems like the natural reading of "request another action" for an unavailable/insufficient response — or whether doing so would violate "does not authorize the agent to invent a replacement decision," since re-asking under the same name and later matching `WHEN <name>.<answer>` looks exactly like using the fallback to eventually still produce the original decision through a side door.

**Two readings:**
- (A) A `FALLBACK` may contain a fresh `HITL:<name>(...)` re-asking the same question; this isn't "inventing" a decision, it's legitimately re-soliciting the one that was never obtained, and the outcome it establishes is exactly the original decision, just obtained on a second attempt.
- (B) "Does not authorize the agent to invent a replacement decision" forbids the fallback from ever producing `<name>.<answer>` itself (by any means, including re-asking under the same name), because that would let an agent effectively route around a failed/insufficient response and manufacture the very outcome the fallback exists to handle the *absence* of; a fallback may only take actions that don't resolve the original decision (e.g., transition to a different state, ask an unrelated question, stop).

---

## 13. "Insufficient" is itself a judgment call with only loose examples

**Section:** `FALLBACK`

**Quote:** "**Insufficient** means a response arrives but does not provide the requested decision or input. Examples are 'I haven't looked yet', an off-topic reply, or an answer to a different question."

**Problem:** Like the `AUTO` uncertainty threshold (ambiguity #10), "does not provide the requested decision or input" is a general test applied via three illustrative (not exhaustive — "Examples are") cases, all of which are unambiguous non-answers. It gives no guidance on borderline cases: a hedge ("probably, but I'd double check X first"), a conditional answer ("approve it if tests pass"), or a partial answer to a multi-part `HITL`. Whether these count as "insufficient" (triggering `FALLBACK`) or as usable (continuing the normal flow, perhaps via the `AUTO`/agent-judgment path or via direct interpretation) is left entirely to whoever runs the process.

**Two readings:**
- (A) Any response that doesn't cleanly resolve to exactly one of the declared `<answer>` tokens is insufficient by default — hedges and conditionals fall to `FALLBACK` unless a human is asked to clarify further (itself unspecified as a mechanism).
- (B) "Insufficient" is meant narrowly, limited to responses like the three given examples (non-answers, off-topic, wrong-question); anything that substantively engages with the actual question, even if hedged or conditional, should be interpreted (by the agent or runtime) into one of the declared answers rather than triggering `FALLBACK`.

---

## 14. Does `FALLBACK` still apply when `AUTO` fails to resolve and the resulting human response is itself unusable?

**Section:** `AUTO` (execution table), `FALLBACK`

**Quote:** AUTO table, row "yes / no (uncertain...)": "The human is asked, as for a `HITL` without `AUTO`." / "`FALLBACK` is used only if the human is asked and the response is unavailable or insufficient."

**Problem:** The AUTO table's third row says the uncertain case is handled "as for a `HITL` without `AUTO`," which by cross-reference to the `FALLBACK` section implies `FALLBACK` semantics fully apply here too. But this is only established by chaining two separate sections together — the `AUTO` section's table never itself mentions `FALLBACK` by name in that row, and the one sentence in the `AUTO` section that does mention `FALLBACK` ("`FALLBACK` is used only if the human is asked and the response is unavailable or insufficient") appears afterward, decoupled from the table, as a general clarifying remark about `AUTO` vs. `FALLBACK` being "different mechanisms" rather than as an explicit annotation on the table's uncertain-case row. A careful reader has to infer the connection rather than being told it directly at the point where it matters (the table).

**Two readings:**
- (A) The inference is correct and intended: "as for a `HITL` without `AUTO`" is a complete cross-reference, meaning every rule from the plain `HITL`/`FALLBACK` sections — including fallback-on-unusable-response — applies identically once `AUTO` defers to asking a human.
- (B) Because the `AUTO` section's own explicit discussion of `FALLBACK` is phrased only as a general distinction ("`AUTO` and `FALLBACK` are different mechanisms... `FALLBACK` applies only afterwards"), and not as part of the table's row description, a reader could take the table at face value as only specifying *that* a human is asked, leaving open (again, underspecified) exactly which downstream mechanics apply — e.g., whether an `AUTO`-triggered human ask still needs an explicit `→ FALLBACK` sub-block written under that same `HITL` in the source text, or whether `FALLBACK` behavior is somehow assumed even without one being written.

---

## Summary

The clearest structural tension running through most of these items is: `HITL`/`AUTO`/`FALLBACK` describe a decision-resolution mechanism whose *observable effect on control flow* is entirely mediated through `WHEN <name>.<answer>` conditions, yet the spec never pins down (a) the namespace/persistence rules for these outcomes as precisely as it does for `TRANSITION` state or `VERIFY`-in-`FORK` outcomes, (b) the vocabulary constraints on `AUTO`'s automatic answers versus human answers, or (c) what happens to control flow when a `FALLBACK` flow completes without an explicit `STOP`/`BREAK`. Separately, `AUTO`'s core criterion ("sufficiently determined," "protocol-compatible decision") and `FALLBACK`'s core criterion ("insufficient") are both defined only by non-exhaustive examples, which is likely deliberate (per the Semantic Principles' avoidance of prescribing an algorithm) but still means two reasonable implementers can diverge on identical scenarios without either being clearly wrong under the text as written.
