# Milestone Representation

- **Authoritative representation:** one Markdown file per Milestone in `docs/roadmap/`, relative to the target project's root.
- **File name:** `<id>.md`. This is a convention; the `id` field is authoritative.
- **Front matter (YAML)** holds `id`, `type`, `status`, `code` and `requires`.
- **The sections of the Template** are level-2 headings (`## Goal`, …).
- **`_index.md` in the same directory is not an entity.** It is the collection's index, and it is the project's roadmap.
