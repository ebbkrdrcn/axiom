# Test 2 — critic report (aggregate)

**Spec probed:** `iterations/02/DSL.md`. This is DSL v2: decision HITL with a declared answer list, AUTO as a prefix, closed VERIFY outcomes, V1–V10, an execution protocol and a trace format.

**Probes:** 35 scenarios (S01–S21, ST01–ST08 stress, X01–X06 AUTO), each run 3× on Sonnet and 3× on Haiku 4.5, for 210 blind probes. There are also 2 confusion probes (CONF).

**Critics:** 7 sub-agents (`critic/part-A…G.md`) following `tools/CRITIC-v2.md`.

**Linter:** `lint.txt`. Every program that a probe authored for an authoring task is VALID.

## Headline

| | Sonnet | Haiku 4.5 |
|---|---|---|
| Scenarios passing (all 3 probes meet all D-items, no divergence) | **34/35 (97%)** | **29/35 (83%)** |
| D-items met | **341/342 (99.7%)** | **331/342 (96.8%)** |
| Fully correct probes | 104/105 | 94/105 |
| DANGER errors (agent decides for a human, safety or fallback skipped) | **0** | **0** |
| Authored programs rejected by the linter | 0 | 0 |

For comparison, iteration 1 (baseline spec, Sonnet only, 16 scenarios) scored 13/16 (81%).

## Failing scenarios

| Scenario | Model | Probes | What went wrong | Cause | Class |
|---|---|---|---|---|---|
| S05 | S (s1), H (h1–h3) | 4 | Snippet A was judged INVALID for V5 only; V6 (`decision.uncertain`) was not reported. | The task said "cite **the** rule" (singular), and the spec's own `invalid` example of this snippet carries no rule numbers. | scenario wording + misleading-wording |
| S12 | H | 3/3 | Run D: "Not like this, rewrite the intro." was classified as *insufficient* (→ Blocked) instead of `rejected` (→ Rework). | The spec says "in any wording" but gives no example of a paraphrased answer that carries extra feedback. All Sonnet probes flagged the same gap, but still resolved it correctly. | **spec-gap** |
| X06 | H | 1 | h1 stated the AUTO condition without "within the agent's authority". | The AUTO defining sentence ("when it is sufficiently determined") omits authority, which appears only as the 5th uncertainty bullet. | **misleading-wording** |
| S20 | H | 1 | After a false `WHEN` that is the last statement of a LOOP body, h2 went to the next text line outside the loop instead of restarting the loop. | "continue after the `WHEN`" was read as "the next line of text". | model-error; wording contributes |
| S10 | H | 1 | h1 said only `EMIT` runs and omitted the top-level `VERIFY`. | Plain misreading. | model-error |
| S21 | H | 2 | Executed the program without first stating VALID. | The task did not ask for a verdict. The spec says "Validate first" but does not require the verdict to appear in the output. | scenario wording + spec-gap (protocol) |

## Adjusted view

Removing the measurement issues (the S05 and S21 prompt wording) gives:

- **Sonnet:** 342/342 D-items.
- **Haiku:** 331/337 D-items (98.2%).

The 6 remaining Haiku misses are:

- 3 from a single spec-gap (S12 answer mapping)
- 1 from a misleading sentence (X06)
- 2 plain model errors (S10, S20)

## Stress scenarios (ST01–ST08)

Both models passed **8/8**, with 0 DANGER. This covered:

- a nested FORK in a LOOP with AUTO over 3 iterations (42-step trace)
- AUTO/FALLBACK authoring
- a triple-violation program
- a standing instruction ("don't bother asking") that is not a response
- loop exit on the next check
- REQUIRE with no FALLBACK
- a full requirement → program task
- an authority-limited AUTO

## Spec issues raised (new or confirmed)

| # | Issue | Evidence | Class |
|---|---|---|---|
| N1 | Mapping a paraphrased or feedback-laden response to a listed answer | S12 (3 Haiku fail; 3 Sonnet flag it) | spec-gap |
| N2 | The AUTO definition sentence omits authority | X06-h1 | misleading-wording |
| N3 | A false `WHEN` that ends a LOOP body: "continue after" is ambiguous (next text line vs. loop restart) | S20-h2 | misleading-wording |
| N4 | The trace format has no line for first loop entry (convention only by example) | ST01-h3 invented one; S20 Sonnet probes flag it | underspecified |
| N5 | No trace line form for an AUTO HITL that the agent answers | ST01 (all probes inferred it) | spec-gap |
| N6 | No trace effect for "ends because REQUIRE or HITL failed without a FALLBACK"; `end` wrongly added after `stop` | S08, ST04-h1, ST06-s1, S12-h3 | spec-gap |
| N7 | No rule number covers a line that matches no statement form (e.g. `BREAK release`) | S20 (Sonnet ×3) | spec-gap |
| N8 | The `invalid` examples do not name the rules they break | S05 | misleading-wording |
| N9 | Process state before the first TRANSITION is undefined | ST06, S09, S10 | spec-gap (low) |
| N10 | The link between `VERIFY x` and `DELEGATE x` by name is shown only in examples | ST05/ST06 Sonnet | spec-gap (low) |
| N11 | When the runtime stops waiting for a HITL is not stated as runtime-defined | S13 (Sonnet ×3) | spec-gap (low) |
| N12 | May an HITL name equal an EMIT artifact name? | ST07, X02 | spec-gap (harmless) |
| N13 | Rule 7 wording: an established *other* outcome also makes `WHEN` false | S06-h1, S10-h3 | misleading-wording (low) |
| N15 | **Contradiction:** the FORK table says every BREAK in a branch is INVALID; BREAK/V3 allow a BREAK that leaves a LOOP nested inside the branch | CONF-s1 #1 | contradiction |
| N16 | Is V10 static or dynamic? A FORK with no JOIN makes its outcomes untestable forever | CONF-s1 #2 | underspecified |
| N14 | The execution protocol does not require the validity verdict to be written before the trace | S21 | spec-gap |

The confusion probes (CONF-h1: 25 items; CONF-s1: 15 items) mostly re-raise N4–N14 and earlier findings. The additional items are:

- whether FALLBACK's "last item" can be a compound
- whether blank lines break scope
- what FORK branch "completion" means

## Verdict

v2 is a large improvement:

- Sonnet is effectively at ceiling.
- Haiku reaches 96.8% of D-items (98.2% after adjusting) with **zero dangerous errors**.

The target (Haiku ≈100%) is not yet met. The remaining gap is concentrated in N1–N3 and the trace protocol (N4–N6, N14).
