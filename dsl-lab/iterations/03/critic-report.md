# Test 3 — critic report (partial)

**Spec probed:** `iterations/03/DSL.md` (DSL v3) with `iterations/03/ENTITY.md`.

**What ran:**
- 163 of 366 planned probes. The run was stopped on the owner's request.
- Graded: E01–E12, N01–N10 and S01. That is 23 scenarios, each with 5 Haiku 4.5 probes and 2 Sonnet probes (S01 has 1 Sonnet probe).
- Not run: S02 (partial only), S03–S21, ST01–ST08, X01–X06 and CONF.

**Critics:** 5 critics, `critic/part-A…E.md`, following `tools/CRITIC-E.md`.

**Linter:** `lint.txt`. All 23 programs written by probes are VALID.

## Headline

| | Sonnet | Haiku 4.5 |
|---|---|---|
| Scenarios passing | **23/23 (100%)** | **16/23 (70%)** |
| D-items met | **215/215 (100%)** | **535/550 (97.3%)** |
| DANGER | 0 | **3** (E03-h2, N06-h4, N06-h5) |
| Programs rejected by the linter | 0 | 0 |

Entity scenarios only (E01–E12), compared with E1:

| | E1 (DSL v2) | Test 3 (DSL v3) |
|---|---|---|
| Sonnet scenarios passing | 11/12 | 12/12 |
| Haiku scenarios passing | 8/12 | 9/12 |
| Haiku D-items met | 96.0% | 97.8% (269/275) |
| DANGER | 1 | 1 |

## Haiku failures

| Scenario | Probe | What went wrong | Class | Proposed fix |
|---|---|---|---|---|
| E03 | h2 | Bound one of two files that declare the same id (**DANGER**, the same error as in E1). | model-error; the v3 rule is still not applied | Make Binding procedural: "List every file whose `id` equals the identity. Count them. If the count is not exactly 1, the binding is not satisfied." |
| N06 | h4, h5 | After DELEGATE rewrote the Description, still treated `verified: accepted` as holding and moved TASK-0100 to Review (**DANGER** ×2). | model-error on a rule that is stated only once | Make the precondition check procedural: "Before a TRANSITION with `verified:`, list every statement since that VERIFY that changed this entity. If the list is not empty, the precondition does not hold." Also add an example. |
| E11 | h2 | Authoring: added a FALLBACK to `HITL:done` that moves the task to InProgress on a non-answer. This treats a non-answer as a rejection (borderline DANGER). | authoring gap | Authoring rule: "A FALLBACK does only what the requirement says to do on failure. It never transitions an entity and never stands in for a human answer." |
| N09, S01 | h5 | Authoring: added FALLBACKs the requirement did not ask for, so the final state differs from the other probes. | authoring gap | Same authoring rule as E11. |
| E06 | h3 | Claimed TASK-0102 has no Acceptance Criteria; it does (INVENT). | model-error | none (reading error) |
| N05 | h4 | One mistake in classifying the response (D1). | model-error | — |

## What held on every probe

- A `human:` precondition is never satisfied by AUTO (E07).
- A HITL question that lacks the entity identity makes the TRANSITION fail (N07, 7/7).
- An instruction embedded in a response is not treated as an answer (N03, 7/7).
- Paraphrased responses are mapped to answers correctly (N02, 7/7). This is fixed since Test 2's S12.
- The FORK→LOOP→BREAK scope is followed (N01).
- Nested loops and their trace counts are correct (N08).
- The long entity program ends with TASK-0100 Done (N04).
- The validity snippets are graded correctly (E12, N10).

## Verdict

- Sonnet is at ceiling on this harder set.
- Haiku is at 97.3% of D-items, but produced 3 DANGER errors, all from two rules that are stated declaratively and not as steps:
  - binding identity;
  - stale `verified:`.
- A third pattern is that Haiku adds FALLBACKs nobody asked for when authoring (3 probes).

The next spec change (v4) should make these three rules procedural.
