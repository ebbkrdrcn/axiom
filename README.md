# axiom

Intent-driven software development with agents. A small human team (architect, security, DevOps) and business intent. Agents do the rest under enforced, auditable protocols.

Axiom is a stateless **rulebook and interpreter** (ADR-0021).

- The work happens in a target project.
- The project's `docs/` is its knowledge.
- Axiom makes execution deterministic.

| Directory | Contents |
|---|---|
| [`VISION.md`](VISION.md) | the vision |
| [`ROADMAP.md`](ROADMAP.md) | points to the roadmap: Milestone entities in `docs/roadmap/` |
| [`CONTRIBUTING.md`](CONTRIBUTING.md) | points to the conventions: Convention entities in `docs/contributing/` |
| [`spec/`](spec/) | the DSL (`dsl.md`) and the Entity Model (`entity-model.md`) |
| [`rules/`](rules/) | entity types, protocols and actor definitions: the source of truth |
| [`runtime/`](runtime/) | the interpreter, MCP server and CLI (not built yet) |
| [`templates/`](templates/) | the `AGENT.md` template and the `docs/` skeleton (not built yet) |
| [`tests/`](tests/) | runtime tests (not built yet) |
| [`lab/`](lab/) | the test corpus, tools, findings, [status](lab/STATUS.md) and [next steps](lab/NEXT.md) |
| [`docs/`](docs/_index.md) | axiom's own knowledge: ADRs, Tasks, conventions and the roadmap. Start at `docs/_index.md` |
