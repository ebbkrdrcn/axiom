"""CONV-0001: the runtime core imports only the standard library (and axiom itself); only `mcp/` may use the MCP SDK."""

import ast
import sys
from pathlib import Path

RUNTIME = Path(__file__).resolve().parents[1] / "runtime" / "axiom"


def test_runtime_core_imports_only_the_standard_library() -> None:
    offenders = []
    for path in RUNTIME.rglob("*.py"):
        if "mcp" in path.relative_to(RUNTIME).parts:
            continue
        for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
            names = []
            if isinstance(node, ast.Import):
                names = [a.name for a in node.names]
            elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
                names = [node.module]
            for name in names:
                top = name.split(".")[0]
                if top != "axiom" and top not in sys.stdlib_module_names and top != "__future__":
                    offenders.append(f"{path.relative_to(RUNTIME)}: {name}")
    assert offenders == []
