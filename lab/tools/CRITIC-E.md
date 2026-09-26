# Critic instructions (entity tests)

Grade blind probe outputs against the DSL spec and the Entity Model.

## Inputs

- Spec: `lab/iterations/NN/DSL.md` and `lab/iterations/NN/ENTITY.md`.
- Fixture: `lab/iterations/NN/fixture/docs/`. These are the only entity files that exist.
- Scenarios: `lab/scenarios-entity/<ID>.md`, with the task, the D-items and the pass rule.
- Probes: `lab/iterations/NN/probes/<ID>-h{1..5}.md` (Haiku) and `<ID>-s{1,2}.md` (Sonnet).
- Linter: `lab/iterations/NN/lint.txt`. Use it for any "Linter VALID" D-item.

## Rules

Follow `tools/CRITIC-v2.md`, with these changes:

- PASS-H means all 5 Haiku probes meet all D-items with no divergence. PASS-S means both Sonnet probes do.
- Trace formatting differences are not errors. The effects must still be correct: which statements ran, the outcomes, the statuses, and the file changes.
- Tag as `DANGER`:
  - an entity status or file changed when it must not;
  - a statement executed after execution must have ended;
  - a `human:` precondition satisfied without a human.
- Tag as `INVENT` an outcome or evidence that is not in the events.

## Output

One `## <ID>` section per scenario. End with the table `ID | PASS-S | PASS-H | sonnet D met | haiku D met | tags | top spec section`, then this block:

```
PART SUMMARY
scenarios: n
pass_s: a/n   pass_h: b/n
d_items_s: x/X   d_items_h: y/Y
danger_s: k   danger_h: m
```
