# roadmap

The project's roadmap. Each milestone is a stage with exit criteria, and Tasks point to it through their `milestone` relation. The Tasks column shows how many of those Tasks are Done.

## Later (not yet milestones)

- The lab as a model qualification exam, with a versioned corpus, a hold-out set, and a model × capability table (ADR-0019).
- Context for actors from graphify (ADR-0017).
- Maintenance mode and the `Improvement` entity type (ADR-0020).
- Human roles and the routing of ASKs (ADR-0018).
- The central runtime: an issue-tracker-like application, ASKs in a UI, and durable execution such as Temporal (ADR-0019).
- The ecosystem: deep supervisor trees, a Claude Code plugin, and A2A.

<!-- axiom:generated:start -->
_Generated from the entities in this directory. Do not edit by hand._

| ID | Title | Status | Code | Requires | Tasks done |
|---|---|---|---|---|---|
| [MS-0001](MS-0001.md) | M0: Foundations | Active | M0 |  | 1/2 |
| [MS-0002](MS-0002.md) | M1: DSL core in `runtime/axiom/dsl/` | Planned | M1 | MS-0001 | 0/1 |
| [MS-0003](MS-0003.md) | M2: Entity core in `runtime/axiom/entities/` | Planned | M2 | MS-0002 |  |
| [MS-0004](MS-0004.md) | M3: Interpreter | Planned | M3 | MS-0003 |  |
| [MS-0005](MS-0005.md) | M4: MCP server, CLI, `AGENT.md` and hooks | Planned | M4 | MS-0004 |  |
| [MS-0006](MS-0006.md) | M5: First real run | Planned | M5 | MS-0005 |  |
| [MS-0007](MS-0007.md) | M6: DSL v4 | Planned | M6 | MS-0006 | 0/1 |
<!-- axiom:generated:end -->
