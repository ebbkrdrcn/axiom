# Ambiguities and gaps in the go_harness DSL — focus on HITL, AUTO, FALLBACK, and WHEN

Scope and method: this analysis uses only the text of the specification supplied
in `A-CONF.md`. It focuses on `HITL`, `AUTO`, `FALLBACK`, and their interaction
with `WHEN`, as instructed, and does not attempt to resolve any of the questions
raised — each is presented as genuinely open under the spec as written, with two
readings a competent implementer could each defend from the text.

---

## 1. Which `WHEN` constructs count as "the constructs that follow" a `HITL`?

**Section:** `### HITL`

> `<name>` names the decision. The response establishes the outcome
> `<name>.<answer>`, where `<answer>` is one of the answers tested by the
> `WHEN <name>.<answer>` constructs that follow. A response that corresponds to
> none of these answers is insufficient (see `FALLBACK`).

**Problem:** The set of "valid answers" for a given decision — which determines
whether a human response is *sufficient* or must go to `FALLBACK` — is defined
by "the `WHEN <name>.<answer>` constructs that follow." Nothing in the Syntax,
Scope, or Grammar sections formally binds a `HITL` to any particular set of
`WHEN` statements. Unlike `FALLBACK`, which the grammar attaches directly to
`hitl` (`[INDENT, "→", "FALLBACK", ...]`), there is no grammatical link between
a `hitl` node and any `when` node at all. "Follow" is only prose.

**Two readings:**
- **Reader A (textual/program-wide):** "follow" means anywhere later in the
  program text that uses `WHEN <name>.<answer>`, regardless of whether that
  `WHEN` is reachable from this particular `HITL` (e.g., it could sit inside a
  different `FORK` branch, a different `LOOP`, or after the enclosing scope of
  the `HITL` has already exited). The valid-answer set is computed by scanning
  the whole program for that name.
- **Reader B (flow-local/adjacent):** "follow" means only the statements
  actually reached next in the same flow after the `HITL` — in practice, the
  `WHEN` statements written as immediate siblings at the same indentation as
  the `HITL`, as in every example given. A `WHEN name.answer` elsewhere in the
  program, even if textually later, is irrelevant to what counts as a usable
  answer for this particular `HITL`.

These readings diverge concretely whenever a `HITL` is reused, is inside a
`LOOP`/`FORK`, or coexists with unrelated `WHEN` constructs on the same name.

---

## 2. What "insufficient" means — a named-answer definition vs. a semantic one

**Sections:** `### HITL` and `### FALLBACK`

> `### HITL`: "A response that corresponds to none of these answers is
> insufficient (see `FALLBACK`)."
>
> `### FALLBACK`: "**Insufficient** means a response arrives but does not
> provide the requested decision or input. Examples are 'I haven't looked
> yet', an off-topic reply, or an answer to a different question."

**Problem:** Two different tests for "insufficient" are given. The `HITL`
section defines it *syntactically*, against the closed set of answers tested by
downstream `WHEN` constructs (see item 1). The `FALLBACK` section defines it
*semantically*, as a judgment about whether the reply "provides the requested
decision" at all, independent of any named answer set. These are not obviously
the same test, and the spec never states which governs when they disagree.

**Two readings:**
- **Reader A:** The `FALLBACK` definition is general prose *explaining* the
  `HITL` rule; in practice "insufficient" always reduces to "does not match one
  of the answers tested by the following `WHEN`s." A reply that happens to
  contain the right keyword but is otherwise semantically nonsensical would
  still count as sufficient, because the test is purely syntactic matching.
- **Reader B:** The `FALLBACK` definition is the real (semantic) test, and the
  `HITL` sentence is just the common case for named decisions. Under this
  reading, a response could syntactically match one of the tested answers yet
  still be judged "insufficient" if it doesn't actually address the question
  (e.g., a canned or off-topic reply that happens to contain the token
  "approved"), or conversely a response could be judged "sufficient" in a
  semantic sense while not mapping to any `<name>.<answer>` the `WHEN`s test —
  leaving no `WHEN` to catch it and no defined behavior for that case.

---

## 3. `FALLBACK` on an unnamed `HITL`: against what is "insufficient" measured?

**Sections:** `### HITL`, `### FALLBACK`, `## Syntax`

> `### HITL`: "The name may be omitted when no `WHEN` refers to the decision."
>
> `## Syntax`: `[AUTO] HITL[:<name>]("<message>")` — the name is optional
> independent of whether `FALLBACK` is attached.

**Problem:** The grammar permits `FALLBACK` on a `HITL` with no `<name>` at
all. But the only definition of "insufficient" tied to a formal test (item 1)
depends on `<name>.<answer>` and the `WHEN`s that test it — which cannot exist
for an unnamed decision by definition (no `WHEN` refers to it). So for an
unnamed `HITL` with a `FALLBACK`, the spec gives no formal criterion for when a
response is "insufficient"; only the informal `FALLBACK`-section examples
("I haven't looked yet," off-topic, wrong question) remain available.

**Two readings:**
- **Reader A:** For an unnamed `HITL`, sufficiency can only be about
  *availability* (a response arrived at all); once any response arrives, it is
  automatically sufficient, since there is no answer set to fail to match. The
  `FALLBACK` branch on an unnamed `HITL` is effectively reachable only through
  "unavailable," never through "insufficient."
- **Reader B:** The generic semantic definition in `FALLBACK` (does the reply
  "provide the requested decision or input") applies regardless of naming, so
  an unnamed `HITL`'s `FALLBACK` can still be triggered by an off-topic or
  non-answer reply, using human judgment rather than any formal answer set.

---

## 4. What happens after a `FALLBACK` flow completes without `STOP`/`BREAK`?

**Sections:** `### HITL`, `### FALLBACK`

> `### HITL`: "The flow containing a `HITL` waits at the `HITL` until either a
> usable response is available or its `FALLBACK` flow is used... With a usable
> response, execution continues with the next statement after the `HITL`
> construct."
>
> `### FALLBACK`: "`FALLBACK` is associated with response handling. It does
> not mean 'execute this flow after the normal flow.'" ... "Statements after
> the `HITL` construct, at the indentation of `HITL`, are the normal flow.
> They are not part of the fallback flow."

**Problem:** The spec states explicitly what happens after a *usable response*
(continue with the statement after the `HITL` construct), and states
explicitly that the fallback flow is *not* run "after" the normal flow (i.e.,
the two are mutually exclusive, not additive). But it never states what
happens once the fallback flow itself finishes, if that flow contains no
`STOP` or `BREAK` (every worked example in the spec ends its fallback with
`STOP`). General flow rules ("a statement starts only after the previous
statement in the same flow has completed") would suggest execution falls
through to "the statement after the `HITL` construct" once the whole `hitl`
node — including its optional attached `FALLBACK` — has completed, by analogy
with how a `WHEN` flow's completion falls through to the statement after the
`WHEN`. But this is never stated for `HITL`/`FALLBACK`, and the sentence "it
does not mean 'execute this flow after the normal flow'" can be read as
actively ruling that out.

**Two readings:**
- **Reader A (falls through by analogy with `WHEN`):** Once the `FALLBACK`
  flow finishes (with no explicit terminator), execution continues with the
  statement after the `HITL` construct, exactly as it would after a `WHEN`
  flow completes. Any `WHEN <name>.<answer>` immediately following will
  simply fail to match (no outcome was established), and execution "simply
  continues" past them, per the general `WHEN` rule that an unmatched `WHEN`
  is not an error.
- **Reader B (fallback is terminal for that construct unless it says
  otherwise):** The explicit statement that fallback "does not mean execute
  this flow after the normal flow" signals that fallback and normal-flow
  continuation are alternatives that do not both eventually rejoin; a
  `FALLBACK` flow that doesn't itself decide to continue (via some statement
  that logically returns to the main line) leaves the process's next step
  underspecified/stalled at the design level — an author is expected to make
  the fallback flow self-contained (e.g., end in `STOP`, `BREAK`, or a
  `TRANSITION` that fully handles the situation), and relying on fallthrough
  into subsequent `WHEN`s is not something the spec sanctions.

---

## 5. `AUTO`'s "single protocol-compatible decision" — what is "the protocol"?

**Section:** `### AUTO`

> "Automatic resolution is permitted only when the agent can determine a
> single protocol-compatible decision from the available information and
> applicable criteria."

**Problem:** "Protocol" is used here once and nowhere else in the
specification, and is never defined. It is unclear whether it refers to
something internal to the DSL or to something external to it.

**Two readings:**
- **Reader A:** "Protocol" refers to the DSL's own decision protocol for that
  `HITL` — i.e., the closed set of `<name>.<answer>` values recognized by the
  `WHEN` constructs that follow it (see item 1). A "protocol-compatible
  decision" is simply one of those recognized answers, and "single" means the
  evidence points unambiguously to exactly one of them.
- **Reader B:** "Protocol" refers to an external governing procedure (a
  business, compliance, or approval protocol supplied by "the surrounding
  process") that is not represented anywhere in the DSL's syntax — the DSL
  gives no way to state what that protocol is, so this reading makes
  "protocol-compatible" an entirely extra-linguistic requirement the runtime
  must somehow know about.

These readings matter because they change what evidence would make an `AUTO`
resolution valid: Reader A ties it to answer-syntax; Reader B ties it to
unwritten domain rules.

---

## 6. `AUTO`'s "applicable criteria" and certainty threshold are undefined

**Section:** `### AUTO`

> "Automatic resolution is permitted only when the agent can determine a
> single protocol-compatible decision from the available information and
> applicable criteria." ... "A confidence score alone does not establish
> certainty." ... "The DSL runtime determines uncertainty as part of automatic
> decision resolution."

**Problem:** The spec deliberately declines to define what the "applicable
criteria" are, how they are expressed, or what test distinguishes "sufficiently
determined" from "uncertain" beyond ruling out a bare confidence score. This is
consistent with the DSL's stated principle of implementation-independence, but
it means the single most consequential branch point around `HITL` — whether a
human is asked at all — has no operational definition in the spec itself.

**Two readings:**
- **Reader A:** This is intentionally left to "the surrounding process" (i.e.,
  criteria are defined outside the DSL, e.g. in accompanying documentation or
  policy that the agent is told to consult), and the DSL's silence here is a
  feature, not a gap — analogous to `VERIFY`'s undefined "applicable
  acceptance criteria."
- **Reader B:** Because no criteria, format, or threshold is given anywhere,
  and because the spec explicitly disqualifies the one concrete signal it
  mentions (confidence score), an agent following the spec literally can never
  be *certain* it is entitled to use `AUTO`, and a maximally conservative
  reading would treat every `AUTO HITL` as requiring a human in practice
  unless criteria happen to be pinned down elsewhere — which would make `AUTO`
  largely inoperative on the spec's text alone.

---

## 7. Lifetime, scope, and namespace of an "outcome" (including HITL/AUTO answers)

**Sections:** `### HITL`, `### JOIN`, `### TRANSITION`, `### VERIFY`

> `### JOIN`: "Outcomes established inside the branches remain available to
> `WHEN` constructs after the `JOIN`."
>
> `### TRANSITION`: "The process has exactly one current state. Each
> `TRANSITION` replaces it... the most recently executed `TRANSITION`
> determines the current state."
>
> `### HITL`: "The response establishes the outcome `<name>.<answer>`..."

**Problem:** `TRANSITION` is explicitly given a replace-and-single-current-value
semantics. No equivalent rule is given for outcomes established by `HITL`,
`AUTO`, or `VERIFY`. It is therefore unclear (a) how long an established
`<name>.<answer>` outcome remains available to later `WHEN` checks, (b)
whether re-executing the same named `HITL` (e.g., on a later `LOOP` iteration,
or at a second, textually distinct `HITL:<name>` elsewhere in the program)
overwrites the previous outcome the way `TRANSITION` overwrites state, and (c)
whether `HITL`, `AUTO`, and `VERIFY` outcomes all share one flat
`<identifier>.<identifier>` namespace such that two different constructs
targeting the same pair (e.g., an `implementation.accepted` from both a
`VERIFY` and an unrelated `HITL:implementation`) could collide.

**Two readings:**
- **Reader A:** Outcomes behave like `TRANSITION`'s state — a single
  process-wide, always-current value per name, where each new establishment
  (whether via `HITL`, `AUTO`, or `VERIFY`) replaces any prior value under
  that name, and a `WHEN` checked later always sees only the most recent one.
- **Reader B:** Outcomes are scoped to the flow/iteration that produced them
  (analogous to how `BREAK` and completion are scoped to "the current" loop
  or branch) and are only guaranteed available to `WHEN`s within that same
  execution episode; a re-entrant `HITL` on a second `LOOP` pass starts fresh,
  and an outcome from one branch or iteration is not guaranteed to still be
  "the" value seen by an unrelated `WHEN` elsewhere, since the spec's one
  explicit persistence guarantee ("remain available... after the `JOIN`") is
  scoped narrowly to the `FORK`/`JOIN` case and is not stated as a general
  rule.

---

## 8. Multiple `WHEN`s matching the same `HITL` answer, or the same name used at more than one `HITL`

**Sections:** `### WHEN`, `### HITL`

> `### WHEN`: "Each `WHEN` is independent. There is no implicit 'else' and no
> 'first match wins'... every one whose condition is satisfied executes its
> flow."
>
> `### HITL`: "`<name>` names the decision."

**Problem:** Because `WHEN` evaluation is defined generically (every matching
`WHEN` fires, independent of others), and `HITL` naming is defined generically
("names the decision," with no stated uniqueness constraint across the
program), two situations are left open: (a) if two separate `WHEN
merge.approved` constructs exist after one `HITL:merge`, do both flows really
run for a single human answer, and is that intended for a decision boundary
(as opposed to, say, verification outcomes where fan-out to multiple flows is
more obviously benign)? and (b) if `HITL:merge(...)` appears twice at two
different points in the program (e.g., once per `LOOP` iteration, or in two
unrelated places), do they represent one recurring decision sharing one
outcome slot, or two independent decisions that happen to share a label?

**Two readings:**
- **Reader A:** `HITL` names are global identifiers for one decision; every
  occurrence of `HITL:merge` refers to the *same* decision, its outcome is
  reused/overwritten each time it's asked, and the general "every matching
  `WHEN` fires" rule applies to it exactly as to any other outcome, including
  duplicate `WHEN`s firing in sequence for the one answer.
- **Reader B:** A `HITL:<name>` is local to its point in the program (its
  outcome exists only for the `WHEN`s that "follow" that specific occurrence,
  per item 1); reusing the same `<name>` at a different `HITL` elsewhere is
  simply a different, independent decision that happens to share a label, and
  nothing in the spec prevents or flags this as a naming collision — making it
  the author's problem to avoid, not something the DSL's semantics resolve.

---

## Summary of underspecified/ambiguous points

1. Which `WHEN <name>.<answer>` constructs are the ones "that follow" a given
   `HITL` (program-text order vs. reachable-flow order; sibling requirement).
2. Whether "insufficient" is a syntactic test (against the `WHEN`-tested answer
   set) or a semantic one (does the reply address the question) when the two
   disagree.
3. What "insufficient" even means for an unnamed `HITL`, which has no answer
   set to fail to match.
4. What happens after a `FALLBACK` flow completes without `STOP`/`BREAK` —
   fallthrough to the statement after `HITL`, or an undefined/terminal state.
5. What "protocol" means in `AUTO`'s "single protocol-compatible decision."
6. What the "applicable criteria" and certainty threshold for `AUTO` actually
   are, beyond "not a confidence score alone."
7. The lifetime, scope, and shared-namespace behavior of outcomes established
   by `HITL`/`AUTO` (and by extension `VERIFY`), which — unlike `TRANSITION`'s
   explicit single-current-value rule — is never stated.
8. Whether a `HITL` name is a single global decision slot or a fresh, local
   one at each occurrence, and what follows from `WHEN`'s "every match fires"
   rule when multiple `WHEN`s target the same named answer.

No assumption was required to *complete* this task beyond identifying these
gaps; where the specification does not determine an answer, that
indeterminacy is itself the finding, and is presented above as such rather
than resolved.
