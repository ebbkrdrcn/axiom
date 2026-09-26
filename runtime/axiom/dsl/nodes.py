"""AST of a DSL program (Composite).

Every node is a frozen dataclass with its source position. `children` are the lines indented under
the node, `arrow` marks a line written as a `→` item. The parser accepts any nesting; which nesting
is valid is decided by the validity rules, so that each violation is reported under the rule id the
spec gives it.
"""

from __future__ import annotations

from dataclasses import dataclass

from axiom.dsl.issues import SyntaxIssue


@dataclass(frozen=True, kw_only=True)
class Node:
    line: int
    column: int
    arrow: bool = False
    children: tuple[Node, ...] = ()


@dataclass(frozen=True, kw_only=True)
class Program(Node):
    issues: tuple[SyntaxIssue, ...] = ()


# --- inputs and bindings -------------------------------------------------------------------------


@dataclass(frozen=True, kw_only=True)
class Input(Node):
    name: str
    type: str


@dataclass(frozen=True, kw_only=True)
class Binding(Node):
    name: str
    type: str
    target: str  # an identity, or the bound name a relation starts from
    relation: str | None = None


# --- control -------------------------------------------------------------------------------------


@dataclass(frozen=True, kw_only=True)
class Loop(Node):
    name: str


@dataclass(frozen=True, kw_only=True)
class When(Node):
    subject: str
    outcome: str


@dataclass(frozen=True, kw_only=True)
class Fork(Node):
    pass


@dataclass(frozen=True, kw_only=True)
class Join(Node):
    pass


@dataclass(frozen=True, kw_only=True)
class Break(Node):
    pass


@dataclass(frozen=True, kw_only=True)
class Wait(Node):
    pass


@dataclass(frozen=True, kw_only=True)
class Stop(Node):
    pass


# --- agentic operations --------------------------------------------------------------------------


@dataclass(frozen=True, kw_only=True)
class Require(Node):
    item: str


@dataclass(frozen=True, kw_only=True)
class Delegate(Node):
    work: str


@dataclass(frozen=True, kw_only=True)
class Verify(Node):
    subject: str


@dataclass(frozen=True, kw_only=True)
class Emit(Node):
    artifact: str


@dataclass(frozen=True, kw_only=True)
class Transition(Node):
    """`TRANSITION "<state>"`: sets the process state."""

    state: str


@dataclass(frozen=True, kw_only=True)
class EntityTransition(Node):
    """`TRANSITION <name> "<status>"`: sets the status of a bound entity."""

    name: str
    status: str


# --- human interaction ---------------------------------------------------------------------------


@dataclass(frozen=True)
class Reference:
    """`{<name>}` inside a text."""

    name: str
    line: int
    column: int


@dataclass(frozen=True)
class Text:
    """The question or request of a `HITL`."""

    value: str
    references: tuple[Reference, ...]
    line: int
    column: int


@dataclass(frozen=True, kw_only=True)
class Hitl(Node):
    """`[AUTO] HITL:<name>[<answers>]("<question>")`, or `HITL("<request>")` with no name."""

    text: Text
    name: str | None = None
    answers: tuple[str, ...] = ()
    auto: bool = False


@dataclass(frozen=True, kw_only=True)
class Fallback(Node):
    pass


# --- recovery ------------------------------------------------------------------------------------


@dataclass(frozen=True, kw_only=True)
class Invalid(Node):
    """A line the parser could not read. Its issue is in `Program.issues`; its children are kept."""

    source: str


COMPOUND: tuple[type[Node], ...] = (Loop, When, Fork, Hitl, Require, Verify, EntityTransition)
FALLBACK_HOSTS: tuple[type[Node], ...] = (Hitl, Require, Verify, EntityTransition)
FLOW_HOSTS: tuple[type[Node], ...] = (When, Fork, Fallback)
