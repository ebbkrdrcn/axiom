# Roadmap

This roadmap turns axiom into a usable tool: a stateless rulebook and interpreter. The work happens in a target project (ADR-0021).

**Working rules for every milestone:**

- It ends with a usable increment, and its decisions are recorded as ADRs and Tasks in `docs/`.
- A Task reaches Done only after an independent review by an agent that did not do the work.
- Temporary tooling stays minimal (ADR-0019). The syntax stays as it is until M6. Lab tests resume when usage limits allow.

| Milestone | Goal | Status |
|---|---|---|
| M0 | Foundations: conventions, indexes, contributing | next |
| M1 | DSL core: lexer, AST, parser, validity rules | — |
| M2 | Entity core: types, instances, bindings, preconditions, indexes | — |
| M3 | Interpreter: a stateless step engine | — |
| M4 | MCP server, CLI, `AGENT.md`, hooks | — |
| M5 | First real run: axiom develops itself | — |
| M6 | DSL v4 | — |
| Later | Lab, context, maintenance mode, central runtime | — |

## M0 — Foundations

**Delivers:**

- **The `Convention` entity type.**
  - Its contracts live in `rules/types/convention/`.
  - Its instances are `docs/contributing/CONV-NNNN.md`.
  - Its statuses are Proposed → Active → Retired.
  - Each instance names its scope, its check (`mechanical` or `review`) and its ADR.
- **The first conventions:**
  - the core uses only the standard library;
  - `mypy --strict` passes;
  - there is no global state;
  - every layer has its own tests;
  - diagnostics are collected, not raised;
  - AST nodes are frozen dataclasses;
  - a new validity rule is a new `Rule` class;
  - paths are relative to the project root;
  - entity writes go through axiom;
  - commit messages follow a set format.
- **An `_index.md` in every `docs/` directory,** produced by a temporary generator script. `entitycheck` verifies that each index matches its files.
- **A root `CONTRIBUTING.md`** that points to `docs/contributing/_index.md`.
- **TASK-0015:** replace the leftover "go_harness" and ".harness" names.

**Exit:**

- every entity and every index is valid;
- the conventions are Active;
- the independent review accepts the milestone.

## M1 — DSL core (`runtime/axiom/dsl/`)

**Delivers:**

- **The token model and the lexer.**
  - Tokens are defined as an enum with a keyword table.
  - The lexer is a scanner and generator. It produces INDENT and DEDENT tokens, and every token carries its line and column.
- **The AST.** Nodes are frozen dataclasses and carry their positions.
- **The parser.** It is a recursive-descent parser that mirrors the EBNF. It recovers in panic mode, so it reports every error in one pass.
- **Diagnostics,** using the Notification pattern. Each one carries its rule id, position, message and a fix hint.
- **A visitor base class, a symbol table, and one `Rule` class per validity rule (V1–V12),** registered in a registry.
- **A facade and a CLI.** The facade is `axiom.dsl.check()`; the CLI command is `axiom check`.

**Exit:**

- **differential test:** the new checker agrees with `lab/tools/dslcheck.py` on:
  - every example in `spec/dsl.md`;
  - every lab scenario program;
  - every probe-authored program;
- `mypy --strict` is clean;
- all tests pass.

Once the exit criteria are met, `lab/tools/dslcheck.py` stays only as the oracle for the differential test.

## M2 — Entity core (`runtime/axiom/entities/`)

**Delivers:**

- Parsing of types: Template, Definition and Representation.
- Loading of instances through a repository port. Paths are relative to the project root, and an in-memory adapter is used for tests.
- Structural validity.
- Binding resolution. It includes counting the files that declare an identity.
- Relations.
- The evaluation of preconditions, including a stale `verified:` detected by content hash.
- Checking of permitted changes.
- The index generator.

**Exit:**

- the new code replaces `lab/tools/entitycheck.py` with the same verdicts on `docs/` and on the lab fixtures;
- tests pass;
- `mypy --strict` is clean.

## M3 — Interpreter (`runtime/axiom/interpreter/`)

**Delivers:**

- **A step engine.**
  - It keeps an explicit program counter and a frame stack.
  - Its state is serialised to `.axiom/run.json` (a memento).
  - Axiom returns the next step as a command, and the agent reports the result as an event.
- **Outcomes, WHEN, LOOP, FORK and JOIN, BREAK, FALLBACK and STOP, bindings, and entity transitions,** all running through the entity core.
- **The ledger writer** (`.axiom/ledger.jsonl`).

**Exit:**

- **golden tests:** given the scripted events, the interpreter reproduces the expected traces of the lab scenarios;
- the interpreter handles the Test 3 DANGER cases (E03 and N06) correctly by construction.

## M4 — MCP, CLI, AGENT.md, hooks

**Delivers:**

- **An MCP server with these tools:**
  - get a protocol, an actor or a type, by name;
  - `start_run`, `next_step` and `report_result`;
  - `create_entity`, `update_entity` and `transition`, each of which updates the index and the ledger;
  - `rebuild_index`.
- **`axiom project start <path>`.** It leaves `AGENT.md` in the project, creates the `docs/` skeleton if it is missing, and adds `.axiom/run.json` to `.gitignore`.
- **Claude Code hooks.** A PreToolUse hook blocks direct writes to entity files, to `_index.md` files and to `status:` lines.
- The runtime pins a **stable axiom version** for execution.

**Exit:**

- a session in a scratch project runs `task-delivery` through MCP from start to finish, with scripted answers.

## M5 — First real run

**Delivers:**

- **Actor definitions** in `rules/actors/`: spec writer, developer, debugger and verifier.
- A real Task on axiom itself (for example TASK-0014) is run with `task-delivery`: axiom is the interpreter, and Claude Code subagents are the actors.
- Findings from the run, as new Tasks and ADRs.

**Exit:**

- the Task reaches Done through the protocol, with an independent verifier;
- the findings are recorded.

## M6 — DSL v4

**Delivers:**

- **`ASK` replaces `HITL`** (ADR-0016), with role targets such as `@human` and `@business`, and `answered: … by …` preconditions.
- **`DELEGATE … TO <actor>`**, with a FALLBACK.
- **Protocol parameters,** such as `t:Task = $task`.
- **The rule that extra text in an answer is context, not an outcome.**
- **F-61…F-63 move into the runtime,** and the spec keeps only the judgement rules.
- **TASK-0014:** Review → Done is split into technical verification and intent acceptance.

**Exit:**

- the parser, the interpreter and the protocols are updated;
- a small lab validation run on Sonnet passes.

## Later

- **The lab as a model qualification exam** (ADR-0019):
  - the corpus is versioned;
  - part of it is a hold-out set;
  - results form a table of model × capability.
- **Context for actors** from graphify (ADR-0017).
- **Maintenance mode** and the `Improvement` entity type (ADR-0020).
- **Human roles and routing of ASKs** (ADR-0018).
- **The central runtime:** an issue-tracker-like application, answering ASKs in a UI, and durable execution, for example with Temporal (ADR-0019).
- **The ecosystem:** deep supervisor trees, a Claude Code plugin, and A2A.
