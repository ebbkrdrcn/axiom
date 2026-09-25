# Critic report: variant C (`→ AUTO` written as a child line directly under `HITL`, before `→ FALLBACK`)

Sources: `variants/C.md`, `rendered/C/X01–X06`, `probes/C-X0n-p{1,2,3}.md`, `probes/C-CONF-p1.md`.

Variant C's AUTO form (spec, AUTO > Syntax): "`→ AUTO` is written directly under a `HITL`, indented one level. It marks that one `HITL` as automatically resolvable. If the `HITL` also has a `→ FALLBACK`, `→ AUTO` comes first. `→ AUTO` has no children. `AUTO` is not a statement of its own and applies to no other statement."

---

## X01: authoring, one auto-resolvable decision

All three probes produced the same program:

```text
DELEGATE implementation
VERIFY implementation
HITL:merge("Merge this change?")
  → AUTO
  → FALLBACK
      → TRANSITION "Blocked"
        STOP
WHEN merge.approved
  → TRANSITION "Merged"
WHEN merge.declined
  → TRANSITION "Rework"
```

| Probe | D1 AUTO form/attachment | D2 named HITL + 2 WHENs | D3 FALLBACK Blocked→STOP, AUTO before FALLBACK | D4 no uncertainty cond./flow in AUTO |
|---|---|---|---|---|
| p1 | met: `HITL:merge(...)` / `  → AUTO` | met: `WHEN merge.approved` / `WHEN merge.declined` | met: `→ AUTO` then `→ FALLBACK` / `→ TRANSITION "Blocked"` / nested `STOP` | met: `→ AUTO` has no children |
| p2 | met (identical) | met | met | met |
| p3 | met (identical) | met | met | met |

- Fallback body: all three used the nested-`STOP` form, which the spec calls equivalent ("The following two forms are equivalent"). This is the same across probes, so it is not a divergence and not an error.
- Divergence: none. The programs are character-identical.
- Verdict: **PASS**
- Errors: none.
- Hesitations about AUTO form: 0. Every probe's assumption list mentions AUTO placement or order (p1 #6, p2 #5, p3 #6), but each one justifies it directly from the spec ("The spec mandates that when a `HITL` has both, `→ AUTO` must come before `→ FALLBACK`; this ordering was followed exactly"). None says the placement is unclear or needed an assumption.

## X02: authoring, two decisions, only one auto-resolvable

| Probe | D1 AUTO on notes HITL only | D2 no AUTO on approval | D3 two named HITLs, own WHENs, right order |
|---|---|---|---|
| p1 | met: `HITL:notes(...)` / `  → AUTO` | met: `HITL:approval("Approve the release?")` has no child lines | met: `notes.short/detailed`, then `approval.approved/rejected` |
| p2 | met: `HITL:format(...)` / `  → AUTO` | met: `HITL:approve(...)` bare | met |
| p3 | met: `HITL:notes(...)` / `  → AUTO` | met: `HITL:approve(...)` bare | met |

- Every probe explicitly ties "never by the agent" to leaving out `→ AUTO`. For example, p1 #5: "is expressed by simply omitting `→ AUTO`. Per the spec's table, a `HITL` without `AUTO` always asks the human".
- Divergence: none material. Only the identifiers differ (notes/format, approval/approve), and p1/p3 add blank lines.
- Verdict: **PASS**
- Errors: none. No probe placed AUTO where it could reach the second HITL.
- Hesitations about AUTO form: 0.

## X03: trace, decision sufficiently determined

| Probe | D1 agent resolves, no human | D2 merge.approved → Merged, declined unmatched | D3 no FALLBACK, offline human irrelevant | D4 final "Merged" |
|---|---|---|---|---|
| p1 | met: "**The human is not asked.**" | met: "`merge.declined` does not match … skipped" | met: "`FALLBACK` is not used … their being offline is never actually tested" | met |
| p2 | met: "agent automatically establishes `merge.approved`" | met | met: "'no human is currently online' is a distractor" | met |
| p3 | met | met | met: "not relevant to the trace" | met |

- Divergence: none.
- Minor note: p2's Step 3 heading has a self-correction ("with `→ AUTO` (no `→ FALLBACK`... wait, there is one here)"). It briefly misread whether a FALLBACK child was present, then fixed it immediately, and the reasoning that follows is correct. This concerns FALLBACK, not where AUTO is placed or what it binds to, so it is not counted as an AUTO-form hesitation and not tagged.
- Verdict: **PASS**
- Errors: none.
- Hesitations about AUTO form: 0. All three say that deciding whether the decision is "sufficiently determined" is a judgment call, but that is about AUTO semantics, not form.

## X04: trace, decision uncertain, human does not respond

| Probe | D1 uncertain; 90% not certainty; agent must not decide | D2 human asked | D3 no response → FALLBACK Blocked, STOP; no WHEN evaluated | D4 final "Blocked" |
|---|---|---|---|---|
| p1 | met: "The agent's 90% estimate is therefore explicitly insufficient" | met: "`HITL:merge` asks 'Merge the dependency upgrade?'" | met: "neither `WHEN` is ever evaluated" | met |
| p2 | met: "90% confidence … is explicitly disqualified" | met | met: "the two `WHEN` constructs … are never evaluated" | met |
| p3 | met | met: "the runtime asks the human" | met | met |

- All three correctly say that AUTO failing to resolve the decision is not a FALLBACK. For example, p3: "This is not a `FALLBACK` case yet".
- All three add the same caveat: the runtime decides when a non-response counts as "unavailable", and under a strict reading the process would stay suspended. Because all three share it and reach the same answer, this is not a divergence.
- Divergence: none.
- Verdict: **PASS**
- Errors: none.
- Hesitations about AUTO form: 0.

## X05: validity of AUTO placements

| Probe | D1 S1 VALID | D2 S2 INVALID | D3 S3 INVALID | D4 S4 INVALID |
|---|---|---|---|---|
| p1 | met: cites hitl EBNF and "`→ AUTO` is written directly under a `HITL`" | met: "`AUTO` applies only to `HITL`" + Scope rule 6 | met: "`AUTO HITL:deploy(...)` therefore matches no production" | met: "`AUTO` is not a control-flow container" + "Uncertainty is not a DSL condition" |
| p2 | met | met | met: "the line does not start with the `HITL` keyword" | met |
| p3 | met | met | met: "concatenating them into one token stream … is not one of the defined statement forms" | met |

- p1 notes as an assumption that "yes" is an allowed answer identifier. That is about answer vocabulary, not AUTO form.
- Divergence: none.
- Verdict: **PASS**
- Errors: none.
- Hesitations about AUTO form: 0. p2 and p3 say explicitly "No assumption beyond the given specification was required".

## X06: which decisions may the agent make

| Probe | D1 only wording, only when determined | D2 release: no (no AUTO; confidence ≠ certainty) | D3 human asked the wording question |
|---|---|---|---|
| p1 | met: "Only the **`wording`** decision … only when the agent can determine a single protocol-compatible decision" | met: "has no `→ AUTO` … 'a confidence score alone does not establish certainty'" | met: "it asks the human the message 'Short or detailed release notes?'" |
| p2 | met | met | met: "The human is asked the message 'Short or detailed release notes?'" |
| p3 | met | met: "the agent must not decide it under any circumstances" | met |

- All three point out the same gap: the spec does not say what happens when a `HITL` has no `FALLBACK` and the response is unusable. All three assume indefinite suspension. The answers agree, so this is not a divergence. It is a FALLBACK gap, not an AUTO-form hesitation.
- Minor inaccuracy in p1 (Q2): "only that response … can establish `release.approved` or `release.declined`." The program tests only `release.approved`, so under the spec a "declined" answer would be an insufficient response, not the outcome `release.declined`. This does not affect any D-item. Tagged **OTHER** (1).
  - Spec sentence: "The response establishes the outcome `<name>.<answer>`, where `<answer>` is one of the answers tested by the `WHEN <name>.<answer>` constructs that follow. A response that corresponds to none of these answers is insufficient (see `FALLBACK`)."
- Divergence: none material.
- Verdict: **PASS**
- Errors: OTHER ×1 (minor, outside any D-item).
- Hesitations about AUTO form: 0.

---

## Error tally

| Tag | Count | Where |
|---|---|---|
| FORM | 0 | — |
| SCOPE | 0 | — |
| DANGER | 0 | — |
| OVERCAUTION | 0 | — |
| FALLBACK-CONFUSION | 0 | — |
| OTHER | 1 | X06-p1: an untested answer (`release.declined`) is treated as a possible outcome (HITL answer-set sentence quoted above) |

## CONF probe (C-CONF-p1)

The probe lists 8 items, and all of them touch HITL, AUTO or FALLBACK:

1. The scope of "the `WHEN` constructs that follow" used to judge whether a response is sufficient; also how sufficiency works for an unnamed HITL. (HITL/FALLBACK)
2. What happens after a FALLBACK flow ends without `STOP`/`BREAK`: does execution fall through or is it undefined? (FALLBACK)
3. A HITL with no FALLBACK when the response is unavailable or insufficient: suspend forever, or reject the program? (HITL/FALLBACK)
4. Whether AUTO's resolved answer must be one of the answers the WHENs test ("protocol-compatible" is undefined). (AUTO semantics)
5. In WHEN, "not satisfied" lumps together three cases: resolved to a different answer, not yet reached, and an undefined name. (HITL outcomes)
6. Whether re-establishing a HITL or VERIFY outcome overwrites the earlier one. (HITL outcomes)
7. Whether a FALLBACK that falls through undermines the guarantee that a HITL "must not be silently replaced". (HITL/FALLBACK)
8. Whether a WHEN can see a HITL or AUTO outcome from a FORK branch that has not been joined. (HITL/AUTO outcomes)

Items specific to variant C's AUTO form (`→ AUTO` child line, ordering relative to `→ FALLBACK`, one-HITL binding): **none**. Item 4 is the only AUTO-focused item, and it is about the meaning of AUTO's resolution ("protocol-compatible"), not about how or where AUTO is written. It would come up the same way in any variant.

---

```
VARIANT C
scenarios_passed: 6/6
probe_D_items_met: 66/66
divergent_scenarios: []
errors_by_tag: FORM=0 SCOPE=0 DANGER=0 OVERCAUTION=0 FALLBACK-CONFUSION=0 OTHER=1
hesitations_about_AUTO_form: 0
conf_items_about_AUTO_form: 0
```
