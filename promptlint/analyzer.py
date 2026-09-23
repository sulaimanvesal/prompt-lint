"""Core linter: builds the shared context once, then runs every rule."""
from __future__ import annotations

import re
from dataclasses import dataclass, field


@dataclass
class Finding:
    rule: str
    title: str
    severity: str  # "error" | "warning" | "info"
    message: str
    line: int | None = None
    suggestion: str = ""

    def to_dict(self) -> dict:
        return {
            "rule": self.rule,
            "title": self.title,
            "severity": self.severity,
            "message": self.message,
            "line": self.line,
            "suggestion": self.suggestion,
        }


@dataclass
class LintReport:
    source: str
    words: int
    findings: list[Finding] = field(default_factory=list)

    @property
    def errors(self) -> list[Finding]:
        return [f for f in self.findings if f.severity == "error"]

    @property
    def warnings(self) -> list[Finding]:
        return [f for f in self.findings if f.severity == "warning"]

    @property
    def infos(self) -> list[Finding]:
        return [f for f in self.findings if f.severity == "info"]

    def summary(self) -> str:
        return (f"{len(self.errors)} error(s), {len(self.warnings)} warning(s), "
                f"{len(self.infos)} info note(s) in {self.words} words")

    def to_dict(self) -> dict:
        return {
            "source": self.source,
            "words": self.words,
            "summary": self.summary(),
            "findings": [f.to_dict() for f in self.findings],
        }


def build_context(text: str) -> dict:
    lines = text.splitlines()
    sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+", text.strip()) if s.strip()]
    return {
        "lines": lines,
        "sentences": sentences,
        "words": len(text.split()),
        "chars": len(text),
    }


class PromptLinter:
    """Run the rule catalog against a prompt string.

    ``disable`` takes rule codes (e.g. ["PL004"]) to skip.
    """

    def __init__(self, rules=None, disable: list[str] | None = None):
        from promptlint.rules import RULES
        disabled = set(disable or [])
        self.rules = [r for r in (rules or RULES) if r.code not in disabled]

    def lint(self, text: str, source: str = "<string>") -> LintReport:
        ctx = build_context(text)
        findings: list[Finding] = []
        for rule in self.rules:
            findings.extend(rule.check(text, ctx, rule))
        order = {"error": 0, "warning": 1, "info": 2}
        findings.sort(key=lambda f: (order[f.severity], f.line or 0))
        return LintReport(source=source, words=ctx["words"], findings=findings)
