"""The validity rules V1…V12 of `dsl.md`, one class each, and the default registry."""

from __future__ import annotations

from axiom.dsl.rules.base import NodeRule, Rule, RuleRegistry
from axiom.dsl.rules.v01_structure import V1Structure
from axiom.dsl.rules.v02_break_outside_loop import V2BreakOutsideLoop
from axiom.dsl.rules.v03_break_across_fork import V3BreakAcrossFork
from axiom.dsl.rules.v04_arrows import V4Arrows
from axiom.dsl.rules.v05_auto import V5Auto
from axiom.dsl.rules.v06_when_outcome import V6WhenOutcome
from axiom.dsl.rules.v07_decision_names import V7DecisionNames
from axiom.dsl.rules.v08_fallback_end import V8FallbackEnd
from axiom.dsl.rules.v09_fork_join import V9ForkJoin
from axiom.dsl.rules.v10_when_before_join import V10WhenBeforeJoin
from axiom.dsl.rules.v11_declarations import V11Declarations
from axiom.dsl.rules.v12_bound_names import V12BoundNames

RULE_CLASSES: tuple[type[Rule], ...] = (
    V1Structure,
    V2BreakOutsideLoop,
    V3BreakAcrossFork,
    V4Arrows,
    V5Auto,
    V6WhenOutcome,
    V7DecisionNames,
    V8FallbackEnd,
    V9ForkJoin,
    V10WhenBeforeJoin,
    V11Declarations,
    V12BoundNames,
)


def default_registry() -> RuleRegistry:
    return RuleRegistry([cls() for cls in RULE_CLASSES])


__all__ = ["NodeRule", "RULE_CLASSES", "Rule", "RuleRegistry", "default_registry"]
