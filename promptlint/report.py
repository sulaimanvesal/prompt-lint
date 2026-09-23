"""Report formatters: human-readable text and machine-readable JSON."""
from __future__ import annotations

import json

from promptlint.analyzer import LintReport

_SEV_ICON = {"error": "✗", "warning": "⚠", "info": "ℹ"}


def format_text(report: LintReport) -> str:
    lines = [f"prompt-lint: {report.source}", f"  {report.summary()}", ""]
    if not report.findings:
        lines.append("  No issues found. Ship it.")
        return "\n".join(lines)
    for f in report.findings:
        loc = f"line {f.line}" if f.line else "prompt"
        lines.append(f"  [{_SEV_ICON[f.severity]}] {f.rule} {f.title} ({loc})")
        lines.append(f"      {f.message}")
        if f.suggestion:
            lines.append(f"      → {f.suggestion}")
    return "\n".join(lines)


def format_json(report: LintReport) -> str:
    return json.dumps(report.to_dict(), indent=2)
