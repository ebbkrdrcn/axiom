# runtime

The axiom package (ADR-0021). Install it for development with `pip install -e .` from the repository root, or run it in place with `PYTHONPATH=runtime python3 -m axiom`.

| Package | State | Contents |
|---|---|---|
| `axiom.dsl` | built (M1) | lexer, AST, parser, symbol table and the validity rules V1–V12; the facade `axiom.dsl.check()` |
| `axiom.cli` | built (M1, M2) | `axiom check [--md] FILE…`, `axiom entities check [DOCS]`, `axiom index [--check] [DOCS]` |
| `axiom.entities` | M2 (TASK-0019 built; preconditions in TASK-0020) | type contracts, repository port, loading, structural validity, relations, binding resolution, index generator |
| `axiom.interpreter` | M3 | a stateless step engine; state lives in the target project's `.axiom/` |
| `axiom.mcp` | M4 | the MCP server; content is requested by name and paths are relative to the target project |

## `axiom.dsl` layers

`tokens` → `lexer` (INDENT/DEDENT, positions) → `parser` (recursive descent, panic-mode recovery per line) → `nodes` (frozen dataclass AST) → `symbols` → `rules` (one `Rule` class per V-rule, in a registry). Malformed input never raises: the lexer and parser record `SyntaxIssue`s, and the rules turn them and every other violation into `Diagnostic`s.

## `axiom.entities` layers

`store` (the `EntityStore` port; `FileSystemStore` and `MemoryStore` adapters; paths relative to the project root) → `contracts` (an `EntityType` per `rules/types/<type>/`, with `formats` as field-format strategies) → `model` (`Entity`, with its content hash) → `validity` (structural problems) → `corpus` (every entity of `docs/`, identity counts, relations) → `binding` (resolution) and `index` (the `_index.md` generator). `Project` is the facade.
