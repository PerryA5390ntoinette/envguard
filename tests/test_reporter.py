"""Tests for envguard.reporter output formatting."""

import io
import pytest

from envguard.validator import ValidationResult, ValidationReport
from envguard.reporter import format_result, print_report


def make_result(level: str, variable: str, message: str) -> ValidationResult:
    return ValidationResult(level=level, variable=variable, message=message)


class TestFormatResult:
    def test_error_label_no_color(self):
        result = make_result("error", "DATABASE_URL", "Missing required variable")
        output = format_result(result, use_color=False)
        assert "[ERROR]" in output
        assert "DATABASE_URL" in output
        assert "Missing required variable" in output

    def test_warning_label_no_color(self):
        result = make_result("warning", "LOG_LEVEL", "Does not match pattern")
        output = format_result(result, use_color=False)
        assert "[WARNING]" in output
        assert "LOG_LEVEL" in output

    def test_info_label_no_color(self):
        result = make_result("info", "APP_ENV", "Optional variable present")
        output = format_result(result, use_color=False)
        assert "[INFO]" in output

    def test_color_codes_included_when_enabled(self):
        result = make_result("error", "SECRET_KEY", "Missing")
        output = format_result(result, use_color=True)
        assert "\033[" in output

    def test_no_color_codes_when_disabled(self):
        result = make_result("error", "SECRET_KEY", "Missing")
        output = format_result(result, use_color=False)
        assert "\033[" not in output


class TestPrintReport:
    def _make_report(self, errors=None, warnings=None, passed=None):
        return ValidationReport(
            errors=errors or [],
            warnings=warnings or [],
            passed=passed or [],
        )

    def test_all_passed_shows_success_message(self):
        report = self._make_report(passed=[make_result("info", "APP_ENV", "OK")])
        buf = io.StringIO()
        print_report(report, out=buf, use_color=False)
        output = buf.getvalue()
        assert "All variables passed validation" in output
        assert "Status: PASS" in output

    def test_errors_shown_in_output(self):
        report = self._make_report(
            errors=[make_result("error", "DB_URL", "Missing required variable")]
        )
        buf = io.StringIO()
        print_report(report, out=buf, use_color=False)
        output = buf.getvalue()
        assert "DB_URL" in output
        assert "Missing required variable" in output
        assert "Status: FAIL" in output

    def test_summary_counts_are_correct(self):
        report = self._make_report(
            errors=[make_result("error", "A", "err")],
            warnings=[make_result("warning", "B", "warn"), make_result("warning", "C", "warn2")],
            passed=[make_result("info", "D", "ok")],
        )
        buf = io.StringIO()
        print_report(report, out=buf, use_color=False)
        output = buf.getvalue()
        assert "1 error(s)" in output
        assert "2 warning(s)" in output
        assert "1 passed" in output

    def test_pass_status_when_only_warnings(self):
        report = self._make_report(
            warnings=[make_result("warning", "LOG_LEVEL", "unexpected value")]
        )
        buf = io.StringIO()
        print_report(report, out=buf, use_color=False)
        output = buf.getvalue()
        assert "Status: PASS" in output
