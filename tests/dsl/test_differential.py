"""Differential test: `axiom.dsl.check` agrees with the reference checker `lab/tools/dslcheck.py`.

For every program of the corpus, both must give the same verdict and the same set of rule ids. The
corpus is every example in `spec/dsl.md`, every lab scenario, every probe output and every protocol.
"""

from __future__ import annotations

import importlib.util
import re
from pathlib import Path
from types import ModuleType

from axiom import dsl

ROOT = Path(__file__).resolve().parents[2]
FENCE = re.compile(r"^```(\w*)\n(.*?)^```", re.S | re.M)
PROGRAM_TAGS = ("text", "invalid", "dsl", "")


def reference() -> ModuleType:
    spec = importlib.util.spec_from_file_location("dslcheck", ROOT / "lab" / "tools" / "dslcheck.py")
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def corpus() -> list[tuple[str, str]]:
    files = [ROOT / "spec" / "dsl.md"]
    files += sorted(ROOT.glob("lab/scenarios*/*.md"))
    files += sorted(ROOT.glob("lab/iterations/*/probes/*.md"))
    programs = []
    for f in files:
        for i, (tag, block) in enumerate(FENCE.findall(f.read_text(encoding="utf-8"))):
            if tag in PROGRAM_TAGS:
                programs.append((f"{f.relative_to(ROOT)}#{i}", block))
    for f in sorted(ROOT.glob("rules/protocols/*.dsl")):
        programs.append((str(f.relative_to(ROOT)), f.read_text(encoding="utf-8")))
    return programs


def test_corpus_covers_every_source() -> None:
    names = [name for name, _ in corpus()]
    for prefix in ("spec/dsl.md", "lab/scenarios", "lab/iterations/", "rules/protocols/"):
        assert any(name.startswith(prefix) for name in names), prefix
    assert len(names) > 500


def test_zero_disagreement_with_the_reference_checker() -> None:
    ref = reference()
    disagreements = []
    for name, source in corpus():
        expected = set(re.findall(r"line \d+: (V\d+):", "\n".join(ref.check(source))))
        actual = set(dsl.check(source).rule_ids)
        if expected != actual:
            disagreements.append(f"{name}: reference {sorted(expected)}, axiom {sorted(actual)}")
    assert disagreements == []
