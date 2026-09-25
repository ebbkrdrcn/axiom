#!/usr/bin/env python3
"""Lint every DSL code block found in probe outputs (authoring scenarios).
usage: lint_outputs.py PROBES_DIR IDS...  -> prints '<file> block<k>: VALID|INVALID ...'"""
import re, sys, glob, os
sys.path.insert(0, os.path.dirname(__file__))
from dslcheck import check
d, ids = sys.argv[1], sys.argv[2:]
for i in ids:
    for f in sorted(glob.glob(f"{d}/{i}-*.md")):
        text = open(f).read()
        blocks = [b for b in re.findall(r"```[a-zA-Z]*\n(.*?)```", text, re.S)
                  if re.search(r"^\s*(LOOP:|WHEN |FORK|DELEGATE|VERIFY|REQUIRE|HITL|AUTO|TRANSITION|EMIT)", b, re.M)]
        if not blocks:
            print(f"{os.path.basename(f)}: NO DSL BLOCK"); continue
        for k, b in enumerate(blocks, 1):
            e = check(b)
            print(f"{os.path.basename(f)} block{k}: " + ("VALID" if not e else "INVALID " + " | ".join(e)))
