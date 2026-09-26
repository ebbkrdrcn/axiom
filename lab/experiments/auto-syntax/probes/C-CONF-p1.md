# Ambiguities and gaps in `DSL`, focused on HITL / AUTO / FALLBACK / WHEN

Method note: I used only the text of the specification. Where a question turns
on how two passages relate to each other, I quote both. Where the spec is
simply silent, I say so and give the two (or more) readings a careful
implementer could adopt, without picking one as "correct" — the spec does not
let me pick.

---

## 1. What counts as "the `WHEN` constructs that follow" when judging sufficiency

**Section:** `HITL`

> "`<name>` names the decision. The response establishes the outcome
> `<name>.<answer>`, where `<answer>` is one of the answers tested by the
> `WHEN <name>.<answer>` constructs that follow. A response that corresponds
> to none of these answers is insufficient (see `FALLBACK`)."

**Problem:** Whether a response is *sufficient* (and hence whether `FALLBACK`
fires) depends entirely on which `WHEN <name>.<answer>` constructs count as
"the constructs that follow." The spec never defines "follow" precisely —
not as a grammar production, not as a scope rule.

- **Reading A (adjacent/same-flow only):** "follow" means the `WHEN`
  statements placed immediately after the `HITL`, at the same indentation,
  in the same flow — exactly as every example in the spec shows (`HITL` then
  two `WHEN`s at the same level). A `WHEN merge.something` buried inside a
  distant `LOOP` or a different `FORK` branch would not count toward the
  answer set.
- **Reading B (anywhere later in the program):** "follow" means anywhere
  later in the program text, in any scope, since the spec's scope rules are
  about statement nesting, not about which identifiers are "in scope" for
  sufficiency-checking, and the sentence gives no textual-adjacency
  qualifier.

These readings diverge concretely: under Reading A, a `WHEN merge.deferred`
placed one page later inside an unrelated branch would not make "deferred"
an acceptable answer, so a human answering "deferred" would be *insufficient*
and trigger `FALLBACK`. Under Reading B it would be accepted and no
`FALLBACK` would fire. The DSL gives no way to tell which the author meant.

A related gap: when `<name>` is **omitted** (permitted "when no `WHEN` refers
to the decision"), there is by construction no `WHEN <name>.<answer>` to test
against at all. The spec's sufficiency test is defined only in terms of that
set. It never says what makes a response to an *unnamed* `HITL` sufficient —
literally any non-empty answer? Any answer that isn't itself an "insufficient"
example ("I haven't looked yet", off-topic, wrong question)? Both are
consistent with the rest of the text.

---

## 2. What happens after the `FALLBACK` flow finishes, if it doesn't `STOP`/`BREAK`

**Sections:** `HITL`, `FALLBACK`

> "The flow containing a `HITL` waits at the `HITL` until either a usable
> response is available or its `FALLBACK` flow is used... **With a usable
> response**, execution continues with the next statement after the `HITL`
> construct." (HITL)

> "Statements after the `HITL` construct, at the indentation of `HITL`, are
> the normal flow. They are not part of the fallback flow." (FALLBACK)

**Problem:** Continuation to "the next statement after the `HITL`
construct" is stated only for the *usable-response* case ("With a usable
response, execution continues..."). The spec never says what happens once a
`FALLBACK` flow itself reaches its own last statement, if that statement is
not `STOP` or `BREAK`. All the worked examples end their fallback in `STOP`,
so the general case is never actually shown.

- **Reading A (fall-through/rejoin):** By analogy with every other flow
  construct (`WHEN` flows, `FORK` branches), completing a flow's last
  statement just means falling through. So after `FALLBACK` completes,
  execution resumes at "the statement after the `HITL` construct" — the same
  place the usable-response path rejoins — except that no `<name>.<answer>`
  outcome was ever established, so any subsequent `WHEN <name>.<answer>`
  will simply not match (per the ordinary WHEN rule that an unmatched WHEN is
  not an error).
- **Reading B (fallback is a dead end unless it says otherwise):** Since
  "with a usable response" is explicitly the condition for resuming the
  normal flow, and no equivalent clause is written for the fallback case,
  a `FALLBACK` that doesn't itself `STOP`/`BREAK`/loop back leaves execution
  in an undefined state — the author is expected to always terminate,
  redirect ("defer, request another action"), or otherwise dispose of control
  explicitly inside the fallback, and a fallback that just "runs off the end"
  is simply not a well-formed way of writing a process, even though nothing
  in the syntax rules forbids it.

These two readings produce materially different runtime behavior for any
`FALLBACK` that ends in something other than `STOP`/`BREAK` (e.g. a
`FALLBACK` that only does `TRANSITION "Blocked"` and then ends) — one keeps
running the rest of the program, the other is undefined/stuck.

---

## 3. No `FALLBACK` attached at all: what happens on an unavailable/insufficient response?

**Section:** `FALLBACK`, `HITL`

> "The fallback flow is used only when the expected response cannot be used
> to continue the normal flow." (FALLBACK)

**Problem:** The HITL grammar makes `→ FALLBACK` optional:
`[ INDENT , [→AUTO NL] , [→FALLBACK NL INDENT flow DEDENT] , DEDENT ]`. So a
program may legally contain a named `HITL`, with `WHEN`s testing its answers,
and *no* `FALLBACK` clause. The spec defines what `FALLBACK` does when
present, but never says what happens when a response turns out to be
unavailable or insufficient and **no** `FALLBACK` exists to "use."

- **Reading A (indefinite suspension, like a timeout-less `WAIT`):** By
  analogy with `WAIT` ("If the event never becomes available, execution
  remains suspended") and with `REQUIRE` ("execution must not proceed as if
  the requirement were satisfied"), the safe default is that the flow simply
  stays suspended at the `HITL` forever if no `FALLBACK` is defined and the
  response is unusable — there is no way to proceed, and none is invented.
- **Reading B (not well-formed):** Since the whole point of naming a `HITL`
  and writing `WHEN`s against it is to guarantee the process can determine
  *some* subsequent branch, a named `HITL` with tested answers but no
  `FALLBACK` is an incomplete process description — the spec's rule that "a
  program that violates a rule stated as ... 'must not' ... is not
  well-formed" could be read as implicitly requiring a `FALLBACK` wherever an
  insufficient/unavailable response is possible, i.e. essentially always
  (since human responses can always be off-topic). Under this reading such a
  program should be rejected rather than executed with silent hanging.

The spec supports neither reading with a direct statement, and they lead to
opposite recommendations (run it and hang vs. reject the program).

---

## 4. Must `AUTO`'s automatically-resolved answer be one of the answers tested by the following `WHEN`s?

**Section:** `AUTO`

> "Automatic resolution is permitted only when the agent can determine a
> single **protocol-compatible** decision from the available information and
> applicable criteria." ... "The outcome `<name>.<answer>` is established
> exactly as if a human had given that answer."

**Problem:** "Protocol-compatible" is used nowhere else in the specification
and is never defined. Separately, the sufficiency rule quoted in Item 1
("`<answer>` is one of the answers tested by the `WHEN` constructs that
follow... a response that corresponds to none of these answers is
insufficient") is written in the general `HITL` prose, before `AUTO` is even
introduced, and talks about "the response" (which reads most naturally as
the *human's* response). It is never restated for the case where `AUTO`
supplies the answer instead of a human.

- **Reading A:** "Protocol-compatible" just *means* "one of the answers the
  surrounding `WHEN`s test for" — i.e. the same sufficiency constraint
  applies uniformly whether the answer comes from a human or from `AUTO`. An
  agent that is "sufficiently determined" but lands on an answer outside that
  set has, by definition, not made a protocol-compatible decision, and per
  the Execution table this counts as uncertain, so the human must be asked.
- **Reading B:** `AUTO`'s decision procedure is independent of what `WHEN`s
  happen to be written afterward — "protocol-compatible" refers to the
  process's own domain rules (e.g. "an approved dependency-upgrade protocol"),
  not to the DSL's `WHEN` syntax at all. Under this reading `AUTO` could
  resolve to an answer that no subsequent `WHEN` tests for, in which case the
  outcome is established (`<name>.<answer>`), no `WHEN` matches it, and
  execution "simply continues" with nothing having visibly happened — the
  automatic decision is silently inert rather than being treated as
  "uncertain."

These readings disagree on whether a poorly-matched `AUTO` outcome ever
reaches a human (Reading A: yes, it's treated as uncertain) or is silently
swallowed (Reading B: no human is ever consulted, and the branching the
author intended never fires).

---

## 5. `WHEN` referencing an outcome that was never established vs. one that resolved differently

**Sections:** `WHEN`, `HITL`

> "If the condition is not satisfied, the flow is skipped... An unmatched
> `WHEN` is not an error; it does not stop, wait, or escalate." (WHEN)

> "The name may be omitted when no `WHEN` refers to the decision." (HITL)

**Problem:** `WHEN`'s rule treats "condition not satisfied" as a single
uniform case. But for a `HITL`-produced condition, "not satisfied" could mean
at least three different things that the spec never distinguishes:
(a) the `HITL` was reached and resolved to a *different* named answer, (b)
the `HITL` that would establish this outcome was never reached at all in this
execution (e.g. it sits behind a different, unmatched `WHEN`, or inside an
unreached loop iteration), or (c) the identifier in the `WHEN` condition is
simply misspelled / refers to a `HITL` name that doesn't exist anywhere in
the program.

- **Reading A:** All three collapse to "not satisfied," full stop — the DSL
  has no notion of an undefined vs. false outcome, so a typo'd condition name
  is silently and permanently unsatisfied forever, exactly like a legitimate
  alternate answer. This is consistent with the literal wording ("if no
  `WHEN` matches... execution simply continues") but means the DSL has no way
  to catch a misnamed reference — it just looks like "that branch didn't
  happen to fire this time."
  - **Reading B:** A reference to a name that no `HITL`/`VERIFY` in the
  program could ever establish is a static well-formedness problem (akin to
  an undefined identifier), and should be rejected before execution, whereas
  "reached but resolved differently" and "not yet reached" are both
  legitimately just "not satisfied" at runtime. The spec's validity section
  ("A program that violates a rule stated as... 'must not'...") doesn't
  clearly extend this far, but nothing rules it out either.

---

## 6. Does re-invoking the same-named `HITL` overwrite its previously established outcome for `WHEN`s elsewhere?

**Sections:** `LOOP`, `TRANSITION`, `HITL`

> "The process has exactly one current state. Each `TRANSITION` replaces it,
> so the most recently executed `TRANSITION` determines the current state.
> Two `TRANSITION` statements executed in sequence are not a conflict: the
> second one wins." (TRANSITION)

**Problem:** This "most recent wins" rule is stated explicitly, but only for
`TRANSITION`/process state. No equivalent statement exists for outcomes
established by `HITL` (or `VERIFY`). Yet the `LOOP` example itself puts a
`VERIFY`/`WHEN` pair inside a loop body, implying that each iteration's
result is checked freshly — which only makes sense if each iteration's
outcome supersedes the last. Nothing says this is a general rule for named
outcomes, though, especially where the `WHEN` doing the checking sits outside
the loop, or the same `HITL` name is reused in two different places in the
program.

- **Reading A:** Like `TRANSITION`, an outcome is a single named value that
  the most recent establishment overwrites; any `WHEN <name>.<answer>`
  anywhere in the program, evaluated after that point in execution order,
  sees the latest value. A `HITL:merge(...)` asked twice (e.g. once per loop
  iteration) simply has its answer replaced each time.
- **Reading B:** Outcomes are scoped to the flow/invocation that produced
  them (closer to a local result of that specific `HITL`/`VERIFY` statement),
  and a `WHEN` elsewhere referring to the same name after a second invocation
  is really referring to a different, unrelated occurrence of that name —
  the spec's `FORK`/`JOIN` note ("Outcomes established inside the branches
  remain available to `WHEN` constructs after the `JOIN`") suggests outcomes
  are tied to *where* they were produced rather than being globally-scoped
  mutable state, which cuts against treating every `<name>.<answer>` as one
  global slot like `TRANSITION`'s single current state.

---

## 7. Does a fall-through `FALLBACK` (see Item 2) undermine the "must not be silently replaced" guarantee?

**Section:** `HITL`

> "`HITL` must not be silently replaced by an agent decision unless that
> `HITL` is explicitly marked with `AUTO`."

**Problem:** This sentence guarantees that *some* explicit human or `AUTO`
decision always determines what "having asked" means. But combine it with
Item 2's open question: if `FALLBACK` completes without `STOP`/`BREAK` and
(under Reading A of Item 2) execution simply falls through to the normal flow
after the `HITL`, then any `WHEN <name>.<answer>` there will find no outcome
established and silently skip — meaning the process moves forward past what
was meant to be a decision gate, without any decision (human, `AUTO`, or
otherwise) ever having been recorded. No agent "replaced" the human, but no
decision was made either, and the DSL text never flags this as a special
case distinct from an ordinary "declined" answer.

- **Reading A:** This is fine and intended — `FALLBACK` is precisely the
  author's tool for defining what "no decision" means for their process (its
  own text: "may explicitly terminate, defer, request another action, or
  otherwise handle the unresolved situation"), so falling through to
  unmatched `WHEN`s is just one more legitimate way of "otherwise handling"
  it, functionally equivalent to a silent "none of the above."
- **Reading B:** This is a gap in the guarantee — the "human decision
  boundary" language implies every path forward past a `HITL` corresponds to
  an actual decision (human-made or `AUTO`-made). A path forward that
  corresponds to *no* decision at all (response was unusable, fallback ran,
  fell through) is a third, undocumented category that the `WHEN`-matching
  machinery cannot distinguish from "the human said no," which could hide
  the fact that the decision boundary was never actually crossed.

---

## 8. `WHEN` reading a `HITL`/`AUTO` outcome from a still-running (unjoined) `FORK` branch

**Sections:** `WHEN`, `FORK`, `JOIN`

> "A `WHEN` is evaluated once, when execution reaches it in declaration
> order. It is not a standing trigger and does not wait for its condition to
> become true." (WHEN)

> "Outcomes established inside the branches remain available to `WHEN`
> constructs after the `JOIN`." (JOIN)

**Problem:** The `JOIN` section only promises outcome-visibility *after* a
`JOIN`. Nothing says what a `WHEN` sees if it evaluates a condition tied to a
`HITL`/`AUTO` decision inside a sibling `FORK` branch that hasn't completed
yet (e.g. a `WHEN` in a branch that finishes quickly, or in code that runs
after the `FORK` without a `JOIN`, per "If no `JOIN` follows the `FORK`,
execution continues immediately... while the branches keep running"). Since
`WHEN` explicitly "does not wait," it must do *something* when the outcome
isn't there yet.

- **Reading A:** It reads the outcome as simply unestablished/not-satisfied
  (same as Item 5's "not yet reached" case) — the `WHEN` evaluates
  immediately against whatever has been established so far, races included,
  and a `HITL` still pending in another branch just means that condition is
  false for this evaluation, permanently (since `WHEN` is "evaluated once").
- **Reading B:** Since `HITL` and `AUTO` are decision boundaries whose whole
  purpose is to gate subsequent flow, a `WHEN` that depends on one implicitly
  requires that decision to have already been made in program order — i.e.
  the author is expected never to write a `WHEN` that reads a `FORK`
  branch's not-yet-joined outcome, and a program that does so is relying on
  an unspecified race rather than exercising a normal, supported feature.

---

## Summary of what the spec leaves genuinely open

The clearest, highest-impact gaps for HITL/AUTO/FALLBACK × WHEN are:

1. The scope of "the `WHEN` constructs that follow" for judging sufficiency (Item 1).
2. What happens when a `FALLBACK` flow ends without `STOP`/`BREAK` (Item 2), which in turn drives Item 7's question about whether the "decision boundary" guarantee can be silently bypassed.
3. What happens when there is no `FALLBACK` at all (Item 3).
4. Whether `AUTO`'s answer is constrained to the `WHEN`-tested set ("protocol-compatible" is undefined) (Item 4).
5. Whether "not satisfied" in `WHEN` conflates "resolved differently," "not yet reached," and "undefined identifier" (Item 5).
6. Whether outcomes are overwritten on re-establishment the way process state is under `TRANSITION` (Item 6).
7. Cross-branch visibility of outcomes before a `JOIN` (Item 8).

None of these is resolved by the text as given; each admits at least two
materially different, reasonable implementations.
