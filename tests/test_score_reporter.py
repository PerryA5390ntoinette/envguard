"""Tests for envguard.score_reporter."""
import pytest
from envguard.scorer import compute_score
from envguard.score_reporter import format_score_report


def perfect_report():
    return compute_score()


def flawed_report():
    return compute_score(audit_errors=2, lint_warnings=3, exposed_secrets=1)


class TestFormatScoreReport:
    def test_score_present_in_output(self):
        out = format_score_report(perfect_report(), use_color=False)
        assert "100" in out

    def test_grade_present_in_output(self):
        out = format_score_report(perfect_report(), use_color=False)
        assert "A" in out

    def test_breakdown_section_present(self):
        out = format_score_report(perfect_report(), use_color=False)
        assert "Breakdown" in out

    def test_audit_errors_shown_in_breakdown(self):
        out = format_score_report(flawed_report(), use_color=False)
        assert "Audit errors" in out

    def test_exposed_secrets_shown_in_breakdown(self):
        out = format_score_report(flawed_report(), use_color=False)
        assert "Exposed secrets" in out

    def test_deductions_section_shown_when_issues(self):
        out = format_score_report(flawed_report(), use_color=False)
        assert "Deductions" in out

    def test_deductions_section_absent_when_perfect(self):
        out = format_score_report(perfect_report(), use_color=False)
        assert "Deductions" not in out

    def test_color_codes_absent_when_disabled(self):
        out = format_score_report(perfect_report(), use_color=False)
        assert "\033[" not in out

    def test_color_codes_present_when_enabled(self):
        out = format_score_report(perfect_report(), use_color=True)
        assert "\033[" in out

    def test_f_grade_in_output_for_failing_score(self):
        report = compute_score(audit_errors=100)
        out = format_score_report(report, use_color=False)
        assert "F" in out
        assert "0" in out
