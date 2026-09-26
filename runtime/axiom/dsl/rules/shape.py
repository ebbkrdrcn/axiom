"""How a node's readable children divide into `→` items, `→ FALLBACK`s and plain lines."""

from __future__ import annotations

from axiom.dsl import nodes as n
from axiom.dsl.visitor import valid_children


def items(node: n.Node) -> tuple[n.Node, ...]:
    return tuple(c for c in valid_children(node) if c.arrow and not isinstance(c, n.Fallback))


def fallbacks(node: n.Node) -> tuple[n.Node, ...]:
    return tuple(c for c in valid_children(node) if isinstance(c, n.Fallback))


def plain(node: n.Node) -> tuple[n.Node, ...]:
    return tuple(c for c in valid_children(node) if not c.arrow)


def is_simple(node: n.Node) -> bool:
    """A statement that has no body of its own; as a `→` item it may have continuation lines."""
    return not isinstance(node, (n.Program, n.Loop, n.Fallback, *n.FLOW_HOSTS, *n.FALLBACK_HOSTS))


def is_fallback_host(node: n.Node) -> bool:
    return isinstance(node, n.FALLBACK_HOSTS)


def is_flow_host(node: n.Node) -> bool:
    return isinstance(node, n.FLOW_HOSTS)


def fallback_problem(node: n.Node) -> bool:
    """True when a FALLBACK's children are not a non-empty list of `→` items (V1)."""
    return not items(node) or bool(plain(node)) or bool(fallbacks(node))
