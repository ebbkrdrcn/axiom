# Convention Representation

- **Authoritative representation:** one Markdown file per Convention in `docs/contributing/`, relative to the target project's root.
- **File name:** `<id>.md`. This is a convention; the `id` field is authoritative.
- **Front matter (YAML)** holds `id`, `type`, `status`, `scope`, `check` and `adr`.
- **The sections of the Template** are level-2 headings (`## Rule`, …).
- **`_index.md` in the same directory is not an entity.** It is the collection's index.
