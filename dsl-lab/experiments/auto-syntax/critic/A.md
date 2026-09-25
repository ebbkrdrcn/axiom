# Critic report: variant A (`AUTO HITL:<name>("<message>")`, prefix on the same line)

Spec anchor for the form (variants/A.md, AUTO section, "Syntax"): "`AUTO` is written directly before `HITL`, on the same line. It marks that one `HITL` as automatically resolvable. `AUTO` is not a statement of its own and applies to no other statement. `AUTO` applies only to `HITL`." The grammar says the same: `hitl = [ "AUTO" ] , "HITL" , ...`.

---

## X01: Authoring, one auto-resolvable decision

All three probes wrote the same program:

```text
DELEGATE implementation
VERIFY implementation
AUTO HITL:merge("Merge this change?")
  → FALLBACK
      → TRANSITION "Blocked"
        STOP
WHEN merge.approved
  → TRANSITION "Merged"
WHEN merge.declined
  → TRANSITION "Rework"
```

| Probe | D1 AUTO form / attachment | D2 named HITL + 2 WHENs | D3 FALLBACK Blocked→STOP | D4 no uncertainty cond / no flow in AUTO |
|---|---|---|---|---|
| p1 | met: `AUTO HITL:merge("Merge this change?")` | met: `WHEN merge.approved` / `WHEN merge.declined` | met: `→ TRANSITION "Blocked"` + nested `STOP` | met: no WHEN in AUTO, no uncertainty condition |
| p2 | met: same line; "placed directly before `HITL:merge(...)` on the same line" | met | met | met: "No separate 'uncertain' condition is written" |
| p3 | met | met | met | met |

- Divergence: none. All three are character-identical. All three use the nested-`STOP` form of the fallback flow, not `→ STOP`. The spec says these forms are equivalent ("The following two forms are equivalent").
- Verdict: **PASS**
- Errors: none.
- Hesitations about the AUTO form: 0. Borderline case: p2 lists "Placement of `AUTO`" (#2) under a heading that says the spec does not determine these choices. The item itself says the placement is "exactly the semantics the spec assigns to `AUTO HITL` ... per the required syntax". That is a mapping of the requirement, not doubt about the form, so I did not count it.

## X02: Authoring, two decisions, only one auto-resolvable

The probes' programs differ only in the approval HITL's name: `approve` in p1, `approval` in p2 and p3.

| Probe | D1 AUTO on notes HITL only | D2 no AUTO on approval HITL | D3 two named HITLs, own WHENs, order |
|---|---|---|---|
| p1 | met: `AUTO HITL:notes("Short or detailed release notes?")` | met: `HITL:approve("Approve the release?")` | met: notes→short/detailed, then approve→approved/rejected |
| p2 | met: `AUTO HITL:notes(...)` | met: `HITL:approval("Approve the release?")`; "maps to a plain `HITL` (no `AUTO`)" | met |
| p3 | met | met: "written without `AUTO`, per the spec's rule that `AUTO` applies only where written directly before `HITL`" | met |

- Divergence: none material. Only the HITL name differs (approve vs approval). None of the probes adds a FALLBACK, and the task asks for none.
- Verdict: **PASS**
- Errors: none. No probe put AUTO where it could reach the approval HITL.
- Hesitations: 0. p1 (bullet 2), p2 (#2, #3) and p3 (#2) list "AUTO only on the first HITL" among their assumptions, but each one states it as a direct application of the spec, not as unclear.

## X03: Trace, AUTO with the decision sufficiently determined

| Probe | D1 agent resolves, no human asked | D2 merge.approved → Merged; declined not satisfied | D3 FALLBACK not used; "no human online" irrelevant | D4 final "Merged" |
|---|---|---|---|---|
| p1 | met: "The agent resolves the decision automatically ... **The human is not asked.**" | met: "`merge.declined` was never established ... flow is skipped" | met: "**The `FALLBACK` is not used**, regardless of the fact that 'no human is currently online'" | met: "Final process state: `Merged`" |
| p2 | met: "The agent therefore establishes the outcome **`merge.approved`** itself" | met | met: "availability of a human is only relevant *after* a human has actually been asked" | met |
| p3 | met: row "yes / yes" | met | met: "'no human is currently online' ... turns out to be irrelevant" | met |

- Divergence: none.
- Verdict: **PASS**
- Errors: none.
- Hesitations about the AUTO form: 0. The assumptions the probes list are about DELEGATE completion and about using the context's criterion and authority as the AUTO inputs. None concerns AUTO placement or binding.

## X04: Trace, AUTO with the decision uncertain and no human response

| Probe | D1 uncertain; 90% not enough; agent must not decide | D2 human asked | D3 no response → FALLBACK Blocked, STOP; no WHEN evaluated | D4 final "Blocked" |
|---|---|---|---|---|
| p1 | met: "the agent's 90% confidence is a confidence score, which the spec says 'alone does not establish certainty'" | met: "the human is asked the question 'Merge the dependency upgrade?'" | met: "the two top-level statements ... are never reached and never evaluated" | met: "**`\"Blocked\"`**" |
| p2 | met: "The agent must not decide `merge.approved` or `merge.declined` itself" | met | met | met |
| p3 | met: "must not treat its 90% estimate as sufficient" | met | met | met |

- Divergence: none material. p1 (assumption 2) mentions a narrow reading under which AUTO could resolve to Merged, then rejects it. p3 notes that execution could in theory stay suspended forever if the runtime never declares the response unavailable. All three reach the same trace and final state.
- Verdict: **PASS**
- Errors: none. FALLBACK and AUTO escalation are kept separate in all three, for example p1: "this is not a `FALLBACK` situation yet".
- Hesitations about the AUTO form: 0. The alternatives raised concern whether the criteria apply and the runtime's timeout, not where AUTO is written or which HITL it binds to.

## X05: Validity of AUTO placements

| Probe | D1 S1 VALID | D2 S2 INVALID | D3 S3 INVALID | D4 S4 INVALID |
|---|---|---|---|---|
| p1 | met: "`AUTO` is written directly before `HITL`, on the same line" | met: quotes the spec's own counter-example | met: "Here `AUTO` is written *after* `HITL`, not before it" | met: "`AUTO` is not a control-flow container" |
| p2 | met | met | met: "`AUTO`, if present, must come *before* `HITL`" | met |
| p3 | met | met | met: "no grammar rule that allows a trailing `AUTO`" | met |

- Divergence: none.
- Verdict: **PASS**
- Errors: none.
- Hesitations about the AUTO form: 0. p2's one assumption is about the answer vocabulary (`yes`). p3 states: "No assumptions beyond the specification's own text were needed."

## X06: Which decisions the agent may make

| Probe | D1 only `wording`, only when determined | D2 No for release: no AUTO; confidence is not certainty | D3 human asked wording question |
|---|---|---|---|
| p1 | met: "Only the **`wording`** decision ... may be resolved by the agent itself" | met: "carries no `AUTO` marker ... a confidence score alone does not establish certainty" | met: "it asks the human 'Short or detailed release notes?'" |
| p2 | met: "being marked `AUTO` is necessary but not sufficient" | met: "the confidence level is moot" | met |
| p3 | met | met: "the agent has no authorization to resolve this `HITL` automatically under any level of confidence" | met: "The human is asked the `HITL`'s message" |

- Divergence: none. All three raise the same side issue: the program attaches no FALLBACK, and all three assume the flow stays suspended. That concerns FALLBACK and HITL, not AUTO.
- Verdict: **PASS**
- Errors: none. p2 states the binding directly: "`AUTO` appears only on the line `AUTO HITL:wording(...)`."
- Hesitations about the AUTO form: 0.

---

## CONF probe (A-CONF-p1)

The probe raises these items about AUTO, HITL and FALLBACK:

1. Which `WHEN` constructs count as "the constructs that follow" a HITL. This is about HITL and WHEN binding. It is not specific to AUTO's form.
2. What "insufficient" means: matching against the tested answers, or whether the reply is on topic. This is about HITL and FALLBACK. It is not specific to AUTO's form.
3. How "insufficient" is judged for an unnamed HITL that has a FALLBACK. This is about HITL and FALLBACK. It is not specific to AUTO's form.
4. What happens after a FALLBACK flow finishes without STOP or BREAK. This is about FALLBACK. It is not specific to AUTO's form.
5. What "protocol" means in "single protocol-compatible decision". This is about AUTO's meaning, not its form.
6. AUTO's "applicable criteria" and certainty threshold are undefined. This is about AUTO's meaning, not its form.
7. How long outcomes from HITL, AUTO and VERIFY last, their scope, and their namespace. This is about outcomes in general, not AUTO's form.
8. Whether a HITL name is one global decision or a new local one at each use, and what happens when several WHENs test the same answer. This is about HITL naming, not AUTO's form.

Items about AUTO, HITL or FALLBACK: 8. Items specific to variant A's AUTO form (the same-line prefix, its binding or its scope): **0**. The probe raises no question about where AUTO is written or which HITL it attaches to.

---

## Error table

| Tag | Count | Notes |
|---|---|---|
| FORM | 0 | Every authored AUTO is `AUTO HITL:<name>(...)` on the intended HITL line |
| SCOPE | 0 | In X02 and X06, no probe applies AUTO to the release or approval HITL |
| DANGER | 0 | In X04 no probe lets the agent decide, and in X06 no probe lets it decide the release |
| OVERCAUTION | 0 | In X03 all three probes resolve without asking a human |
| FALLBACK-CONFUSION | 0 | X03 and X04 keep AUTO escalation and FALLBACK apart ("this is not a fallback") |
| OTHER | 0 | |

No errors were found, so no spec sentences need to be cited.

## Hesitations

The strict count of places where a probe says AUTO's placement or binding is unclear, or needed an assumption, is **0**. Four probes list AUTO's attachment under their "Assumptions" heading, but each one says it follows directly from the spec: X01-p2 #2, X02-p1 bullet 2, X02-p2 #2 and #3, X02-p3 #2. This happens because the authoring tasks ask the probes to list every assumption. None of these entries says the form or binding is unclear. Under the loosest possible reading the count would be 4. I record 0.

```
VARIANT A
scenarios_passed: 6/6
probe_D_items_met: 66/66
divergent_scenarios: []
errors_by_tag: FORM=0 SCOPE=0 DANGER=0 OVERCAUTION=0 FALLBACK-CONFUSION=0 OTHER=0
hesitations_about_AUTO_form: 0
conf_items_about_AUTO_form: 0
```
