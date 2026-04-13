"""Tests for envguard.scorer."""
import pytest
from envguard.scorer import compute_score, MAX_SCORE


def test_perfect_score_when_no_issues():
    report = compute_score()
    assert report.score == MAX_SCORE


def test_grade_a_for_perfect_score():
    report = compute_score()
    assert report.grade == "A"


def test_audit_error_deducts_ten_points():
    report = compute_score(audit_errors=1)
    assert report.score == MAX_SCORE - 10


def test_audit_warning_deducts_three_points():
    report = compute_score(audit_warnings=1)
    assert report.score == MAX_SCORE - 3


def test_lint_error_deducts_eight_points():
    report = compute_score(lint_errors=1)
    assert report.score == MAX_SCORE - 8


def test_lint_warning_deducts_two_points():
    report = compute_score(lint_warnings=1)
    assert report.score == MAX_SCORE - 2


def test_exposed_secret_deducts_fifteen_points():
    report = compute_score(exposed_secrets=1)
    assert report.score == MAX_SCORE - 15


def test_combined_deductions_sum_correctly():
    report = compute_score(audit_errors=2, lint_warnings=3)
    expected = MAX_SCORE - (2 * 10) - (3 * 2)
    assert report.score == expected


def test_score_never_goes_below_zero():
    report = compute_score(audit_errors=100)
    assert report.score == 0


def test_grade_f_for_zero_score():
    report = compute_score(audit_errors=100)
    assert report.grade == "F"


def test_grade_b_for_score_75():
    # 25 points deducted: 2 audit errors (20) + 1 lint error (8) -> 72 -> D
    # 1 audit error (10) + 5 lint warnings (10) = 20 deducted -> 80 -> B
    report = compute_score(audit_errors=1, lint_warnings=5)
    assert report.score == 80
    assert report.grade == "B"


def test_grade_c_for_score_between_60_and_75():
    # 3 audit errors = 30 deducted -> 70 -> C
    report = compute_score(audit_errors=3)
    assert report.score == 70
    assert report.grade == "C"


def test_breakdown_fields_populated():
    report = compute_score(audit_errors=1, lint_warnings=2, exposed_secrets=1)
    assert report.breakdown.audit_errors == 1
    assert report.breakdown.lint_warnings == 2
    assert report.breakdown.exposed_secrets == 1


def test_deductions_list_populated_when_issues_present():
    report = compute_score(audit_errors=1, lint_errors=1)
    assert len(report.breakdown.deductions) == 2


def test_deductions_list_empty_when_no_issues():
    report = compute_score()
    assert report.breakdown.deductions == []
