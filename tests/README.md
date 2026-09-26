# tests

Tests of the runtime, one directory per package under `runtime/axiom/` (CONV-0004). Run them with `python3 -m pytest`; `requirements-dev.txt` lists the tools.

- `tests/dsl/test_differential.py` compares `axiom.dsl.check` with the reference checker `lab/tools/dslcheck.py` on every program in `spec/dsl.md`, the lab scenarios, the probe outputs and `rules/protocols/`.
- `tests/entities/test_entitycheck_parity.py` runs `axiom entities check` and `axiom index` against `lab/tools/entitycheck.py` and `indexgen.py` on mutated copies of `docs/` and the lab fixtures.
- `tests/test_stdlib_only.py` is the mechanical check of CONV-0001.

The lab's expected traces (`lab/scenarios*/`) will serve as golden tests for the interpreter (M3).
