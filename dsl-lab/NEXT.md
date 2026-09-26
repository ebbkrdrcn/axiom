# Resume note (for the next session)

Last stop: 2026-09-26. Test 3 stopped part way at the owner's request because of usage limits. Everything is merged to `main`.

## Read first

- `STATUS.md`: the current state and the agreed direction.
- `iterations/03/critic-report.md`: Test 3 results, failures and proposed fixes.
- `findings.md`: F-61…F-63 are the open items for v4.

## Next steps. Report to the owner in Turkish and wait for approval before and after each test.

1. **DSL v4.** Change `dsl.md`, and `entity-model.md` if needed:
   - **F-61, binding:** "List every file whose `id` equals the identity. Count them. If the count is not exactly 1, the binding is not satisfied."
   - **F-62, `verified:`:** "Before a TRANSITION with `verified:`, list every statement since that VERIFY that changed this entity. If the list is not empty, the precondition does not hold." Add an example.
   - **F-63, authoring:** "A FALLBACK does only what the requirement says to do on failure. It never transitions an entity and never stands in for a human answer."
   - Keep the spec short and do not grow it. Check it with `python3 tools/dslcheck.py --md ../dsl.md`.
2. **Small validation test (Sonnet only).** Run E03, N06, E11, N09 and S01 with 2 Sonnet probes each: 10 probes and 1 critic, 11 subagents in total. Build inputs the same way as in `iterations/03`: DSL.md + ENTITY.md + fixture, with the task at the end.
3. **Optional wider regression.** Run the 34 scenarios that have not run yet (S02–S21, ST01–ST08, X01–X06) with 1 Sonnet probe each: 34 probes and 2 critics.
4. **Tools.** Add mechanical checks for binding count, stale `verified:` and TRANSITION preconditions, for example an extension of `tools/entitycheck.py`.
5. **Docs.** Once verified, TASK-0001…0009 and 0011 can move to Review. Done needs human approval. The ADRs await owner approval.

## Practical notes

- **Probe prompt:** "Read the file <in>.md … using only that file's contents … write your answer to <out>.md … reply: done". Use model `haiku` or `sonnet`, in the background.
- **Concurrency:** about 20 concurrent subagents at most. Usage limits have been hit twice, so keep batches small.
- **Critic:** follow `tools/CRITIC-E.md`, with one output file per part in `iterations/NN/critic/`.
