# Critic part G: iteration 02 (X03, X04, X05, X06)

Graded against `iterations/02/DSL.md` and the expected D-items in each scenario. None of these D-items say "Linter VALID". The linter was consulted only to check which rule it maps each snippet to (see X05).

---

## X03: Execution, AUTO with a determined decision

D-items:
- D1: The decision is determined, so the agent establishes `merge.approved` and no human is asked.
- D2: The FALLBACK is not used; the state becomes "Merged"; the declined-WHEN is skipped; the final state is "Merged".

| Probe | D1 | D2 | Evidence |
|---|---|---|---|
| s1 | met | met | "3. AUTO HITL:merge[…] -> outcome merge.approved"; "Is a human asked? No."; "6. WHEN merge.declined -> false: skip"; "**`Merged`**"; "Is the `FALLBACK` used? No." |
| s2 | met | met | "the agent establishes `merge.approved` itself; the human is not asked; `FALLBACK` is not used"; trace steps 4–6; "**`Merged`**" |
| s3 | met | met | "**the agent answers**, establishing `merge.approved`, and the human is not asked"; "6. WHEN merge.declined -> false: skip"; final `Merged` |
| h1 | met | met | "Is a human asked? No."; "Is the FALLBACK used? No."; "6. WHEN merge.declined -> false: skip"; final `"Merged"` |
| h2 | met | met | "Is a human asked? **No.**"; "Is FALLBACK used? **No.**"; trace step 6 skip; final **"Merged"** |
| h3 | met | met | "Is a human asked? No."; "Is the FALLBACK used? No."; trace step 6 skip; final `"Merged"` |

**Divergence**
- Sonnet: none. All three have the same 7-line trace and the same answers.
- Haiku: none on the D-items. All three have the same trace. h2 adds a wrong side claim, listed under Errors below. It does not change the trace or the answers.

**Errors (outside the D-items)**
1. h2, tagged `SEMANTIC`. h2 says the FALLBACK "only runs if the HITL response is insufficient, unavailable, or (implicitly) if the human were asked and declined." This is wrong. `declined` is a listed answer, so it is a usable response: it establishes `merge.declined` and does not run the FALLBACK.
   - Spec: HITL, "Usable, insufficient, unavailable": "Clearly selects exactly one listed answer (in any wording) | usable". FALLBACK: "A usable response never runs the fallback flow."
   - Classification: `model-error`.
2. h1 and h2, tagged `OTHER`. Both attribute "A usable response never runs the fallback flow" / the FALLBACK trigger to rule V8. V8 is only about how a fallback flow ends. This is a citation error with no effect on the outcome.
   - Spec: Validity rules, V8: "the last item of a fallback flow is not `STOP` or `BREAK`".
   - Classification: `model-error`.
3. h1, tagged `OTHER`. Trace line 5 is written "→ TRANSITION "Merged"", keeping the arrow. This is cosmetic.
   - Spec: "Executing a program": "`<n>. <statement as written> -> <effect>`".
   - Classification: `model-error`.

**Verdict:** PASS-S yes; PASS-H yes.

**NEW issues:** None for the spec. The spec does not show a one-line AUTO-resolved trace (the complete example shows only the `waiting` path), but all six probes produced the same single line on their own.

**Scenario issues:** None.

---

## X04: Execution, AUTO uncertain and the human does not respond

D-items:
- D1: The decision is uncertain; the 90% estimate does not establish certainty; the agent must not decide.
- D2: The human is asked; there is no response, so the FALLBACK runs ("Blocked", STOP); no WHEN is evaluated.
- D3: The final state is "Blocked".

| Probe | D1 | D2 | D3 | Evidence |
|---|---|---|---|---|
| s1 | met | met | met | "The agent's 90% confidence is a confidence score, and per the spec this **does not establish certainty**"; "The agent MUST NOT answer; the human is asked"; trace 3 `waiting`, 4 `fallback`, 5 Blocked, 6 stop; "the two `WHEN merge...` statements … are never executed"; **`Blocked`** |
| s2 | met | met | met | "the agent MUST NOT answer it itself"; "unavailable … runs the fallback flow"; "the two `WHEN` statements are never executed"; **`Blocked`** |
| s3 | met | met | met | "the agent's 90% estimate cannot make the decision certain"; "the human is asked"; "They are never reached, not even to be skipped."; **`Blocked`** |
| h1 | met | met | met | "The agent estimates 90% confidence, which is insufficient"; "The human must be asked."; the trace ends at "6. STOP -> stop" with no WHEN line; **State: "Blocked"** |
| h2 | met | met | met | "90% confidence estimate is a confidence score, which the specification explicitly states does not establish certainty"; "The subsequent WHEN statements are never reached."; **"Blocked"** |
| h3 | met | met | met | "A 90% confidence score alone does not establish certainty"; "the human is asked"; "`WHEN merge.approved` and `WHEN merge.declined` statements are never reached"; **`"Blocked"`** |

**Divergence**
- Sonnet: none. The traces are identical.
- Haiku: none on the D-items. The traces are identical.
- Minor point in h2: it puts the AUTO-certainty evaluation under "Step 4", after the `waiting` of step 3, which blurs the order. The trace is still the same as in h1 and h3. This is not material.

**Errors:** None that affect the D-items.
- Tag: `OTHER` (minor, not counted). s1 says "not certain and/or not clearly within the agent's authority". Authority was not actually at issue here, but the conclusion is correct.

**Verdict:** PASS-S yes; PASS-H yes.

**NEW issues**
1. s1, s2 and s3 each flag that the spec has no trace example of a HITL that resolves to `fallback`. They inferred the pair `waiting` then `fallback` by analogy with lines 19–20 of the complete example. All six probes converged on it, so this is not an error.
   - Spec: "Executing a program", the trace effect list includes `fallback`, but no example uses it.
   - Classification: `underspecified-syntax` (low priority).

**Scenario issues:** None.

---

## X05: Interpretation, validity of AUTO placements

D-items:
- D1: Snippet 1 is VALID.
- D2: Snippet 2 is INVALID (V5).
- D3: Snippet 3 is INVALID (form: AUTO must come before HITL on the same line).
- D4: Snippet 4 is INVALID (V5).

| Probe | D1 | D2 | D3 | D4 | Evidence |
|---|---|---|---|---|---|
| s1 | met | met | met | met | "**VALID.**"; "**INVALID — rule V5.**" ×3; snippet 3: "`AUTO` appears *after* the `HITL:deploy[...](...)` … this ordering isn't a recognized form under the grammar's `hitl` production" |
| s2 | met | met | met | met | same verdicts; snippet 3: "`AUTO` is an optional token that must precede `"HITL:"`" |
| s3 | met | met | met | met | same verdicts; snippet 3: "`AUTO`, if present, must precede `HITL:` … does not match any other line form" |
| h1 | met | met | met | met | "**VALID**"; "**INVALID - Rule V5**" ×3; snippet 3: "`AUTO` must be written directly **before** `HITL`" |
| h2 | met | met | met | met | same verdicts; snippet 3: "the specification requires `AUTO` to be written directly before `HITL`, not after it" |
| h3 | met | met | met | met | same verdicts; snippet 3: "The placement of `AUTO` at the end of the line is not valid—it must precede the HITL." |

**Divergence**
- Sonnet: none.
- Haiku: none.
- All six probes cite V5 for snippet 3. The linter reports snippet 3 as V1 ("unrecognised statement"), plus a knock-on V6 on line 2. This is a disagreement between the probes and the linter on which rule applies, not a divergence within a trio. D3 does not require a rule number.

**Errors:** None.

**Verdict:** PASS-S yes; PASS-H yes.

**NEW issues**
1. There is no named validity rule for a line that matches no statement form. The table V1–V10 does not cover a line such as `HITL:…(…) AUTO`, or any line with trailing or unknown tokens. The linter files it under V1, whose text is only about indentation. The probes file it under V5, whose text ("`AUTO` is not immediately followed, on the same line, by a decision `HITL`") only fits literally. Each choice is defensible, and they disagree.
   - Spec: Validity rules. "A program that breaks any of these rules is INVALID" lists only V1–V10. "Lines and statements" gives the permitted forms but ties them to no rule number.
   - Classification: `spec-gap`.
   - Suggested fix: add a rule, for example V0/V11 "a line does not match any form in **Lines and statements** / the grammar". Alternatively, widen V1 to say "indentation or line form".

**Scenario issues:** D3 says "form" with no rule number. Given the spec gap above, V5 (what the probes cite) and a grammar/V1 reading (what the linter reports) should both be accepted, which is how this critique graded it.

---

## X06: Interpretation, which decisions the agent may make

D-items:
- D1: Only `wording`, and only when the decision is certain and within the agent's authority.
- D2: No (there is no AUTO; confidence alone is not enough).
- D3: The human is asked the wording question.
- D4: `release.rejected` is established; the approved-WHEN is skipped; execution ends normally (no FALLBACK: the answer is usable).

| Probe | D1 | D2 | D3 | D4 | Evidence |
|---|---|---|---|---|---|
| s1 | met | met | met | met | D1: "only when it can single out exactly one of `short`/`detailed` with certainty (not merely high confidence) and has the authority to do so". D2: "No. `HITL:release…` carries no `AUTO`". D3: "the human is asked". D4: "`release.rejected` is established … skipped … ends normally" |
| s2 | met | met | met | met | D1: "only when the decision is **certain and within the agent's authority**". D2: "No." D3: "The human is asked". D4: "ends normally … no fallback (… the response was usable)" |
| s3 | met | met | met | met | D1: "'the decision is certain and within the agent's authority'". D2: "No." D3: "put to the human". D4: "ends normally per rule 10" |
| h1 | **not met** | met | met | met | D1: "The `wording` decision may the agent make by itself, under the condition that it is sufficiently determined." The condition gives only determinacy/certainty and never mentions authority. D2: "No". D3: "The human is asked". D4: "Execution ends normally" |
| h2 | met | met | met | met | D1: "sufficiently determined (certain) … The decision is within the agent's authority". D2: "**No.**" D3: "**the human is asked**". D4: "The program ends normally … without error" |
| h3 | met | met | met | met | D1: "The decision is within the agent's authority". D2: "No". D3: "The human is asked the wording question." D4: "Execution ends normally … No fallback is triggered" |

**Divergence**
- Sonnet: none.
- Haiku: material. On the D1 condition, h1 states only "sufficiently determined", while h2 and h3 state both certainty and authority.

**Errors**
1. h1, D1, tagged `SEMANTIC`. h1 leaves the authority requirement out of the condition under which the agent may answer an `AUTO` HITL. No action is taken in this scenario, so this was not tagged DANGER. Read as a rule, though, it would let the agent answer without authority.
   - Spec: "Who decides a `HITL`": "Decision certain and within the agent's authority?". AUTO table: "The decision is certain and within the agent's authority | The agent establishes…".
   - Contributing wording: the AUTO section's defining sentence is "`AUTO` means: resolve the decision automatically when it is sufficiently determined; otherwise ask the human." It does not mention authority, which appears only as the fifth bullet among the uncertainty examples. h1 paraphrased this sentence almost verbatim.
   - Classification: `misleading-wording`.
2. s1, tagged `OTHER` (not counted against the D-items). s1 misquotes the HITL section as saying it "'MUST be replaced by an agent decision' only if marked `AUTO`". The spec says "MUST NOT be replaced by an agent decision, unless it is marked with `AUTO`". s1's conclusion is correct.
   - Classification: `model-error`.

**Verdict:** PASS-S yes; PASS-H **no** (h1 misses D1, and the haiku trio diverges).

**NEW issues**
1. The AUTO definition sentence omits authority, as explained under Errors item 1. Suggested fix: "resolve the decision automatically when it is certain and within the agent's authority; otherwise ask the human."
   - Spec: AUTO, "`AUTO` means: …".
   - Classification: `misleading-wording`.

**Scenario issues:** None.

---

## Summary table

| ID | PASS-S | PASS-H | sonnet D met | haiku D met | tags | top spec section |
|---|---|---|---|---|---|---|
| X03 | yes | yes | 6/6 | 6/6 | SEMANTIC (h2, not a D-item), OTHER ×2 | HITL › Usable, insufficient, unavailable ("A usable response never runs the fallback flow") |
| X04 | yes | yes | 9/9 | 9/9 | — | Executing a program › trace effects (no `fallback` example) |
| X05 | yes | yes | 12/12 | 12/12 | — | Validity rules (no rule for a line that matches no form; V1 vs V5) |
| X06 | yes | no | 12/12 | 11/12 | SEMANTIC (h1 D1), OTHER (s1) | AUTO › "`AUTO` means: resolve … when it is sufficiently determined" (omits authority) |

```
PART SUMMARY
scenarios: 4
pass_s: 4/4   pass_h: 3/4
d_items_s: 39/39   d_items_h: 38/39
danger_s: 0   danger_h: 0
```
