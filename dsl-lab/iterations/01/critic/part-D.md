# Critic report — iteration 01 — part D

## S16

### Verdict
**PASS** — all 3 probes meet D1–D3. They agree on every structural choice: ordering, which WHEN runs, immediate BREAK, EMIT after the loop, natural termination, and final state "Review".

### D-item table

| Probe | D1 (iter 1: failed → skip passed-WHEN → TRANSITION "Debugging" → DELEGATE diagnosis → repeat) | D2 (iter 2: passed → TRANSITION "Review" → BREAK; failed-WHEN not evaluated) | D3 (EMIT once after loop; ends; final "Review") |
|---|---|---|---|
| p1 | met: steps 1–6, "execution returns to the top of the `LOOP:tdd` scope" | met: steps 7–11, "`WHEN tests.failed` ... is not evaluated for this iteration" | met: steps 12–13, "Final process state **`Review`**" |
| p2 | met: steps 1–6, "the loop repeats from the top of its body" | met: steps 7–11, "`WHEN tests.failed`, is not reached/evaluated in this pass" | met: steps 12–13, "**`Review`**" |
| p3 | met: steps 1–6, "the loop continues and the body is re-executed" | met: steps 7–11, "`WHEN tests.failed` ... is **not** evaluated in this iteration" | met: steps 13–14, "**`Review`**" |

### Divergence
None material. All three probes:
- re-run the whole body, including both DELEGATEs, on iteration 2;
- check the WHENs in declaration order, and exactly one flow runs in each iteration;
- treat BREAK as an immediate exit, so the sibling WHEN is skipped;
- run EMIT exactly once after the loop, and end execution when no statements remain (no STOP needed);
- report the final state as `Review`, which supersedes `Debugging`.

The wording of the assumption lists differs, but the conclusions are the same.

### Errors
None.

| Probe | What | Section | Class |
|---|---|---|---|
| — | — | — | — |

### New issues
The probes converged, but all three had to state these same assumptions explicitly. Each one is a latent gap that could cause divergence in less clear-cut programs:
1. **Loop re-entry at end of body** (p1 A1, p2 A1, p3 A1). The spec never says that reaching the end of the body returns control to its first statement. §LOOP: "The loop continues until `BREAK`, `STOP`, or another explicit control flow terminates it." The rule is implied, not stated. `spec-gap` (minor).
2. **BREAK immediacy / remaining siblings** (p1 A4, p2 A2, p3 A3). The spec does not say that statements after the BREAK-containing flow, still inside the loop, are skipped. §BREAK: "Exits the current `LOOP`." combined with §Flow: "Statements execute in declaration order unless an explicit control construct changes the flow." This is a reasonable basis, but it is not explicit. `spec-gap` (minor).
3. **Program termination without STOP** (p2 A4, p3 A5). §STOP: "Terminates execution." Nothing says that execution ends when the statement sequence is exhausted. `spec-gap`.
4. **WHEN evaluation model: exclusive dispatch vs independent checks** (p1 A3, p2 A3, p3 A2). §WHEN: "Multiple `WHEN` constructs may describe different outcomes of the same process state." The spec does not say whether every WHEN is checked, or whether the first match excludes the rest. It also does not say whether outcomes such as `passed` and `failed` are mutually exclusive. This does not matter in S16, because only one outcome is injected, but it would matter if both conditions could hold. `underspecified-syntax` / `spec-gap`.
5. **Outcome lifetime across iterations** (p1 A2). §VERIFY: "Verification may establish outcomes that can be used by `WHEN`." The spec does not say whether an outcome persists, is overwritten by the next VERIFY, or is cleared at the start of an iteration. It would matter if a WHEN were placed before VERIFY inside a loop. `spec-gap`.
6. **Identity of re-delegated work across iterations** (p2 A6). §DELEGATE: "defines responsibility, not execution mechanics." It is unclear whether iteration 2's `DELEGATE implementation` is new work or continues the earlier work. This does not affect control flow. `spec-gap` (low impact).
7. **Unverified DELEGATE** (p1 A5, p2 A5, p3 A4). `DELEGATE diagnosis` is never verified, and its result never feeds the next iteration. All probes treat it as fire-and-forget. The spec allows this ("A delegated result *may* subsequently be evaluated"), but does not say whether a delegation must complete before the next statement runs. It is not flagged in the scenario. `spec-gap` (sync vs async DELEGATE).

### Scenario issues
- D1's "loop repeats" and D3's "execution ends" rest on rules the spec implies but never states (New issues 1 and 3). Calling them *determined* is defensible because no other reading is plausible, but the scenario should acknowledge that they are inferred.
- D2's "`WHEN tests.failed` is not evaluated" rests on BREAK being immediate (New issue 2). §BREAK and §Flow support this reasonably well, so D is acceptable.
- "U-items: none expected" is accurate for this program's outcome. Items 4, 5 and 7 remain real gaps that this baseline does not exercise.

## Summary

| Scenario | Verdict | # probes fully correct | Top section(s) implicated |
|---|---|---|---|
| S16 | PASS | 3/3 | §LOOP (end-of-body re-entry), §BREAK (immediacy), §STOP (termination without STOP), §WHEN (multi-WHEN evaluation) — all latent gaps, not errors |
