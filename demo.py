#!/usr/bin/env python3
"""Zero-dependency demo: lints the bundled good/bad example prompts and
prints text + JSON reports. Run with:  python3 demo.py"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

from promptlint import PromptLinter
from promptlint.report import format_json, format_text

here = pathlib.Path(__file__).resolve().parent / "examples"
linter = PromptLinter()

for name in ("bad_prompt.md", "good_prompt.md"):
    text = (here / name).read_text(encoding="utf-8")
    report = linter.lint(text, source=name)
    print(format_text(report))
    print()

bad = linter.lint((here / "bad_prompt.md").read_text(encoding="utf-8"), source="bad_prompt.md")
print("--- JSON excerpt (bad_prompt.md, first finding) ---")
print(format_json(bad)[:600], "...")
