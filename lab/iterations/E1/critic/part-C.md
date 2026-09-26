# Critic E1 — Part C (E11, E12)

Grader note: syntax validity (E11 D1) is taken from `lint.txt`, which reports every E11 block as VALID. The entity rules were checked against `ENTITY.md` and `fixture/docs/types/task/definition.md`. TASK-0100 starts as `InProgress` with `adr: ADR-0100`, and TASK-0102 starts as `Todo`. The full text of `DSL.md` could not be re-read in this session (a tool permission was denied). Rule wording for V11 and V12 is taken from ENTITY.md (Binding Rules and Invalid Usage) and from the V-rule text that the probes quote, which agrees across all probes.

## E11

Each program's entity status was traced from `InProgress`:
- rejected path: `InProgress → Debugging` (verified: rejected), then DELEGATE diagnosis, then `Debugging → InProgress` (none). Every probe has these steps in this order.
- accepted path: `InProgress → Review` (verified: accepted).
- HITL path: `Review → Done` inside `WHEN done.approved` and `Review → InProgress` inside `WHEN done.rejected`.

Every TRANSITION in every probe follows a transition that the Task Definition declares from the status the task has at that point. No probe puts AUTO on the done HITL.

| Probe | D1 lint | D2 bindings | D3 LOOP+VERIFY+FALLBACK Blocked/STOP | D4 rejected order | D5 Review then BREAK | D6 HITL no AUTO, WHENs |
|---|---|---|---|---|---|---|
| s1 | met | met | met | met | met: `WHEN t1.accepted → TRANSITION t1 "Review" → BREAK` | met |
| s2 | met | met | met | met | **not met**: `WHEN t1.accepted → BREAK`; `TRANSITION t1 "Review"` comes after the loop | met |
| h1 | met | met | met | met | **not met**: `→ BREAK` only; `TRANSITION t1 "Review"` comes after the loop | met |
| h2 | met | met | met | met | met: `→ TRANSITION t1 "Review"` `→ BREAK` | met |
| h3 | met | met (`t:Task`, `a:ADR = t.adr`) | met | met | met: `→ TRANSITION t "Review"` `→ BREAK` | met |
| h4 | met | met | met | met | **not met**: Review comes after the loop | met |
| h5 | met | met | met | met | **not met**: Review comes after the loop | met |

### Errors
- **s2, h1, h4, h5: D5 not met (OTHER, model-error, minor).** These probes move `TRANSITION <task> "Review"` out of the `WHEN t1.accepted` flow and put it after `LOOP`, so BREAK runs before the Review transition. The expected order is TRANSITION "Review" and then BREAK, as in ENTITY.md › Example › Process (`WHEN t1.accepted → TRANSITION t1 "Review" → BREAK`) and Interpretation step 5 ("writes `status: Review` to the file, and the loop ends"). No execution error follows. The loop has only one exit that continues execution, the BREAK under `t1.accepted`, and the FALLBACK path ends in STOP. So the post-loop TRANSITION runs only when the most recent `VERIFY t1` established `accepted`, and `verified: accepted` holds. There is no DANGER.
- Divergence: within the Sonnet pair (s1 places Review inside the WHEN, s2 places it after the loop) and within the Haiku set (h2 and h3 inside, h1, h4 and h5 after).

### Observations (not scored)
- **h1 and h3 add an unrequested `FALLBACK` on `HITL:done` that runs `TRANSITION t "InProgress"` and then STOP.** `Review → InProgress` (none) is declared, so the transition is valid. However, it changes the entity's status when the human does not answer, and the requirement does not ask for this. It is not tagged DANGER because the Definition permits the transition and the requirement does not forbid it. It is still a behaviour that was invented.
- h4's "Validation Summary" says "FALLBACK ends with STOP" and "No duplicate names". Both claims are correct.

### Scenario issues
- D5 is stricter than the requirement's semantics: the post-loop placement behaves the same way. It is kept as written because the literal order of statements is part of the check.

Verdict: PASS-S **no** (s2 D5). PASS-H **no** (h1, h4, h5 D5).

## E12

| Probe | D1 A INVALID V11 | D2 B INVALID V11 (t1 unbound earlier) | D3 C VALID | D4 D INVALID V12 ×2 |
|---|---|---|---|---|
| s1 | met (indented + follows non-binding) | met | met (cites Todo→Done, runtime failure) | met (HITL:t1 and unbound t2) |
| s2 | met | met | met (Todo→Done, runtime failure) | met |
| h1 | met | met | met | met |
| h2 | met | met | met | met |
| h3 | met | met | met (Todo→Done) | met |
| h4 | met | met | met: verdict VALID. The probe miscopies the snippet as `TASK-0100` and reasons about InProgress→Done | met |
| h5 | met | met | met: verdict VALID. Same miscopy (`TASK-0100`, InProgress→Done) | met |

### Errors
- **h4, h5: OTHER (model-error, minor).** In Snippet C these probes quote `t1:Task = TASK-0100` instead of `TASK-0102`, so their runtime note names the wrong starting status. The verdict and the reason (an undeclared transition is an execution failure, not a validity rule: ENTITY.md › Invalid Usage › "Undeclared transition") are correct. This is not a material divergence, because every probe reaches the same verdict and cites the same rule.
- s1's summary table lists D as "V12" without "×2", but the body states both V12 violations. Counted as met.

Verdict: PASS-S **yes**. PASS-H **yes**.

## Summary table

| ID | PASS-S | PASS-H | sonnet D met | haiku D met | tags | top spec section |
|---|---|---|---|---|---|---|
| E11 | no | no | 11/12 | 27/30 | OTHER×4 (D5 Review placed after the loop) | ENTITY.md › Example › Process / Interpretation step 5 |
| E12 | yes | yes | 8/8 | 20/20 | OTHER×2 (h4, h5 miscopied snippet C identity, not scored) | DSL.md V11/V12; ENTITY.md › Invalid Usage |

```
PART SUMMARY
scenarios: 2
pass_s: 1/2   pass_h: 1/2
d_items_s: 19/20   d_items_h: 47/50
danger_s: 0   danger_h: 0
```
