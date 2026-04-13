"""Tests for envguard.comparator and envguard.compare_reporter."""

import pytest
from envguard.comparator import compare_envs, ComparisonReport
from envguard.compare_reporter import format_comparison_report


def run_compare(left, right, left_label="left", right_label="right"):
    return compare_envs(left, right, left_label=left_label, right_label=right_label)


def test_identical_envs_is_identical():
    report = run_compare({"A": "1", "B": "2"}, {"A": "1", "B": "2"})
    assert report.is_identical


def test_empty_envs_is_identical():
    report = run_compare({}, {})
    assert report.is_identical


def test_mismatch_detected():
    report = run_compare({"A": "1"}, {"A": "2"})
    assert len(report.mismatches) == 1
    assert report.mismatches[0].key == "A"
    assert report.mismatches[0].left_value == "1"
    assert report.mismatches[0].right_value == "2"


def test_left_only_key():
    report = run_compare({"ONLY_LEFT": "x"}, {})
    assert len(report.left_only) == 1
    assert report.left_only[0].key == "ONLY_LEFT"
    assert report.left_only[0].right_value is None


def test_right_only_key():
    report = run_compare({}, {"ONLY_RIGHT": "y"})
    assert len(report.right_only) == 1
    assert report.right_only[0].key == "ONLY_RIGHT"
    assert report.right_only[0].left_value is None


def test_match_entry_status():
    report = run_compare({"X": "same"}, {"X": "same"})
    assert report.entries[0].status == "match"


def test_entries_sorted_by_key():
    report = run_compare({"Z": "1", "A": "2"}, {"Z": "1", "A": "2"})
    keys = [e.key for e in report.entries]
    assert keys == sorted(keys)


def test_labels_stored_on_report():
    report = run_compare({}, {}, left_label=".env.dev", right_label=".env.prod")
    assert report.left_label == ".env.dev"
    assert report.right_label == ".env.prod"


def test_is_identical_false_when_mismatch():
    report = run_compare({"A": "1"}, {"A": "9"})
    assert not report.is_identical


def test_is_identical_false_when_left_only():
    report = run_compare({"EXTRA": "v"}, {})
    assert not report.is_identical


def test_format_report_contains_labels():
    report = run_compare({"A": "1"}, {"A": "1"}, left_label="dev", right_label="prod")
    output = format_comparison_report(report, use_color=False)
    assert "dev" in output
    assert "prod" in output


def test_format_report_shows_mismatch_values():
    report = run_compare({"DB_HOST": "localhost"}, {"DB_HOST": "prod-db"})
    output = format_comparison_report(report, use_color=False)
    assert "localhost" in output
    assert "prod-db" in output


def test_format_report_identical_message():
    report = run_compare({"A": "1"}, {"A": "1"})
    output = format_comparison_report(report, use_color=False)
    assert "identical" in output.lower()


def test_format_report_summary_present():
    report = run_compare({"A": "1", "B": "2"}, {"A": "1", "C": "3"})
    output = format_comparison_report(report, use_color=False)
    assert "Summary" in output
