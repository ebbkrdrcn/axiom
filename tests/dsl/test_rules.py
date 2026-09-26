"""One valid and one invalid program per validity rule; each invalid one breaks only that rule."""

import pytest

from axiom.dsl import check
from axiom.dsl.rules import RULE_CLASSES, Rule, RuleRegistry, default_registry

VALID = """\
INPUT t:Task
a:ADR = t.adr
LOOP:work
  DELEGATE implementation
  VERIFY t
    → FALLBACK
        → STOP
  WHEN t.accepted
    → TRANSITION t "Review"
    → BREAK
FORK
  → VERIFY docs
  → DELEGATE tests
JOIN
WHEN docs.rejected
  → DELEGATE docs
AUTO HITL:done[approved, rejected]("Is {t} done?")
  → FALLBACK
      → STOP
WHEN done.approved
  → TRANSITION t "Done"
"""

BROKEN = {
    "V1": "LOOP:work\n",
    "V2": "BREAK\n",
    "V3": "LOOP:a\n  FORK\n    → BREAK\n    → STOP\n",
    "V4": "→ STOP\n",
    "V5": "AUTO DELEGATE x\n",
    "V6": "DELEGATE x\nWHEN x.accepted\n  → STOP\n",
    "V7": 'HITL:m[a, a]("q")\n',
    "V8": "REQUIRE repo\n  → FALLBACK\n      → DELEGATE x\n",
    "V9": "JOIN\n",
    "V10": "FORK\n  → VERIFY a\n  → VERIFY b\nWHEN a.accepted\n  → STOP\n",
    "V11": "STOP\nt:Task = TASK-0001\n",
    "V12": 'TRANSITION t "Done"\n',
}


def test_the_reference_program_is_valid() -> None:
    result = check(VALID)
    assert result.valid, [str(d) for d in result.diagnostics]


@pytest.mark.parametrize("rule", sorted(BROKEN, key=lambda r: int(r[1:])))
def test_each_rule_detects_its_violation(rule: str) -> None:
    assert check(BROKEN[rule]).rule_ids == {rule}


@pytest.mark.parametrize(
    "source, rules",
    [
        ('HITL:m[]("q")', {"V7"}),
        ('HITL:m[a]("q")\nVERIFY m', {"V7"}),
        ("t:Task = TASK-1\nt:Task = TASK-2\n", {"V11"}),
        ("a:ADR = t.adr\n", {"V11"}),
        ("INPUT t:Task\nINPUT t:Task\n", {"V11"}),
        ("a:ADR = ADR-1\nINPUT t:Task\n", {"V11"}),
        ("LOOP:a\n  INPUT t:Task\n  BREAK\n", {"V11"}),
        ('INPUT t:Task\nHITL("Look at {x}")\n', {"V12"}),
        ('t:Task = TASK-1\nHITL:t[a]("q")\n', {"V12"}),
        ("VERIFY x\n  → FALLBACK\n      → STOP\n  → FALLBACK\n      → STOP\n", {"V4"}),
        ("LOOP:a\n  → FALLBACK\n      → STOP\n", {"V4"}),
        ("VERIFY x\n  STOP\n", {"V1"}),
        ("FORK\n  → STOP\n", {"V9"}),
        ("WHEN x.y\n  STOP\n", {"V1", "V6"}),
    ],
)
def test_further_violations(source: str, rules: set[str]) -> None:
    assert check(source).rule_ids == rules


def test_break_in_a_loop_inside_a_fork_branch_is_valid() -> None:
    assert check("FORK\n  → LOOP:a\n      BREAK\n  → STOP\n").valid


def test_registry_has_one_class_per_rule_id() -> None:
    ids = [cls.id for cls in RULE_CLASSES]
    assert ids == [f"V{i}" for i in range(1, 13)]
    assert default_registry().ids == tuple(ids)


def test_registry_rejects_duplicate_ids() -> None:
    first = RULE_CLASSES[0]
    with pytest.raises(ValueError):
        RuleRegistry([first(), first()])


def test_a_registry_applies_only_its_rules() -> None:
    only_v2: list[Rule] = [cls() for cls in RULE_CLASSES if cls.id == "V2"]
    assert check("BREAK\nWHEN x.y\n  → STOP\n", RuleRegistry(only_v2)).rule_ids == {"V2"}
