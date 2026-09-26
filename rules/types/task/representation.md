# Task Representation

- Authoritative representation: one Markdown file per Task in `docs/tasks/`, relative to the target project's root.
- File name: `<id>.md` (a convention; the `id` field is authoritative).
- Front matter (YAML) holds `id`, `type`, `status`, `adr` and `milestone`.
- The sections of the Template are level-2 headings (`## Description`, …).
- `_index.md` in the same directory is not an entity; it is the collection's index.
