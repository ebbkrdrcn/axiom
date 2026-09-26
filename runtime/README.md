# runtime

The axiom interpreter as a Python package (ADR-0021). It will contain:

- `parser`: grows from `lab/tools/dslcheck.py`;
- `interpreter`: a stateless step engine. State lives in the target project's `.axiom/`;
- `entities`: loading, binding and precondition evaluation. Grows from `lab/tools/entitycheck.py`;
- `mcp`: the MCP server. Content is requested by name, and paths are relative to the target project;
- `cli`: `axiom project start <path>`.

Not built yet.
