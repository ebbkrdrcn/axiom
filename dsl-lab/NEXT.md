# Resume note (for the next session)

Last stop: 2026-09-26. Test 3 stopped part way at the owner's request because of usage limits. Everything is merged to `main`.

## Read first

- `STATUS.md`: the current state and the agreed direction.
- `iterations/03/critic-report.md`: Test 3 results, failures and proposed fixes.
- `findings.md`: F-61…F-63 are the open items for v4.

## Vision (agreed with the owner on 2026-09-26; see ADR-0015…0017, all Proposed)

- **Single entry point.** A human intent in natural language. The human is always at the top.
- **Recursive responsibility tree.** A supervisor splits the intent into sub-tasks and creates one Actor for each. An Actor is a Role together with a Protocol (a DSL program) and a Context. Supervisors can nest, and every node is responsible for its subtree.
- **ASK replaces HITL (ADR-0016; the owner chose the name `ASK`).**
  - A question escalates upward to the first node that is authorised to answer it.
  - The answer returns down the same path.
  - `@human` marks a decision only the human may answer.
  - The precondition `human:` becomes `answered: <a> by human`.
- **Mechanical layer (ADR-0017):**
  - a harness MCP server that is the only writer of the ledger;
  - Claude Code hooks: a PreToolUse lock on `status:`, and a PostToolUse on AskUserQuestion that records answers `by human`;
  - a pre-commit guard.
- **Context (ADR-0017).** Graphify builds actor context. Decisions use only `EXTRACTED` edges. A vector DB is deferred.
- **Consequence for testing.** Actors may run on small models, so execution determinism (the Haiku DANGER errors) matters again. Revisit the "target model = Sonnet" decision with the owner.

## Open questions for the owner

1. May a node rephrase a question it passes upward? If so, the entity identity must survive.
2. Is an answer shared between identical questions from different actors?
3. How does `DELEGATE` name an Actor? Can a protocol call another protocol? Are protocols an approved library, or written per task?
4. Do actors run as Claude Code subagents or as separate sessions?

## Next steps. Report to the owner in Turkish and wait for approval before and after each test.

1. **DSL v4.** Change `dsl.md`, and `entity-model.md` if needed. Include the `HITL` → `ASK` rename (ADR-0016) once the owner approves it:
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
