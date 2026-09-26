"""Visitor over the AST.

`Visitor.visit` dispatches to `visit_<NodeClass>` and falls back to `generic_visit`, which visits the
children. While a node's children are visited, `self.path` holds its ancestors, innermost last.
"""

from __future__ import annotations

from typing import Callable, Iterator

from axiom.dsl import nodes as n


class Visitor:
    def __init__(self) -> None:
        self.path: list[n.Node] = []

    def visit(self, node: n.Node) -> None:
        method: Callable[[n.Node], None] = getattr(self, f"visit_{type(node).__name__}", self.generic_visit)
        method(node)

    def generic_visit(self, node: n.Node) -> None:
        self.path.append(node)
        for child in node.children:
            self.visit(child)
        self.path.pop()

    @property
    def parent(self) -> n.Node:
        """The parent of the node being visited."""
        return self.path[-1]


def walk(node: n.Node) -> Iterator[n.Node]:
    """Every descendant of `node` in source order (pre-order)."""
    for child in node.children:
        yield child
        yield from walk(child)


def valid_children(node: n.Node) -> tuple[n.Node, ...]:
    """The children the rules judge: lines the parser could not read are left out."""
    return tuple(c for c in node.children if not isinstance(c, n.Invalid))
