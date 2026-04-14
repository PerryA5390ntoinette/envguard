"""Tests for envguard.deprecator."""
import pytest
from envguard.deprecator import (
    DeprecationEntry,
    DeprecationReport,
    check_deprecations,
)


DEP_MAP = {
    "OLD_API_KEY": {"reason": "Use NEW_API_KEY instead.", "replacement": "NEW_API_KEY"},
    "LEGACY_HOST": {"reason": "Removed in v2.", "replacement": None},
    "DEPRECATED_FLAG": {"reason": "Feature removed."},
}


def run_check(env):
    return check_deprecations(env, DEP_MAP)


def test_no_deprecated_keys_returns_empty_report():
    report = run_check({"DATABASE_URL": "postgres://localhost/db"})
    assert not report.has_deprecations
    assert report.total == 0


def test_deprecated_key_detected():
    report = run_check({"OLD_API_KEY": "abc123"})
    assert report.has_deprecations
    assert report.total == 1


def test_deprecated_entry_key_correct():
    report = run_check({"OLD_API_KEY": "abc123"})
    assert report.entries[0].key == "OLD_API_KEY"


def test_deprecated_entry_reason_populated():
    report = run_check({"OLD_API_KEY": "abc123"})
    assert "NEW_API_KEY" in report.entries[0].reason


def test_deprecated_entry_replacement_populated():
    report = run_check({"OLD_API_KEY": "abc123"})
    assert report.entries[0].replacement == "NEW_API_KEY"


def test_deprecated_entry_no_replacement():
    report = run_check({"LEGACY_HOST": "localhost"})
    assert report.entries[0].replacement is None
    assert not report.entries[0].has_replacement


def test_deprecated_entry_missing_replacement_key():
    report = run_check({"DEPRECATED_FLAG": "true"})
    assert report.entries[0].replacement is None


def test_multiple_deprecated_keys_all_detected():
    report = run_check({"OLD_API_KEY": "x", "LEGACY_HOST": "y"})
    assert report.total == 2


def test_only_deprecated_keys_reported():
    report = run_check({"OLD_API_KEY": "x", "SAFE_KEY": "y"})
    assert report.total == 1
    assert report.entries[0].key == "OLD_API_KEY"


def test_with_replacement_list_correct():
    report = run_check({"OLD_API_KEY": "x", "LEGACY_HOST": "y"})
    assert len(report.with_replacement) == 1
    assert report.with_replacement[0].key == "OLD_API_KEY"


def test_without_replacement_list_correct():
    report = run_check({"OLD_API_KEY": "x", "LEGACY_HOST": "y"})
    assert len(report.without_replacement) == 1
    assert report.without_replacement[0].key == "LEGACY_HOST"


def test_empty_env_returns_empty_report():
    report = run_check({})
    assert report.total == 0
    assert not report.has_deprecations
