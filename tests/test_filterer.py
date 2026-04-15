"""Tests for envguard.filterer."""
import pytest
from envguard.filterer import filter_env, FilterReport, FilterEntry


SAMPLE_ENV = {
    "DB_HOST": "localhost",
    "DB_PORT": "5432",
    "APP_SECRET": "abc123",
    "APP_DEBUG": "true",
    "LOG_LEVEL": "info",
}


def test_no_criteria_matches_all():
    report = filter_env(SAMPLE_ENV)
    assert report.matched_count() == len(SAMPLE_ENV)
    assert report.excluded_count() == 0


def test_prefix_filter_keeps_matching_keys():
    report = filter_env(SAMPLE_ENV, prefix="DB_")
    keys = [e.key for e in report.entries]
    assert "DB_HOST" in keys
    assert "DB_PORT" in keys
    assert "APP_SECRET" not in keys


def test_prefix_filter_excludes_non_matching():
    report = filter_env(SAMPLE_ENV, prefix="DB_")
    assert "APP_SECRET" in report.excluded
    assert "LOG_LEVEL" in report.excluded


def test_pattern_filter_matches_by_regex():
    report = filter_env(SAMPLE_ENV, pattern=r"^APP_")
    keys = [e.key for e in report.entries]
    assert "APP_SECRET" in keys
    assert "APP_DEBUG" in keys
    assert "DB_HOST" not in keys


def test_key_filter_matches_explicit_keys():
    report = filter_env(SAMPLE_ENV, keys=["LOG_LEVEL", "DB_HOST"])
    keys = [e.key for e in report.entries]
    assert "LOG_LEVEL" in keys
    assert "DB_HOST" in keys
    assert len(keys) == 2


def test_matched_by_field_set_correctly_for_prefix():
    report = filter_env(SAMPLE_ENV, prefix="DB_")
    for entry in report.entries:
        assert entry.matched_by == "prefix"


def test_matched_by_field_set_correctly_for_key():
    report = filter_env(SAMPLE_ENV, keys=["LOG_LEVEL"])
    assert report.entries[0].matched_by == "key"


def test_matched_by_field_set_correctly_for_pattern():
    report = filter_env(SAMPLE_ENV, pattern=r"SECRET")
    assert report.entries[0].matched_by == "pattern"


def test_exclude_pattern_removes_keys():
    report = filter_env(SAMPLE_ENV, exclude_pattern=r"^DB_")
    keys = [e.key for e in report.entries]
    assert "DB_HOST" not in keys
    assert "DB_PORT" not in keys
    assert "DB_HOST" in report.excluded


def test_result_env_returns_dict():
    report = filter_env(SAMPLE_ENV, prefix="DB_")
    result = report.result_env()
    assert isinstance(result, dict)
    assert result["DB_HOST"] == "localhost"


def test_empty_env_returns_empty_report():
    report = filter_env({})
    assert report.matched_count() == 0
    assert report.excluded_count() == 0


def test_invalid_regex_pattern_does_not_raise():
    report = filter_env(SAMPLE_ENV, pattern="[invalid")
    assert isinstance(report, FilterReport)


def test_exclude_takes_priority_over_prefix():
    report = filter_env(SAMPLE_ENV, prefix="DB_", exclude_pattern=r"DB_PORT")
    keys = [e.key for e in report.entries]
    assert "DB_PORT" not in keys
    assert "DB_HOST" in keys
