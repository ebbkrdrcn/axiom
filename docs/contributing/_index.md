# contributing

Conventions that every contribution follows: how work is done. Each convention names how compliance is checked, either mechanically or by review. An independent reviewer checks a change against the Active conventions in its scope.

<!-- axiom:generated:start -->
_Generated from the entities in this directory. Do not edit by hand._

| ID | Title | Status | Scope | Check | Adr |
|---|---|---|---|---|---|
| [CONV-0001](CONV-0001.md) | The runtime core uses only the Python standard library | Proposed | runtime/ | review | ADR-0021 |
| [CONV-0002](CONV-0002.md) | All code under `runtime/` passes `mypy --strict` | Proposed | runtime/ | mechanical | ADR-0021 |
| [CONV-0003](CONV-0003.md) | No module holds mutable global state | Proposed | runtime/ | review | ADR-0021 |
| [CONV-0004](CONV-0004.md) | Every runtime package has its own test directory | Proposed | runtime/, tests/ | mechanical | ADR-0021 |
| [CONV-0005](CONV-0005.md) | Checks collect diagnostics and return them instead of raising exceptions | Proposed | runtime/axiom/dsl/, runtime/axiom/entities/ | review | ADR-0021 |
| [CONV-0006](CONV-0006.md) | AST nodes are frozen dataclasses that carry their source position | Proposed | runtime/axiom/dsl/ | review | ADR-0021 |
| [CONV-0007](CONV-0007.md) | Each validity rule is its own `Rule` class | Proposed | runtime/axiom/dsl/ | review | ADR-0021 |
| [CONV-0008](CONV-0008.md) | File paths about a project are relative to its root | Proposed | rules/, runtime/ | review | ADR-0021 |
| [CONV-0009](CONV-0009.md) | Entity files and `_index.md` files change only through axiom's entity operations | Proposed | docs/ | mechanical | ADR-0021 |
| [CONV-0010](CONV-0010.md) | Commit messages start with a short imperative summary line | Proposed | all | review |  |
| [CONV-0011](CONV-0011.md) | A Task moves to Done only after an independent review by an agent that did not do the work | Proposed | docs/tasks/ | review | ADR-0021 |
| [CONV-0012](CONV-0012.md) | The test suite passes before a change is merged to `main` | Proposed | runtime/, tests/ | mechanical | ADR-0021 |
<!-- axiom:generated:end -->
