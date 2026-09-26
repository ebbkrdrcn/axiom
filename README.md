# axiom

Intent-driven software development with agents. A small human team (architect, security, DevOps) and business intent. Agents do the rest under enforced, auditable protocols.

Axiom is a stateless **rulebook and interpreter** (ADR-0021).

- The work happens in a target project.
- The project's `docs/` is its knowledge.
- Axiom makes execution deterministic.

| Directory | Contents |
|---|---|
| [`VISION.md`](VISION.md) | the vision |
| [`spec/`](spec/) | the DSL (`dsl.md`) and the Entity Model (`entity-model.md`) |
| [`rules/`](rules/) | entity types, protocols and actor definitions: the source of truth |
| [`runtime/`](runtime/) | the interpreter, MCP server and CLI (not built yet) |
| [`templates/`](templates/) | the `AGENT.md` template and the `docs/` skeleton (not built yet) |
| [`tests/`](tests/) | runtime tests (not built yet) |
| [`lab/`](lab/) | the test corpus, tools, findings, [status](lab/STATUS.md) and [next steps](lab/NEXT.md) |
| [`docs/`](docs/) | axiom's own ADRs and Tasks, used to develop axiom |
