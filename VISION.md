# Vision

## The goal

Software is built from **human intent**.

- A company's development team consists of an **architect**, **security** and **DevOps**.
- Everyone else does **business development**, which means forming intents.
- Agents turn intents into working software.
- Nobody works inside the code. People work through intents, answers and approvals.

## How it works

```
Human intent (natural language)          ← the single entry point; a human is always at the top
        ↓
Supervisor agent
  - splits the intent into sub-tasks
  - creates an Actor for each one
        ↓
Actor = Role + Protocol + Context
  - Role:     a predefined identity (a system prompt: "Python developer", "verifier", …)
  - Protocol: a program in the DSL that defines the process the Actor follows
  - Context:  the knowledge the Actor needs, prepared by its supervisor (e.g. with graphify)
        ↓
The Actor executes its protocol. For work pieces it creates sub-actors,
delegates to them and waits for their results. The structure is recursive:
every node is responsible for its subtree.
```

## Principles

1. **Reasoning decides only inside knowledge.** Uncertainty is epistemic, meaning missing knowledge.
   - An agent decides only what follows from what it holds or can verify.
   - Anything else becomes an `ASK`.
   - Guessing and silent assumptions are forbidden.
2. **Questions escalate to authority.** An `ASK` goes up the tree to the first node that is authorised to answer it; the answer comes back down the same path. Some decisions belong only to people, and each such decision goes to the role that owns it:
   - business owns intent and "done";
   - the architect owns ADRs and protocols;
   - security owns grants;
   - DevOps owns deployment.
3. **Incomplete intent is not an error.** It loops through `ASK`s until the knowledge is sufficient.
   - Answers accumulate as knowledge, so fewer questions reach people over time.
   - People learn to state intent well, helped by templates, feedback and metrics.
4. **The process is a contract.** Protocols make *how* work is done readable, versioned and auditable, not only *what* is done. The architect's main product is the protocols and actor definitions.
5. **Critical rules are enforced, not only stated.** A mechanical layer makes the rules that must never break into checks instead of instructions. These rules cover:
   - bindings;
   - status transitions;
   - preconditions;
   - the provenance of human answers.

   A ledger records which decision was made, by whom, on what knowledge, and with what authority.
6. **Work state lives in entities.** Tasks, ADRs, and later protocols and actors, are typed entities. Their statuses, transitions and preconditions are declared in Definitions.

## Where it runs

- **First version: Claude Code.**
  - One project.
  - The main session is the supervisor.
  - Subagents are the actors.
  - Hooks and an MCP server form the mechanical layer.
- **Target: a central runtime.**
  - It works like an issue tracker and runs protocols over the entity model.
  - People answer `ASK`s in its interface.
  - Durable execution may use Temporal or a similar engine.
- **Long term: an ecosystem.**
  - Deep supervisor trees.
  - Use across projects.
  - Interoperability through standards such as MCP and A2A.

## How we get there

- **Observe first, build later.** The field is young and moving fast, and acting before it is understood is risky and expensive.
  - Concepts come before implementations.
  - Progress comes from small, cheap experiments.
  - Each experiment ends in a finding or an ADR.
- **Stable parts get the investment:**
  - the concepts;
  - the protocol library;
  - the test corpus;
  - the decision records.

  Temporary tooling gets the minimum.
- **The test corpus is a model qualification exam.**
  - Any new model, together with the current tool layer, is run against scenarios grouped by capability.
  - It qualifies for a role only if it meets the threshold and makes **zero** dangerous errors.
  - This makes model choice per role a measured, cost-aware decision.

## Where to read more

| Topic | Location |
|---|---|
| The DSL | `dsl.md` |
| The Entity Model | `entity-model.md` |
| Decisions | `docs/adr/`, in particular ADR-0015 … ADR-0019 |
| Current state and next steps | `dsl-lab/STATUS.md`, `dsl-lab/NEXT.md` |
| Test method and results | `dsl-lab/` |
