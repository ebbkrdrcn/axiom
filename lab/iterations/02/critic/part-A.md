# Critic part A: iteration 02 (S01–S05)

Spec: `dsl-lab/iterations/02/DSL.md`. Linter: `dsl-lab/iterations/02/lint.txt`. I used the linter only for the "Linter VALID" D-items about each probe's own authored program (block1 of S01–S04). For S05 I did not use it, because the linter blocks there are the quoted snippets or suggested corrections.

---

## S01

Authoring task: an auto-resolvable merge decision.

All six probes wrote the same program, character for character:

```text
DELEGATE implementation
VERIFY implementation
AUTO HITL:merge[approved, declined]("Merge this change?")
WHEN merge.approved
  → TRANSITION "Merged"
WHEN merge.declined
  → TRANSITION "Rework"
```

| Probe | D1 Linter VALID | D2 DELEGATE before VERIFY | D3 `AUTO HITL:…[a,b]("Merge this change?")` | D4 two WHEN → Merged / Rework | D5 no uncertainty condition, no flow in AUTO |
|---|---|---|---|---|---|
| s1 | met (`S01-s1.md block1: VALID`) | met: `DELEGATE implementation` / `VERIFY implementation` | met: `AUTO HITL:merge[approved, declined]("Merge this change?")` | met: `WHEN merge.approved → TRANSITION "Merged"`, `WHEN merge.declined → TRANSITION "Rework"` | met: no condition on uncertainty; the AUTO line has no children |
| s2 | met (VALID) | met | met | met | met |
| s3 | met (VALID) | met | met | met | met |
| h1 | met (VALID) | met | met | met | met |
| h2 | met (VALID) | met | met | met | met |
| h3 | met (VALID) | met | met | met | met |

**Divergence.** Sonnet: none, because the programs are identical. Haiku: none, for the same reason.

**Errors.** None affects a D-item. These are in the assumption text only:

- **h1, assumption 3 (`OTHER`, model-error).** h1 writes: "execution ends (as per specification rule V8: an insufficient or unavailable response with no fallback causes execution to end like `STOP`)". The rule is cited wrongly. V8 is about how a fallback flow must end. The behaviour h1 describes is in HITL → What happens: "Insufficient or unavailable, and there is no `FALLBACK` | Execution ends, as with `STOP`", and in Execution rule 8.
- **h2, assumption 3 (`SEMANTIC`, model-error).** h2 writes: "If the human response is unavailable and no fallback is provided, execution ends normally (as per rule 8…)". The spec does not say "normally". HITL → What happens says: "Execution ends, as with `STOP`. No outcome is established." In the spec, "ends normally" is the wording of rule 10, which covers reaching the last statement.

**Verdict.** PASS-S: yes. PASS-H: yes.

**New issues.** None.

---

## S02

Authoring task: a verify-until-accepted loop.

All six probes match the canonical program. They differ only in the loop label: s1 and s2 use `implementation`, s3 `delivery`, h1 `implementation`, h2 `implementation-cycle` and h3 `deliver`.

| Probe | D1 Linter VALID | D2 body: DELEGATE, VERIFY, WHENs | D3 accepted → BREAK; rejected → DELEGATE correction | D4 `EMIT source-code` after the loop, at top level |
|---|---|---|---|---|
| s1 | met (VALID) | met: `DELEGATE implementation` / `VERIFY implementation` / `WHEN …` | met: `WHEN implementation.accepted → BREAK`, `WHEN implementation.rejected → DELEGATE correction` | met: `EMIT source-code` at column 0 |
| s2 | met | met | met | met |
| s3 | met | met | met | met |
| h1 | met | met | met | met |
| h2 | met | met | met | met |
| h3 | met | met | met | met |

**Divergence.** None in either trio. A `LOOP` name is only a label ("`<name>` is only a label. No statement refers to it"), so the different labels are not material.

**Errors.** None affects a D-item.

- **h3, assumption 5 (`OTHER`, model-error).** h3 writes: "the loop's last statement is complete, so the next iteration begins (per rule 1 of 'Execution in ten rules')". The citation is wrong. The loop restart is Execution rule 5: "At the end of a loop body, the body starts again from its first statement."

**Verdict.** PASS-S: yes. PASS-H: yes.

**New issues.** None.

---

## S03

Authoring task: two parallel reviews with a JOIN.

All six probes wrote the same program, character for character:

```text
FORK
  → DELEGATE security-review
      VERIFY security-review
  → DELEGATE performance-review
      VERIFY performance-review
JOIN
TRANSITION "Release"
```

| Probe | D1 Linter VALID | D2 one FORK, two branches, DELEGATE then nested VERIFY | D3 JOIN at FORK indentation, then TRANSITION "Release" |
|---|---|---|---|
| s1 | met (VALID) | met: `→ DELEGATE security-review` / `    VERIFY security-review` (nested, not a separate `→`) | met: `JOIN` at column 0, then `TRANSITION "Release"` |
| s2 | met | met | met |
| s3 | met | met | met |
| h1 | met | met | met |
| h2 | met | met | met |
| h3 | met | met | met |

**Divergence.** None in either trio.

**Errors.** None affects a D-item.

- **h2, assumption 2 (`OTHER`, model-error).** h2 writes: "The specification requires that verified results must match names produced by `VERIFY` in the program (rule V6)." This misstates V6, which concerns only what a `WHEN` tests: "a `WHEN` tests `x.y`, and the program contains neither `VERIFY x` … nor `HITL:x[…]` listing `y`". The program has no `WHEN`, so V6 is not relevant here.

**Verdict.** PASS-S: yes. PASS-H: yes.

**New issues.** None.

---

## S04

Authoring task: a REQUIRE, then a decision HITL with a FALLBACK.

All six programs have the same structure. The only difference is the wording of the question string: "Which region to deploy to: eu or us?" (h1–h3), "Which region should we deploy to?" (s1), "Which region would you like to deploy to?" (s2) and "Which region should this be deployed to?" (s3).

| Probe | D1 Linter VALID | D2 `REQUIRE deployment-target` first | D3 `HITL:<n>[eu, us]` (no AUTO) + FALLBACK with TRANSITION "Blocked" then STOP | D4 WHEN eu → eu-deployment; WHEN us → us-deployment | D5 `EMIT deployment-log` at top level after the WHENs |
|---|---|---|---|---|---|
| s1 | met (VALID) | met: line 1 is `REQUIRE deployment-target` | met: `HITL:region[eu, us](…)` / `→ FALLBACK` / `→ TRANSITION "Blocked"` / `→ STOP` | met: `WHEN region.eu → DELEGATE eu-deployment`, `WHEN region.us → DELEGATE us-deployment` | met: `EMIT deployment-log` at column 0, last line |
| s2 | met | met | met | met | met |
| s3 | met | met | met | met | met |
| h1 | met | met | met | met | met |
| h2 | met | met | met | met | met |
| h3 | met | met | met | met | met |

**Divergence.** None is material. The question string is free text, and the scenario does not fix it.

**Errors.** None.

**Verdict.** PASS-S: yes. PASS-H: yes.

**New issues.** None.

---

## S05

Interpretation task: judge the validity of four snippets.

| Probe | D1 A INVALID (V5; `decision.uncertain` also V6) | D2 B INVALID (V2) | D3 C VALID | D4 D INVALID (V8) |
|---|---|---|---|---|
| s1 | **not met**: "INVALID — rule V5". V6 is never cited, and the summary table says "V5" only. s1 notes that "`AUTO` never contains a flow" but folds it into V5 ("subsumed under V5"). It never says that `decision.uncertain` is an undeclared outcome. | met: "INVALID — rule V2 (BREAK is not inside a LOOP)" | met: "VALID (no rule V1–V10 is violated)" | met: "INVALID — rule V8" |
| s2 | met: "INVALID (rule V5)" and "would independently violate **V6**: `decision` is never a `VERIFY` result nor a `HITL` name" | met: "INVALID (rule V2)" | met: "VALID" | met: "INVALID (rule V8)" |
| s3 | met: "INVALID — rule V5 … also V1 … and V6 (`decision.uncertain` is not a producible outcome)" | met: "INVALID — rule V2" | met: "VALID" | met: "INVALID — rule V8" |
| h1 | **not met**: "INVALID … Rule: V5". There is no mention of V6 or `decision.uncertain`. | met: "INVALID … Rule: V2" | met: "VALID" | met: "INVALID … Rule: V8" |
| h2 | **not met**: "Snippet A: INVALID - V5". V6 is not mentioned. | met: "INVALID - V2" | met: "Snippet C: VALID" | met: "INVALID - V8" |
| h3 | **not met**: "Snippet A: INVALID … Rule violated: V5". V6 is not mentioned. | met: "INVALID … V2" | met: "Snippet C: VALID" | met: "INVALID … V8" |

**Divergence.**

- **Sonnet: material.** All three give the same verdicts, but they cite different rules for A: s1 cites V5 only, s2 cites V5 and V6, and s3 cites V5, V1 and V6. That is the D1 split.
- **Haiku: none.** All three give the same verdicts and cite V5 only for A. They are consistent with each other, but all miss V6.

**Errors.**

- **s1, h1, h2 and h3 on D1 (`SYNTAX`, validity-judgement error, model-error).** Each gives the correct INVALID verdict for A but does not report the V6 violation.
  - The rule that should have prevented it is Validity rules, V6: "INVALID if a `WHEN` tests `x.y`, and the program contains neither `VERIFY x` with `y` being `accepted` or `rejected`, nor `HITL:x[…]` listing `y`". Snippet A has neither `VERIFY decision` nor `HITL:decision[…]`.
  - The spec also asks for every broken rule to be reported. Executing a program, step 1: "Check rules V1–V10. If any is broken, do not execute. Report each broken rule by its number."
  - The AUTO section says as well: "Uncertainty is not a DSL condition, state, variable, or keyword."
  - Contributing factor, not a spec defect: the spec's own `invalid` example (`AUTO` / `WHEN decision.uncertain` / `→ HITL("Approve?")`) sits in the AUTO section and is not annotated with rule numbers. Probes that recognise it as "the spec's invalid example" (s1, h2) attribute it wholly to V5.

The verdicts themselves (INVALID, INVALID, VALID, INVALID) are correct in all six probes. No probe tried to execute an invalid snippet, so none is tagged `DANGER`.

**Verdict.**

- **PASS-S: no.** s1 fails D1, and the trio diverges on the rules it cites for A.
- **PASS-H: no.** All three haiku probes fail D1.

**New issues.**

- **Snippet A also breaks V1, and D1 does not list it.** Indentation and scope, item 4, lists the only lines that may have indented children: `LOOP`, `WHEN`, `FORK`, `HITL`/`REQUIRE` (only `→ FALLBACK`), `→ FALLBACK` and `→` items. A bare `AUTO` line is not one of them, and "Any other indentation is INVALID (V1)". s3 and the linter both flag this. No probe is penalised for omitting V1.
- The unannotated `invalid` examples in the AUTO section make it easy to treat snippet A as a pure V5 case. Labelling that example with all the rules it breaks (V1, V5 and V6) would remove the ambiguity.

**Scenario issues.**

- **The prompt and D1 disagree.** The prompt says "cite the rule" (singular), but D1 expects V6 as well as V5. A probe that gives one correct rule per snippet is following the prompt as worded and still fails D1. Either the prompt should ask for "every rule broken", or D1 should make V6 optional.
- **D1 is incomplete.** Under the same strictness it applies to V6, D1 should also list V1.

---

## Summary table

| ID | PASS-S | PASS-H | sonnet D met | haiku D met | tags | top spec section |
|---|---|---|---|---|---|---|
| S01 | yes | yes | 15/15 | 15/15 | OTHER (h1, citation), SEMANTIC (h2, "ends normally"); neither affects a D-item | HITL → What happens (no FALLBACK → "Execution ends, as with STOP") |
| S02 | yes | yes | 12/12 | 12/12 | OTHER (h3, citation); does not affect a D-item | Execution rule 5 |
| S03 | yes | yes | 9/9 | 9/9 | OTHER (h2, V6 misstated); does not affect a D-item | Validity rules V6 |
| S04 | yes | yes | 15/15 | 15/15 | — | — |
| S05 | no | no | 11/12 | 9/12 | SYNTAX ×4 (s1, h1, h2, h3: V6 not reported for A) | Validity rules V6; Executing a program, step 1 ("Report each broken rule by its number") |

```
PART SUMMARY
scenarios: 5
pass_s: 4/5   pass_h: 4/5
d_items_s: 62/63   d_items_h: 60/63
danger_s: 0   danger_h: 0
```
