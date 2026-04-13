"""Tests for envguard.lint_reporter module."""
import pytest
from envguard.linter import LintReport, LintIssue
from envguard.lint_reporter import format_lint_issue, format_lint_report


def make_issue(severity="error", key="MY_KEY", message="Something wrong", line=1):
    return LintIssue(line_number=line, key=key, message=message, severity=severity)


def make_report(*issues):
    r = LintReport()
    for i in issues:
        r.add(i)
    return r


class TestFormatLintIssue:
    def test_error_label_present(self):
        issue = make_issue(severity="error")
        text = format_lint_issue(issue, use_color=False)
        assert "ERROR" in text

    def test_warning_label_present(self):
        issue = make_issue(severity="warning")
        text = format_lint_issue(issue, use_color=False)
        assert "WARNING" in text

    def test_key_in_output(self):
        issue = make_issue(key="DB_PASS")
        text = format_lint_issue(issue, use_color=False)
        assert "DB_PASS" in text

    def test_message_in_output(self):
        issue = make_issue(message="Needs quoting")
        text = format_lint_issue(issue, use_color=False)
        assert "Needs quoting" in text

    def test_line_number_in_output(self):
        issue = make_issue(line=42)
        text = format_lint_issue(issue, use_color=False)
        assert "42" in text

    def test_empty_key_no_brackets(self):
        issue = make_issue(key="")
        text = format_lint_issue(issue, use_color=False)
        assert "[" not in text


class TestFormatLintReport:
    def test_no_issues_message(self):
        report = make_report()
        text = format_lint_report(report, use_color=False)
        assert "No issues found" in text

    def test_header_present(self):
        report = make_report()
        text = format_lint_report(report, use_color=False)
        assert "Lint Results" in text

    def test_summary_line_present(self):
        report = make_report(make_issue(severity="error"), make_issue(severity="warning"))
        text = format_lint_report(report, use_color=False)
        assert "error(s)" in text
        assert "warning(s)" in text

    def test_each_issue_in_output(self):
        issues = [make_issue(key="A", line=1), make_issue(key="B", line=2)]
        report = make_report(*issues)
        text = format_lint_report(report, use_color=False)
        assert "A" in text
        assert "B" in text

    def test_color_codes_absent_when_disabled(self):
        report = make_report(make_issue())
        text = format_lint_report(report, use_color=False)
        assert "\033[" not in text

    def test_color_codes_present_when_enabled(self):
        report = make_report(make_issue())
        text = format_lint_report(report, use_color=True)
        assert "\033[" in text
