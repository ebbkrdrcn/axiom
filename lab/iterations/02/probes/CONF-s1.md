# Ambiguities, Contradictions, and Underspecified Points in the DSL Spec

Method note: this list uses only the text of the specification given. No item below required an outside assumption to *identify*; where I describe how a reader/implementer would have to fill a gap, that is the assumption they would be forced to invent, not one I am importing from elsewhere. Items are ordered from most to least likely to cause a wrong process or a wrong execution.

---

## 1. Direct contradiction: is `BREAK` ever valid inside a `FORK` branch?

- **Sections:** `FORK`, `BREAK`, and Validity rule V3.
- **Quotes:**
  - FORK's table: "`BREAK` in a branch | INVALID (rule V3). To leave a loop based on a branch's result, `JOIN` first, then use `WHEN … → BREAK`."
  - BREAK section: "INVALID outside a `LOOP` (V2), and INVALID inside a `FORK` branch **unless the `LOOP` it leaves is also inside that branch** (V3)."
  - V3 itself: "`BREAK` is inside a `FORK` branch, and the `LOOP` it would leave is **outside** that branch."
- **Problem:** The FORK table states, unconditionally, that any `BREAK` inside a branch is invalid. The BREAK section and V3 both state a conditional rule: `BREAK` in a branch is invalid *only* when the loop it would leave is outside that branch — implying it is valid when a `LOOP` is nested entirely inside the same branch and the `BREAK` leaves that inner loop. These cannot both be true.
- **Two readings:**
  - Reader A takes the FORK table literally and concludes a program like `FORK → LOOP:x ... WHEN c → BREAK` (loop and break both inside one branch) is INVALID, full stop.
  - Reader B follows BREAK/V3's explicit exception and concludes the same program is VALID, since the loop `BREAK` exits is inside the branch. A validator built from the table will reject programs a validator built from V3 would accept.

---

## 2. Is testing an outcome from an un-joined `FORK` invalid forever, or only while a race is actually possible?

- **Sections:** `JOIN`, `FORK`, `Outcomes` (Visibility), Validity rule V10.
- **Quotes:**
  - FORK: "No `JOIN` follows → Execution continues immediately after the `FORK` while the branches run." (so omitting `JOIN` is explicitly legal)
  - V10: "a `WHEN` tests a subject that a branch of a `FORK` in the same flow establishes, and that `FORK` has not been joined before the `WHEN`" → INVALID.
  - Outcomes/Visibility: "A `WHEN` **MUST NOT test an outcome that a still-running branch may establish**; `JOIN` first (rule V10)."
- **Problem:** If a `FORK` legitimately has no `JOIN` at all, then "that `FORK` has not been joined" is permanently true for the rest of the program — under a literal, static reading of V10, *no* `WHEN` anywhere later in the program may ever test an outcome established inside one of its branches, even long after every branch is certainly finished. But the Outcomes section justifies the same rule with "may establish" — a possibility/timing argument — which suggests the rule is only about genuine races, not a permanent textual ban. The spec gives no way to prove "surely finished" other than `JOIN`, so it's unclear which reading is intended. A concrete edge case sharpens this: a `LOOP` body reading `WHEN result.x ... FORK ... JOIN` in that order — a `WHEN` at the *top* of the body (checking the previous iteration's already-joined outcome) is textually "before" the `FORK`/`JOIN` pair that appears later in that same body. Does "before the `WHEN`" mean lexical position within one pass of the text (making this invalid, since no `JOIN` token precedes it in the body) or execution-time order across loop iterations (making it valid, since the prior iteration's `JOIN` already ran)?
- **Two readings:**
  - Static/structural: V10 is checked purely on program text — a `FORK` "has not been joined before the `WHEN`" whenever there is no `JOIN` statement earlier in the written flow, regardless of loop wraparound or actual timing. This forbids the loop example above and permanently forbids testing outcomes of any un-joined `FORK`.
  - Dynamic/possibility-based: V10 only fires when the branch could *actually* still be running when the `WHEN` is reached. Under this reading the loop example is fine (the relevant `FORK`'s prior iteration was already joined), and a `FORK` without a `JOIN` could still be safely tested later once nothing else in the program is racing it — but the spec supplies no mechanism to decide "nothing else is racing it."

---

## 3. No criterion for when `REQUIRE`/`HITL` give up waiting vs. keep waiting

- **Sections:** `REQUIRE`, `WAIT`, `HITL` (Usable/insufficient/unavailable table).
- **Quotes:**
  - REQUIRE: "The item is not yet available | Wait at the `REQUIRE`." vs. "The runtime determines the item cannot be obtained, and there is a `FALLBACK` | Run the fallback flow."
  - WAIT (for contrast): "There is no timeout. If the event never comes, execution stays at the `WAIT`."
  - HITL: "No response, and the runtime has stopped waiting" = unavailable.
- **Problem:** `WAIT` explicitly has no timeout and no give-up condition. `REQUIRE` and `HITL`, by contrast, both have a "give up" branch ("cannot be obtained" / "the runtime has stopped waiting"), but the spec never states what causes the runtime to reach that determination — no timeout, no retry count, no explicit signal is named. This is the single most consequential gap for execution behavior: it decides whether a program suspends indefinitely, runs its `FALLBACK`, or ends like `STOP`.
- **Two readings:**
  - Reader A treats "cannot be obtained" / "stopped waiting" as an external, opaque runtime signal that simply never fires unless the runtime explicitly says so — making `REQUIRE`/`HITL` behave like `WAIT` (wait forever) in the absence of an explicit "give up" event, so `FALLBACK` code is effectively dead unless the runtime is instrumented to emit it.
  - Reader B treats the agent itself as responsible for deciding, using some unstated heuristic (e.g., a single unanswered prompt, or the absence of the item at "the current moment"), which would make `FALLBACK` trigger essentially immediately whenever the item isn't already on hand — a much more aggressive interpretation with a very different resulting trace.

---

## 4. No operational test for "usable" vs. "insufficient" `HITL` responses

- **Section:** `HITL` — Usable, insufficient, unavailable table.
- **Quote:** "Clearly selects exactly one listed answer (in any wording)" = usable; "Selects none of the listed answers, is ambiguous between answers, or is off-topic ... " = insufficient.
- **Problem:** "Clearly," "ambiguous," and "off-topic" are judgment calls with no criteria (confidence threshold, keyword rule, etc.) given, and the spec elsewhere is emphatic that "a confidence score alone, however high, does not establish certainty" (stated for `AUTO`, but the same subjectivity applies to classifying a human's answer). Since every `HITL` in every program depends on this classification, two compliant agents can produce different traces from the identical human message.
- **Two readings:**
  - Given the answer list `[approved, declined]` and the reply "sounds good to me," Reader A calls this a clear, if informal, selection of `approved` (usable).
  - Reader B calls it off-topic/ambiguous (it doesn't literally name either listed answer, and "sounds good" could describe agreement with a plan rather than a formal approval) and treats it as insufficient, routing to `FALLBACK` or ending execution instead of continuing.

---

## 5. `AUTO`'s "certainty" and "authority" are undefined, and "authority" is folded into "uncertainty" inconsistently with the decision table

- **Section:** `AUTO`.
- **Quotes:**
  - Decision table: "The decision is certain **and** within the agent's authority | The agent establishes ... The human is not asked." (two separate, conjunctive conditions)
  - Bullet list of when "uncertainty exists": "... the agent does not have the authority required to make the decision." (authority is listed as *one example of* uncertainty)
- **Problem:** The table treats "certain" and "has authority" as two independent gates. The bulleted examples instead present lack-of-authority as a species of "uncertainty," even though an agent could be completely certain of the correct answer and simply be barred from acting on it — that is not epistemic uncertainty at all. Beyond this internal inconsistency, the spec never defines what "authority" means (there is no notion of roles, permissions, or scope anywhere else in the document), nor any procedure for judging "certain."
- **Two readings:**
  - Reader A keeps the two gates separate: first ask "am I certain," then, only if yes, separately ask "am I allowed to act here" — a lack of authority is a distinct veto, not a form of doubt.
  - Reader B follows the bulleted prose and treats an authority shortfall as just another instance of "uncertainty," meaning any argument for why the agent might not be certain (including an authority argument) is evaluated by the same single test, with no separate authority check at all.

---

## 6. `DELEGATE`'s "actor" is undefined and overlaps with `HITL("<request>")`

- **Sections:** `DELEGATE`, `HITL`.
- **Quotes:**
  - DELEGATE: "Assigns work to an actor. ... The statement is done when the actor has delivered its result."
  - HITL: "A request (the human provides input or performs an action; no outcome)."
- **Problem:** The spec never says what an "actor" is — human, sub-agent, or external system are all consistent with the wording. This creates a real overlap with `HITL("<request>")`, which is also "a human ... performs an action." For a requirement like "have a person write the release notes," nothing in the spec says whether that should be written as `DELEGATE release-notes` (actor = a person) or `HITL("Write the release notes")`.
- **Two readings:**
  - Author A writes `DELEGATE release-notes`, reasoning that DELEGATE is the general-purpose "assign work" construct and a human is a valid actor.
  - Author B writes `HITL("Write the release notes")`, reasoning that any work a human does is, by definition, a human-interaction boundary and must go through `HITL`. The two programs behave differently: DELEGATE establishes no human-interaction boundary and its result can be `VERIFY`'d for `accepted`/`rejected`; a bare `HITL("...")` establishes no outcome at all and cannot be `VERIFY`'d or tested by `WHEN`.

---

## 7. `JOIN`'s "nearest preceding `FORK` ... in the same flow" doesn't clearly cover branches or nested `FORK`s

- **Sections:** `JOIN`, `The arrow →` table, `FORK`.
- **Quotes:**
  - JOIN: "The corresponding `FORK` is the nearest preceding `FORK` in the **same flow**, at the same indentation, that has no `JOIN` yet."
  - Arrow table: `WHEN`/`FALLBACK` items are "the next step of one sequential flow"; `FORK` items are "a separate concurrent branch" — the spec consistently reserves the word "flow" for the sequential (WHEN/FALLBACK) case and uses "branch" for FORK's concurrent case.
- **Problem:** Having defined "flow" specifically as the WHEN/FALLBACK sequential construct, the JOIN rule then uses "the same flow" to describe where a `JOIN` looks for its `FORK` — but a `JOIN` can legally sit inside a `FORK` branch (e.g., to join a nested inner `FORK`), inside a `LOOP` body, or inside a `WHEN`'s flow. It's unclear whether "flow" in the JOIN rule is being used precisely (so a `JOIN` inside a branch, which is not a "flow" by the spec's own definition, could never find "its" `FORK`) or loosely to mean "whatever sequential context this `JOIN` sits in."
- **Two readings:**
  - Reader A takes "flow" literally: a `JOIN` written inside a `FORK` branch is not in a "flow" at all (it's in a "branch"), so a nested `FORK`/`JOIN` pair fully contained in one branch is either invalid or has to be matched by some unstated exception.
  - Reader B takes "flow" loosely as "the current sequential thread of control, whatever kind of block it's in," so a `JOIN` nested inside a branch matches the nearest un-joined `FORK` in that branch normally, letting `FORK`s nest inside branches freely.

---

## 8. Does "a `→` item is under ... `WHEN`, `FORK` or `FALLBACK`" (V4) mean the *immediate* parent, or any ancestor?

- **Sections:** Indentation and scope (rule 4), Validity rule V4.
- **Quotes:**
  - Rule 4: "any `→` item (lines that continue that item's flow or branch). If the statement after `→` is itself a `LOOP`, `WHEN`, `FORK`, `HITL` or `REQUIRE`, the lines nested under it are that statement's own children."
  - V4: "a `→` item is under anything other than `WHEN`, `FORK` or `FALLBACK`" → INVALID.
- **Problem:** Rule 4 says that lines nested under a plain `→` item (whose statement is, say, `DELEGATE`) "continue that item's flow or branch" — implying they should be un-arrowed continuation statements, as in the worked FORK example (`→ DELEGATE unit-tests` / `VERIFY unit-tests`, with no arrow on the second line). But if a line nested under such a `→ DELEGATE` item *does* itself begin with `→`, V4's wording ("under anything other than WHEN, FORK or FALLBACK") is ambiguous about whether "under" means the immediate syntactic parent (in which case this is invalid, since the immediate parent is a `→` item, not a `WHEN`/`FORK`/`FALLBACK`) or any enclosing ancestor (in which case it could be read as valid, since some `WHEN`/`FORK`/`FALLBACK` sits further up the chain).
- **Two readings:**
  - Reader A: "under" means the nearest enclosing line per the indentation rule (rule 2's "nearest preceding line indented less"). A `→`-prefixed line whose nearest parent is itself a plain `→` item is always INVALID, regardless of what encloses that item further up.
  - Reader B: "under" means "nested anywhere inside," so as long as a `WHEN`/`FORK`/`FALLBACK` appears somewhere in the ancestor chain, an arrow nested several levels deep under another arrow's continuation is acceptable.

---

## 9. What is the process's state before the first `TRANSITION`?

- **Section:** `TRANSITION`.
- **Quote:** "The process has exactly one current state. Each `TRANSITION` replaces it; the most recently executed one wins."
- **Problem:** This describes how the state changes but never says what the state is before any `TRANSITION` has executed (many valid programs, including the spec's own `LOOP:build` example, never call `TRANSITION` before doing other work). If asked to report "current state" or produce a trace at that point, the answer is undefined.
- **Two readings:**
  - Reader A says the state is simply undefined/absent until the first `TRANSITION`, and any report of "current state" before that point must say "none."
  - Reader B assumes there must be some default starting state (e.g., an implicit "Start" or empty string `""`) that a trace can always report, since the spec says the process "has exactly one current state" at all times (present tense, no exception carved out for before the first `TRANSITION`).

---

## 10. "Consecutive `WHEN`s are independent" — does independence require adjacency?

- **Sections:** Quick reference (`WHEN` row), Execution rule 3, `WHEN` section table.
- **Quotes:**
  - Execution rule 3: "**Consecutive** `WHEN`s are independent. Every one that is true runs, top to bottom."
  - WHEN section: "Several `WHEN`s in a row | Each one is checked independently, top to bottom."
- **Problem:** Both statements of the independence rule are scoped with "consecutive" / "in a row," but execution rule 2 (checked once, when reached; true → run, then continue; false → skip) already applies generally to any single `WHEN`, with no adjacency requirement. Because the "independent, every true one runs" language is only ever stated for the adjacent case, a reader could wonder whether two `WHEN`s on the same subject that are *not* adjacent (separated by other statements) are meant to behave differently — e.g., as mutually exclusive, or as if the second re-checks something about the first.
- **Two readings:**
  - Reader A treats "consecutive" as purely descriptive of the example given and applies the same independent, no-first-match, no-else semantics to any two `WHEN`s on any subject anywhere in the program, adjacent or not (which is consistent with rule 2 read alone).
  - Reader B takes the repeated, deliberate use of "consecutive"/"in a row" as meaningful, and infers that the guarantee of independence (as opposed to some other, unstated relationship) is only explicitly given for adjacent `WHEN`s, leaving non-adjacent same-subject `WHEN`s' interaction formally unaddressed.

---

## 11. A trace cannot show whether a `HITL:x` outcome came from `AUTO` or from the human

- **Sections:** Executing a program (trace effects), `AUTO`.
- **Quotes:**
  - Allowed effect: `outcome <subject>.<outcome>` — used identically in the worked trace both for a human-provided answer (line 20: `AUTO HITL:merge... -> outcome merge.approved`, after the "waiting" line shows a human answered) and, by the same rule, for whatever an `AUTO`-resolved certain decision would produce.
  - Rule 9: "The agent MUST NOT invent a response ... A `HITL` is answered only by a response to that `HITL` given after it is reached, or by the agent under `AUTO`."
- **Problem:** Given how central it is that a `HITL` decision boundary "MUST NOT be replaced by an agent decision" except under `AUTO`, the trace format gives no distinct effect for "the agent decided this automatically" vs. "a human answered." The worked example only distinguishes the two informally in prose ("the merge decision is uncertain, so the human is asked"), not in the trace's own vocabulary, so a trace alone cannot be audited for rule 9 compliance.
- **Two readings:**
  - Reader A concludes this is fine: the trace is only meant to record *what happened to the program state*, not *who* caused it, and prose/logs elsewhere are responsible for auditing who answered.
  - Reader B expects the trace itself to be the record of compliance with rule 9 and finds it underspecified that two very different situations (agent overrode a human-decision boundary under `AUTO`, vs. a human answered) render as the identical trace line.

---

## 12. No re-prompt is defined for an "insufficient" `HITL` answer

- **Section:** `HITL`.
- **Quote:** "Insufficient or unavailable, and there is a `FALLBACK` | Run the fallback flow." / "... and there is no `FALLBACK` | Execution ends, as with `STOP`."
- **Problem:** The spec is explicit that there is no retry step, but this is easy to misread because it runs against a natural expectation (a person giving an unclear answer would normally be asked again). Since nothing in the DSL offers a "re-ask" primitive, an author who wants a retry has to build it manually (e.g., wrap the `HITL` in a `LOOP` and treat the fallback as a signal to loop back), and it is not obvious from the `HITL`/`FALLBACK` text alone that this is the only way to get that behavior.
- **Two readings:**
  - Reader A (correct per the letter of the text): one insufficient/unavailable answer immediately and permanently routes to `FALLBACK` or ends execution; there is exactly one chance to answer.
  - Reader B, especially when writing a process for a real human workflow, assumes an insufficient answer should prompt a re-ask before falling back, and writes/expects a program that "asks again" without the DSL actually supporting that inside a single `HITL` statement.

---

## 13. Grammar for `AUTO` scope is ungrouped and technically ambiguous

- **Section:** Grammar (EBNF), `hitl` production.
- **Quote:** `hitl = ( [ "AUTO" ] , "HITL:" , identifier , "[" , identifier , { "," , identifier } , "]" | "HITL" ) , "(" , string , ")" , NL , [ fallback ] ;`
- **Problem:** With no parentheses around the first alternative, the EBNF as literally written leaves it unclear whether `[ "AUTO" ]` scopes only over the `"HITL:" , identifier , "[" ...` branch or is meant to be read as applying across the whole alternation (including the bare `"HITL"` branch). The prose (V5, and the explicit invalid example `AUTO HITL("Please review the notes")`) resolves this correctly, but the grammar block itself, read in isolation, is not self-disambiguating.
- **Two readings:**
  - Reader A applies standard EBNF precedence (comma binds tighter than `|`) and reads `[ "AUTO" ]` as scoped only to the first alternative, matching the prose.
  - Reader B, skimming just the grammar, could initially read the alternation as `[ "AUTO" ] , ( "HITL:" ... | "HITL" )`, i.e., `AUTO` optionally preceding *either* form — which would make `AUTO HITL("...")` grammatically well-formed, directly contradicting V5 and the invalid example given right below it.

---

## 14. `REQUIRE`/`DELEGATE`/`EMIT` arguments are restricted to a single identifier

- **Sections:** Syntax (Lines and statements table), Grammar (`simple`, `require`).
- **Quote:** `simple = ( "DELEGATE" | "VERIFY" | "EMIT" ) , identifier , NL | ...` and `require = "REQUIRE" , identifier , NL , [ fallback ] ;` — and identifiers are "letters, digits, `-` and `_`," starting with a letter (no spaces, no free text).
- **Problem:** This confines every requirement, delegated work item, and artifact name to a single hyphen/underscore identifier. It's workable but means a naturally multi-word requirement ("signed off design document") must be encoded as a single token (`signed-off-design-document`), and the spec gives no guidance on this encoding, so different authors will hyphenate differently for the same real-world requirement, which matters for V6/V7's name-matching rules (they compare identifiers verbatim).
- **Two readings:**
  - Author A writes `REQUIRE design-doc-signoff`.
  - Author B, describing the same real precondition, writes `REQUIRE signoff` or `REQUIRE design-signoff`. Both are individually valid per the grammar, but nothing in the spec ties either identifier to a canonical real-world meaning, so two programs (or two authors on the same team) can silently diverge on what "the same" requirement is called, with no rule to catch the mismatch.

---

## 15. Uniqueness rules (V7) cover `HITL`/`VERIFY` names but not `LOOP` names or repeated identical statements

- **Sections:** Validity rule V7, `LOOP`.
- **Quotes:**
  - V7: "two `HITL` statements use the same name, a name is used by both a `HITL` and a `VERIFY`, or an answer list is empty or repeats an answer" → INVALID.
  - LOOP: "`<name>` is only a label. No statement refers to it; `BREAK` takes no name."
- **Problem:** The spec polices name collisions only between `HITL`/`VERIFY` subjects (because those are the names outcomes attach to). It says nothing about whether two different `LOOP`s may share the same `<name>`, which is consistent with "no statement refers to it" being harmless — but the spec never states this explicitly as a rule, leaving a careful reader to infer it by absence rather than by an explicit "duplicate LOOP names are allowed" statement, unlike the explicit V7 treatment of `HITL`/`VERIFY`.
- **Two readings:**
  - Reader A infers, correctly by the letter of the rules (no validity rule forbids it, and LOOP names are documented as non-referential), that duplicate `LOOP:<name>` labels anywhere in a program are harmless and legal.
  - Reader B, noting that the spec is careful to enumerate exactly which names must be unique (V7) and lists `LOOP` nowhere in that discussion, wonders whether the omission is deliberate silence (allowed) or simply an oversight that should be read as "also invalid by analogy," since every other named construct (`HITL`) does get a uniqueness rule.
