"""FORKs that are still open (not joined) before a statement in the same flow."""

from __future__ import annotations

from axiom.dsl import nodes as n
from axiom.dsl.visitor import valid_children


def open_forks_before(node: n.Node, parent: n.Node) -> tuple[n.Fork, ...]:
    """The FORKs among the earlier siblings of `node` that no JOIN between them and `node` closes."""
    siblings = valid_children(parent)
    open_: list[n.Fork] = []
    for sibling in siblings[: siblings.index(node)]:
        if isinstance(sibling, n.Fork):
            open_.append(sibling)
        elif isinstance(sibling, n.Join) and open_:
            open_.pop()
    return tuple(open_)
