# Contributing

Contributions follow the conventions in [`docs/contributing/`](docs/contributing/_index.md). Each convention is an entity (`CONV-NNNN`) that names its scope and how compliance is checked.

Before a change is merged:

- `python3 lab/tools/entitycheck.py --all docs` passes.
- An independent reviewer, who did not do the work, checks the change against the Active conventions in its scope.
