"""Tests for envguard.duplicator."""
import pytest
from envguard.duplicator import (
    find_duplicates,
    DuplicateReport,
    DuplicateEntry,
)


def run_dup(env: dict, lines=None):
    return find_duplicates(env, raw_lines=lines)


# --- key duplicate detection via raw lines ---

def test_no_key_duplicates_when_lines_absent():
    report = run_dup({"A": "1", "B": "2"})
    assert not report.has_key_duplicates


def test_no_key_duplicates_for_unique_keys():
    lines = ["A=1\n", "B=2\n"]
    report = run_dup({"A": "1", "B": "2"}, lines=lines)
    assert not report.has_key_duplicates


def test_duplicate_key_detected():
    lines = ["A=1\n", "A=2\n"]
    report = run_dup({"A": "2"}, lines=lines)
    assert report.has_key_duplicates
    assert len(report.key_duplicates) == 1
    entry = report.key_duplicates[0]
    assert entry.key == "A"
    assert entry.occurrences == 2


def test_duplicate_key_captures_all_values():
    lines = ["PORT=8080\n", "PORT=9090\n", "PORT=3000\n"]
    report = run_dup({"PORT": "3000"}, lines=lines)
    entry = report.key_duplicates[0]
    assert set(entry.values) == {"8080", "9090", "3000"}


def test_comments_and_blanks_ignored_in_key_scan():
    lines = ["# comment\n", "\n", "A=1\n", "A=2\n"]
    report = run_dup({"A": "2"}, lines=lines)
    assert len(report.key_duplicates) == 1


def test_line_without_equals_ignored():
    lines = ["NOEQUALS\n", "A=1\n", "A=2\n"]
    report = run_dup({"A": "2"}, lines=lines)
    assert report.key_duplicates[0].key == "A"


# --- value duplicate detection ---

def test_no_value_duplicates_for_unique_values():
    report = run_dup({"A": "hello", "B": "world"})
    assert not report.has_value_duplicates


def test_shared_value_detected():
    report = run_dup({"DB_PASS": "secret", "ADMIN_PASS": "secret"})
    assert report.has_value_duplicates
    assert "secret" in report.value_duplicates
    assert set(report.value_duplicates["secret"]) == {"DB_PASS", "ADMIN_PASS"}


def test_empty_value_not_flagged_as_duplicate():
    report = run_dup({"A": "", "B": ""})
    assert not report.has_value_duplicates


def test_value_shared_by_three_keys():
    report = run_dup({"X": "same", "Y": "same", "Z": "same"})
    assert len(report.value_duplicates["same"]) == 3


# --- totals ---

def test_total_issues_zero_when_clean():
    report = run_dup({"A": "1", "B": "2"})
    assert report.total_issues == 0


def test_total_issues_sums_both_categories():
    lines = ["A=1\n", "A=2\n"]
    report = run_dup({"A": "2", "B": "val", "C": "val"}, lines=lines)
    # 1 key dup + 1 value dup
    assert report.total_issues == 2


def test_report_is_duplicate_report_instance():
    report = run_dup({})
    assert isinstance(report, DuplicateReport)
