"""Linter module: checks .env files for style and best-practice issues."""
from dataclasses import dataclass, field
from typing import List

SECRET_KEYWORDS = ("password", "secret", "token", "api_key", "private")


@dataclass
class LintIssue:
    line_number: int
    key: str
    message: str
    severity: str  # 'warning' | 'error'


@dataclass
class LintReport:
    issues: List[LintIssue] = field(default_factory=list)

    def add(self, issue: LintIssue) -> None:
        self.issues.append(issue)

    @property
    def has_issues(self) -> bool:
        return bool(self.issues)

    @property
    def error_count(self) -> int:
        return sum(1 for i in self.issues if i.severity == "error")

    @property
    def warning_count(self) -> int:
        return sum(1 for i in self.issues if i.severity == "warning")


def _check_line(line_number: int, raw_line: str, report: LintReport) -> None:
    stripped = raw_line.rstrip("\n")

    if not stripped or stripped.lstrip().startswith("#"):
        return

    if "=" not in stripped:
        report.add(LintIssue(line_number, "", "Line has no '=' separator", "error"))
        return

    key, _, value = stripped.partition("=")
    key = key.strip()

    if key != key.upper():
        report.add(LintIssue(line_number, key, "Key should be UPPER_SNAKE_CASE", "warning"))

    if " " in key:
        report.add(LintIssue(line_number, key, "Key contains spaces", "error"))

    if value != value.strip():
        report.add(LintIssue(line_number, key, "Value has leading or trailing whitespace", "warning"))

    lower_key = key.lower()
    if any(kw in lower_key for kw in SECRET_KEYWORDS) and not value.startswith(("'", '"')):
        report.add(LintIssue(line_number, key, "Sensitive value should be quoted", "warning"))


def lint_env_lines(lines: List[str]) -> LintReport:
    report = LintReport()
    for idx, line in enumerate(lines, start=1):
        _check_line(idx, line, report)
    return report


def lint_env_file(path: str) -> LintReport:
    with open(path, "r", encoding="utf-8") as fh:
        lines = fh.readlines()
    return lint_env_lines(lines)
