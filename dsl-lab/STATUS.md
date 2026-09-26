# DSL status report (after Test 3)

## Where things stand

| Item | State |
|---|---|
| Spec | `dsl.md` DSL v3, and `entity-model.md` |
| Entities | Task and ADR types are in `entities/types/`. The project's own ADR-0001…0014 are Proposed. TASK-0001…0009 and 0011 are InProgress; the rest are Todo. |
| Tools | `tools/dslcheck.py` (V1–V12), `tools/entitycheck.py`, `tools/lint_outputs.py`, `tools/CRITIC-v2.md`, `tools/CRITIC-E.md` |
| Findings | F-01…F-63 in `findings.md`. F-61…F-63 are open for v4. |

## Test history

| Test | Spec | Probes | Sonnet | Haiku 4.5 | DANGER |
|---|---|---|---|---|---|
| Iteration 1 | baseline | 16 scenarios, Sonnet ×3 | 13/16 (81%) | — | not measured |
| Test 2 | v2 | 35 scenarios, 3S + 3H each | 34/35, 99.7% D-items | 29/35, 96.8% D-items | 0 |
| E1 (entities) | v2 + entities | 12 scenarios, 2S + 5H each | 11/12 | 8/12, 96.0% D-items | 1 |
| Test 3 (partial) | v3 | 23 scenarios, 2S + 5H each | **23/23, 100% D-items** | **16/23, 97.3% D-items** | 3 (Haiku) |

Test 3 covered E01–E12, N01–N10 and S01. It did not run S02–S21, ST01–ST08, X01–X06 or CONF.

## Assessment

- **Sonnet:** at ceiling on the entity scenarios and the hard set.
- **Haiku:** all three DANGER errors come from two rules that are stated declaratively and not as steps:
  - binding identity (F-61);
  - stale `verified:` (F-62).
- **Authoring:** Haiku also adds FALLBACKs that were not requested (F-63).
- **Limit of the approach:** a spec alone probably tops out at about 98–99% for Haiku. The DANGER class needs mechanical checks in tools.

## Direction (agreed 2026-09-26)

1. The target model is Sonnet. Haiku is measured only occasionally.
2. DSL v4 makes F-61, F-62 and F-63 procedural and keeps the spec short.
3. Move the critical checks into tools:
   - binding count;
   - stale `verified:`;
   - TRANSITION preconditions.
4. Keep tests small because of usage limits. Each change gets 1–2 Sonnet probes on the affected scenarios; run a full regression only occasionally.
