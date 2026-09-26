# runtime

The axiom package (ADR-0021). Install it for development with `pip install -e .` from the repository root, or run it in place with `PYTHONPATH=runtime python3 -m axiom`.

| Package | State | Contents |
|---|---|---|
| `axiom.dsl` | built (M1) | lexer, AST, parser, symbol table and the validity rules V1–V12; the facade `axiom.dsl.check()` |
| `axiom.cli` | built (M1) | `axiom check FILE…` and `axiom check --md FILE…` |
| `axiom.entities` | M2 | loading, binding and precondition evaluation; grows from `lab/tools/entitycheck.py` |
| `axiom.interpreter` | M3 | a stateless step engine; state lives in the target project's `.axiom/` |
| `axiom.mcp` | M4 | the MCP server; content is requested by name and paths are relative to the target project |

## `axiom.dsl` layers

`tokens` → `lexer` (INDENT/DEDENT, positions) → `parser` (recursive descent, panic-mode recovery per line) → `nodes` (frozen dataclass AST) → `symbols` → `rules` (one `Rule` class per V-rule, in a registry). Malformed input never raises: the lexer and parser record `SyntaxIssue`s, and the rules turn them and every other violation into `Diagnostic`s.
