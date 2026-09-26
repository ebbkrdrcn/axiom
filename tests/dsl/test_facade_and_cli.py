import io
import random
from pathlib import Path

from axiom import dsl
from axiom.cli import main

ALPHABET = ['→', ' ', '  ', '\n', '"', '{', '}', '[', ']', '(', ')', ':', '.', ',', '=', 'x', 'LOOP', 'WHEN', 'HITL',
            'AUTO', 'FALLBACK', 'STOP', 'BREAK', 'FORK', 'JOIN', 'VERIFY', 'TRANSITION', 'INPUT', '\t', 'accepted']


def test_check_never_raises_on_arbitrary_text() -> None:
    rng = random.Random(0)
    for _ in range(2000):
        source = "".join(rng.choice(ALPHABET) for _ in range(rng.randint(0, 40)))
        result = dsl.check(source)
        assert result.valid == (not result.diagnostics)


def test_empty_program_is_valid() -> None:
    assert dsl.check("").valid


def test_diagnostics_are_sorted_and_positioned() -> None:
    result = dsl.check("BREAK\nJOIN\n")
    assert [(d.line, d.rule) for d in result.diagnostics] == [(1, "V2"), (2, "V9")]
    assert str(result.diagnostics[0]).startswith("line 1: V2: ")


def test_cli_check_files(tmp_path: Path) -> None:
    good, bad = tmp_path / "good.dsl", tmp_path / "bad.dsl"
    good.write_text("STOP\n")
    bad.write_text("BREAK\n")
    out = io.StringIO()
    assert main(["check", str(good)], out) == 0
    assert main(["check", str(good), str(bad)], out) == 1
    assert f"{bad} INVALID" in out.getvalue() and "V2" in out.getvalue()


def test_cli_check_markdown(tmp_path: Path) -> None:
    doc = tmp_path / "doc.md"
    doc.write_text("```text\nSTOP\n```\n\n```invalid\nBREAK\n```\n")
    assert main(["check", "--md", str(doc)], io.StringIO()) == 0
    doc.write_text("```text\nBREAK\n```\n")
    assert main(["check", "--md", str(doc)], io.StringIO()) == 1
