# DSL status report (before Test 2)

## 1. The spec (`dsl.md`) in numbers

| Metric | Baseline (it01 input) | Now (after it01 edits) |
|---|---|---|
| Lines | 442 | 660 |
| Words | 1,187 | 3,010 |
| Approximate tokens | ~1.6k | ~4.1k |
| Code blocks | 29 | 35 |
| Tables | 0 | 2 (statement forms, meaning of `→`) |
| Explicit rule bullets | 13 | 49 |
| Invalid / counter-examples | 1 | 5 |
| Formal grammar (EBNF) | none | yes |
| AUTO syntax | **none** | **none** in `dsl.md` (tested only in the experiment copies) |

## 2. Test history

| Test | Probes | Pass rate | D-item accuracy | Divergent scenarios | Dangerous errors |
|---|---|---|---|---|---|
| Iteration 1: baseline spec, 16 scenarios, sonnet | 48 + 2 | 13/16 (81%) | 100% (every miss was a divergence) | 3 (S01 AUTO, S09 outcome names, S11 BREAK×FORK) | not measured |
| AUTO experiment: 4 variants × 6 scenarios, sonnet | 72 + 4 | 24/24 (100%) | 264/264 | 0 | 0 |

The spec after iteration 1 has **not been re-tested yet** (no regression run).

## 3. Findings

35 findings, F-01…F-35:

| Status | Count |
|---|---|
| fixed (it01) | 19 |
| waiting on a decision (DP-1…DP-8, including the open items that depend on them) | 14 |
| open (wording) | 1 |
| wontfix (outside the DSL's remit) | 1 |

## 4. Corpus

- **S01–S21:** 21 scenarios. S17–S21 were added after iteration 1 and have not run yet.
- **X01–X06:** 6 AUTO scenarios.
