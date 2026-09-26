# ADR Representation

- Authoritative representation: one Markdown file per ADR in `docs/adr/`, relative to the target project's root.
- File name: `<id>.md` (a convention; the `id` field is authoritative).
- Front matter (YAML) holds `id`, `type`, `status`, `date`, `supersedes` and `superseded-by`.
- The sections of the Template are level-2 headings (`## Context`, …).
