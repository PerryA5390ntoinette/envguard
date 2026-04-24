"""Tests for envguard.summarizer_reporter."""

from __future__ import annotations

import pytest

from envguard.summarizer import SummaryReport, SummaryLine
from envguard.summarizer_reporter import format_summary_report


def make_report(
    source: str = "app.env",
    variables_loaded: int = 5,
    audit_errors: int = 0,
    audit_warnings: int = 0,
    audit_passed: int = 5,
    lint_issues: int = 0,
    interpolation_warnings: int = 0,
) -> SummaryReport:
    line = SummaryLine(
        source=source,
        variables_loaded=variables_loaded,
        audit_errors=audit_errors,
        audit_warnings=audit_warnings,
        audit_passed=audit_passed,
        lint_issues=lint_issues,
        interpolation_warnings=interpolation_warnings,
    )
    report = SummaryReport()
    report.add(line)
    return report


class TestFormatSummaryReport:
    def test_header_present(self):
        out = format_summary_report(make_report(), use_color=False)
        assert "EnvGuard Summary" in out

    def test_source_shown(self):
        out = format_summary_report(make_report(source="prod.env"), use_color=False)
        assert "prod.env" in out

    def test_variables_loaded_shown(self):
        out = format_summary_report(make_report(variables_loaded=12), use_color=False)
        assert "12" in out

    def test_audit_errors_shown(self):
        out = format_summary_report(make_report(audit_errors=3), use_color=False)
        assert "3" in out

    def test_audit_warnings_shown(self):
        out = format_summary_report(make_report(audit_warnings=2), use_color=False)
        assert "2" in out

    def test_audit_passed_shown(self):
        out = format_summary_report(make_report(audit_passed=7), use_color=False)
        assert "7" in out

    def test_lint_issues_shown(self):
        out = format_summary_report(make_report(lint_issues=1), use_color=False)
        assert "1" in out

    def test_interpolation_warnings_shown_when_nonzero(self):
        out = format_summary_report(
            make_report(interpolation_warnings=4), use_color=False
        )
        assert "4" in out

    def test_interpolation_warnings_absent_when_zero(self):
        out = format_summary_report(
            make_report(interpolation_warnings=0), use_color=False
        )
        assert "Interp warnings" not in out

    def test_overall_pass_when_clean(self):
        out = format_summary_report(
            make_report(audit_errors=0, lint_issues=0), use_color=False
        )
        assert "PASS" in out

    def test_overall_fail_when_audit_errors(self):
        out = format_summary_report(make_report(audit_errors=1), use_color=False)
        assert "FAIL" in out

    def test_overall_fail_when_lint_issues(self):
        out = format_summary_report(make_report(lint_issues=2), use_color=False)
        assert "FAIL" in out

    def test_color_codes_present_when_enabled(self):
        out = format_summary_report(make_report(), use_color=True)
        assert "\033[" in out

    def test_no_color_codes_when_disabled(self):
        out = format_summary_report(make_report(), use_color=False)
        assert "\033[" not in out
