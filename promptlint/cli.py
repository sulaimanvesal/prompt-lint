"""CLI: lint prompt files (or stdin) from the terminal / CI."""
from __future__ import annotations

import argparse
import sys

from promptlint import PromptLinter
from promptlint.report import format_json, format_text
from promptlint.rules import RULES


def _read(path: str) -> tuple[str, str]:
    if path == "-":
        return sys.stdin.read(), "<stdin>"
    with open(path, encoding="utf-8") as fh:
        return fh.read(), path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="prompt-lint",
        description="Static linter for LLM system prompts and agent instructions.",
    )
    parser.add_argument("files", nargs="*", default=["-"],
                        help="Prompt files to lint (default: stdin).")
    parser.add_argument("--format", choices=["text", "json"], default="text",
                        help="Output format.")
    parser.add_argument("--fail-on", choices=["error", "warning", "info"],
                        default="error",
                        help="Minimum severity that fails the run (exit 1).")
    parser.add_argument("--disable", default="",
                        help="Comma-separated rule codes to skip, e.g. PL004,PL007.")
    parser.add_argument("--list-rules", action="store_true",
                        help="List all rules and exit.")
    args = parser.parse_args(argv)

    if args.list_rules:
        for r in RULES:
            print(f"{r.code}  {r.severity:7} {r.title:28} {r.explanation}")
        return 0

    linter = PromptLinter(disable=[c.strip() for c in args.disable.split(",") if c.strip()])
    rank = {"error": 0, "warning": 1, "info": 2}
    worst = 2
    failed = False
    for path in args.files:
        try:
            text, source = _read(path)
        except OSError as exc:
            print(f"prompt-lint: cannot read {path}: {exc}", file=sys.stderr)
            failed = True
            continue
        report = linter.lint(text, source=source)
        print(format_json(report) if args.format == "json" else format_text(report))
        for f in report.findings:
            worst = min(worst, rank[f.severity])
        if worst <= rank[args.fail_on]:
            failed = True
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
