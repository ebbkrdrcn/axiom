# Critic report — iteration 01, part A (S01–S05)

Spec: `dsl-lab/iterations/01/DSL.md`. Probes: `dsl-lab/iterations/01/probes/Sxx-p{1,2,3}.md`.

---

## S01

**Verdict: FAIL.** All D-items met, but the probes disagree on U1 (the AUTO form) and U2 (outcome names), so the convergence condition fails.

### D-item table

| Probe | D1 DELEGATE→VERIFY | D2 `HITL("Merge this change?")` | D3 AUTO used | D4 AUTO has no WHEN/→, no uncertainty cond. | D5 two WHEN → Merged/Rework |
|---|---|---|---|---|---|
| p1 | met: `DELEGATE implementation` / `VERIFY implementation` | met | met: `HITL(...)` + `→ AUTO` | met: AUTO is a leaf (the `→` belongs to HITL, not AUTO); no `.uncertain` | met: `WHEN merge.approved → TRANSITION "Merged"`, `WHEN merge.rejected → TRANSITION "Rework"` |
| p2 | met | met | met: `AUTO merge-decision` line before HITL | met | met: `merge-decision.merge` / `merge-decision.no-merge` |
| p3 | met | met | met: bare `AUTO` line before HITL | met | met: `merge.approved` / `merge.rejected` |

### Divergence

- **U1 AUTO syntax and binding (AMBIGUITY):** there are three different forms.
  - p1 attaches AUTO under the HITL with an arrow, copying the FALLBACK form: `HITL("…")` / `  → AUTO`. AUTO comes after the HITL.
  - p2 puts a statement with an argument, `AUTO merge-decision`, on the line before the HITL.
  - p3 puts a bare `AUTO` on the line before the HITL.
  - The probes also disagree on order (AUTO before or after the HITL) and on whether AUTO takes an argument.
- **U2 outcome names (AMBIGUITY):**
  - Two probes use `merge.approved/rejected` (p1, p3). p2 uses `merge-decision.merge/no-merge`.
  - The subject also differs: `merge` in p1 and p3, `merge-decision` in p2.
- **Other structure:** all three emit no FALLBACK, no STOP after the transitions and no branch on VERIFY's outcome, so these do not diverge.

### Errors

| Probe | What | Section | Class |
|---|---|---|---|
| p1, p2, p3 | Each probe invents its own AUTO form and its own way of binding AUTO to the HITL | `### AUTO`: the section has no syntax block at all (every other construct has one), only "`AUTO` is not a control-flow container." `### HITL`: "…unless the surrounding definition explicitly permits automatic resolution through `AUTO`" does not say what a "surrounding definition" is | spec-gap |
| p1, p2, p3 | Different condition names for the HITL/AUTO decision outcome | `### VERIFY`: "Verification may establish outcomes that can be used by `WHEN`" (only VERIFY is said to produce outcomes). `### HITL`: "The human response may determine the subsequent flow" (no mechanism, no names) | spec-gap |

### New issues

1. **Nothing says HITL or AUTO produces outcomes that WHEN can use.** This is separate from F-03's naming question: the spec never says that a decision made by HITL or AUTO can be referenced by WHEN at all (p1 assumption 3, p2 assumption 3). Section: `### HITL`: "The human response may determine the subsequent flow."
2. **Scope of a standalone `AUTO` statement.** In p2 and p3's form it is undefined whether AUTO applies to the next HITL only or to everything after it. Section: `### AUTO`.
3. **A VERIFY with no WHEN.** It is unclear whether a VERIFY that no WHEN follows gates the flow. In all three probes, flow goes on to the merge decision even if verification rejects (p3 assumption 4). Section: `### VERIFY` and `## Flow`.

### Scenario issues

None. U1 and U2 are underdetermined, as the scenario predicts.

---

## S02

**Verdict: PASS.** All D-items met in all probes, and all use the same outcome names (`implementation.accepted/rejected`).

### D-item table

| Probe | D1 `LOOP:<name>` + indented body | D2 DELEGATE→VERIFY→WHENs | D3 BREAK in accept-WHEN | D4 `DELEGATE correction` in reject-WHEN | D5 `EMIT source-code` after loop, outer indent |
|---|---|---|---|---|---|
| p1 | met: `LOOP:implementation-cycle` | met | met: `WHEN implementation.accepted → BREAK` | met | met |
| p2 | met | met | met | met | met |
| p3 | met | met | met | met | met |

### Divergence

None. The three DSL blocks are byte-identical, and all name the loop `implementation-cycle`. U1 converged on `.accepted/.rejected`. The canonical answer's loop name, `implementation`, differs from the probes' name, but that is not a D-item.

### Errors

None.

### New issues

1. **Implicit loop continuation.** "Repeat from the start" relies on the inference that when the loop body ends, execution goes back to the top. All three probes flagged this as an assumption (p1 #1, p2 #2, p3 #4). Section: `### LOOP`: "The loop continues until `BREAK`, `STOP`…" says the loop continues but not how. Class: spec-gap (minor).
2. **Identity of results across iterations.** After `DELEGATE correction`, the next iteration runs `DELEGATE implementation` again from scratch. The spec does not say how a correction feeds back into `implementation` (p2 #3, p3 #5). Section: `### DELEGATE` / `## Identifier`. Class: spec-gap.

### Scenario issues

- U1 is effectively determined for this task. The `### VERIFY` example is literally `VERIFY implementation` / `WHEN implementation.accepted` / `WHEN implementation.rejected`, which uses the same identifier and the same accept/reject wording as the requirement. So convergence here does not show that F-03 is resolved. A task with a different subject, or with "pass/fail" wording, would test F-03 properly.

---

## S03

**Verdict: PASS.** All D-items met in all probes, with no structural divergence.

### D-item table

| Probe | D1 one FORK, two `→` | D2 VERIFY nested under DELEGATE | D3 JOIN at FORK indent after FORK | D4 `TRANSITION "Release"` after JOIN |
|---|---|---|---|---|
| p1 | met | met: `→ DELEGATE security-review` / `      VERIFY security-review` | met | met |
| p2 | met | met | met | met |
| p3 | met | met | met | met |

### Divergence

None material. The probes differ only in blank lines. All nest the statements at column 6, level with the text after `→ ` (U1 converged). All use the identifiers `security-review` / `performance-review`, and all proceed to Release whatever the VERIFY outcome.

### Errors

None.

### New issues

1. **Meaning of "required" in JOIN is undefined.** `### JOIN` says "all required forked flows have completed", but nothing defines which flows are "required" or how to mark one (p2 flagged the lack of partial-join syntax). Class: misleading-wording.
2. **VERIFY rejection inside a branch.** The spec does not say whether a rejected VERIFY makes a branch "fail", or how JOIN treats that branch. All probes chose to continue unconditionally (p2: "'have finished' (not 'have succeeded')"). Section: `### JOIN` / `### VERIFY`. Class: spec-gap.

### Scenario issues

- D3 ("JOIN … at the FORK's indentation") is only implicitly determined. The FORK/JOIN examples are shown in separate blocks, and p3 notes the spec "does not require any particular indentation relative to `FORK`." The requirement can be derived from `## Scope` together with `## Forked Flow` ("belong to that branch until the branch scope ends"), so keeping it as a D-item is acceptable.

---

## S04

**Verdict: PASS.** All D-items met, and all probes use the same fallback-flow form (though not the canonical one; see Scenario issues).

### D-item table

| Probe | D1 REQUIRE first | D2 HITL string | D3 `→ FALLBACK` under HITL, no WHEN | D4 TRANSITION "Blocked" then STOP | D5 DELEGATE/EMIT in normal flow | D6 no AUTO |
|---|---|---|---|---|---|---|
| p1 | met | met | met | met: `→ TRANSITION "Blocked"` / `  STOP` | met | met |
| p2 | met | met | met | met | met | met |
| p3 | met | met | met | met | met | met: says explicitly that "`AUTO` is not used" |

### Divergence

None. The three DSL blocks are identical. U1 converged on **one `→` plus nested lines**:

```text
  → FALLBACK
      → TRANSITION "Blocked"
        STOP
```

All three probes derived this form from the FORK "Forked Flow" rule and labelled it an assumption (p1 #5, p2 #4, p3 last bullet).

### Errors

None against the D-items.

### New issues

1. **`→` means different things in different constructs.**
   - Under `## Conditional Flow` (WHEN), every `→` line is a sequential statement of the same flow.
   - Under `## Forked Flow` (FORK), every `→` is a separate concurrent branch.
   - FALLBACK uses `→` in both roles (`→ FALLBACK` then `→ <flow>`) and says neither.

   The canonical answer uses the WHEN reading (one `→` per statement). The probes avoided it, apparently because under the FORK reading it could mean two parallel flows. Sections: `### FALLBACK` syntax block, `## Conditional Flow`, `## Forked Flow`. Class: underspecified-syntax (see also F-04/F-11, S10).
2. **Whether the normal flow resumes after a fallback flow is undefined.** It is undefined what happens when a fallback flow does *not* end in STOP. The probes treat the post-HITL statements as the "otherwise" path only because the fallback ends in STOP (p2 #3). Section: `### FALLBACK`: "It does not mean 'execute this flow after the normal flow'." Class: spec-gap.
3. **An unsatisfiable REQUIRE has no defined behaviour** beyond "must not proceed as if satisfied" (p2 #9). Section: `### REQUIRE`. Class: spec-gap (overlaps S08).

### Scenario issues

- **U1 converged on a form different from the canonical answer.** The canonical answer uses one `→` per statement; all probes use `→` plus nested lines. The pass rule only requires the probes to agree, so this passes. But the canonical form itself is not determined by the spec, and it is arguably the less natural reading given `## Forked Flow`. The convergence came from analogy, not from spec text, so it is fragile. The scenario should either stop presenting one form as canonical or tie it to spec text once the spec defines it.

---

## S05

**Verdict: PASS.** All probes say A is INVALID and B is INVALID, citing the correct rules.

### D-item table

| Probe | D1 A INVALID (AUTO not container, uncertainty not a condition, runtime decides) | D2 B INVALID (BREAK only exits a loop; no LOOP) |
|---|---|---|
| p1 | met: quotes "`AUTO` is not a control-flow container…" and the spec's own invalid example; "the DSL runtime determines uncertainty" | met: "INVALID (as a standalone snippet)", "may only exit a loop scope" |
| p2 | met: all three points cited | met: "INVALID as a standalone snippet (assumption-dependent)" |
| p3 | met | met: "INVALID", "no valid target" |

### Divergence

- **Snippet-completeness hedge.** p1 and p2 explicitly condition B's verdict on the snippet being complete ("if … nested inside some outer `LOOP` … `BREAK` would be valid"). p3 does not hedge. The verdicts are the same, so this is not a D-item failure. It does show that the spec does not say whether a program fragment is judged standalone.
- **Consequence of B (U2):**
  - p1 says there is "no defined target and no defined effect" and it "cannot legally [be] treat[ed] as a no-op".
  - p3 says it "must be treated as a malformed/invalid statement" to be rejected, error handling undefined.
  - p2 gives no runtime consequence.

  None read it as a no-op. The difference is minor.
- **Correct replacement for A (U1):**
  - p1 gives a bare `AUTO`.
  - p3 gives a bare `AUTO` *or* `HITL(...) → FALLBACK → <flow>`.
  - p2 gives no rewrite.

  This divergence is expected (F-01).
- **Relationship between the leading `HITL` and `AUTO` in A:** all three independently flag it as undefined by the spec. They agree that it is a gap.

### Errors

| Probe | What | Section | Class |
|---|---|---|---|
| p3 | Presents FALLBACK as "the specification's suggested way to express 'fall back to a human when the automatic/expected path can't be used'". This conflates AUTO's escalation to a human with FALLBACK, which handles an unusable HITL response | `### FALLBACK`: "Defines the flow to use when an expected response is unavailable or insufficient." The name "FALLBACK" together with AUTO's "otherwise require human input" invites the conflation | misleading-wording |
| p3 | The suggested fix for B (`LOOP:review … WHEN implementation.rejected → BREAK`) is glossed as exiting "once the delegated result is no longer being rejected". The loop actually exits *on* rejection | `### BREAK` (clear) | model-error (not a D-item) |

### New issues

1. **Fragment vs. program.** The spec does not say whether validity is judged on a complete program or whether an excerpt may sit inside an unseen scope (p1, p2). Section: `## Scope`. Class: spec-gap.
2. **Validity or error model.** The spec states prohibitions ("may only exit a loop scope", "is invalid") but has no notion of static validation or runtime error. Section: `### BREAK`, `### AUTO`. Class: spec-gap (overlaps F-14).
3. **Relationship between a bare `HITL` and a following `AUTO`.** This was flagged by all three probes and is the same gap as S01's U1. Section: `### HITL` / `### AUTO`.

### Scenario issues

- U2 predicted that probes might read B as a no-op. None did, because "may only exit a loop scope" was read as a prohibition by all. The one open point is the fragment-vs-program question above. The scenario could state "each snippet is a complete program" to remove the hedge.

---

## Summary

| Scenario | Verdict | #probes fully correct | Top section(s) implicated |
|---|---|---|---|
| S01 | FAIL | 3/3 on D-items (U1/U2 diverge) | `### AUTO` (no syntax), `### HITL` ("surrounding definition … through `AUTO`"), `### VERIFY` (outcomes only from VERIFY) |
| S02 | PASS | 3/3 | `### LOOP` (implicit continuation, minor) |
| S03 | PASS | 3/3 | `### JOIN` ("required forked flows") |
| S04 | PASS | 3/3 (converged on non-canonical fallback form) | `### FALLBACK` syntax block, `## Conditional Flow` vs `## Forked Flow` (`→` meaning) |
| S05 | PASS | 3/3 | `### AUTO`, `### BREAK`, `## Scope` (fragment vs program) |
