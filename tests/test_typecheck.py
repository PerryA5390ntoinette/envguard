"""Tests for envguard.typecheck module."""
import pytest
from envguard.typecheck import typecheck_env, TypeReport, _check_type


# ---------------------------------------------------------------------------
# _check_type unit tests
# ---------------------------------------------------------------------------

def test_int_valid():
    assert _check_type("PORT", "8080", "int") is None

def test_int_negative_valid():
    assert _check_type("OFFSET", "-5", "int") is None

def test_int_invalid():
    assert _check_type("PORT", "abc", "int") is not None

def test_float_valid():
    assert _check_type("RATIO", "3.14", "float") is None

def test_float_scientific_valid():
    assert _check_type("RATIO", "1e-5", "float") is None

def test_float_invalid():
    assert _check_type("RATIO", "not-a-float", "float") is not None

def test_bool_true_valid():
    for v in ("true", "True", "TRUE", "1", "yes", "on"):
        assert _check_type("FLAG", v, "bool") is None, f"Expected {v!r} to be valid bool"

def test_bool_false_valid():
    for v in ("false", "False", "0", "no", "off"):
        assert _check_type("FLAG", v, "bool") is None

def test_bool_invalid():
    assert _check_type("FLAG", "maybe", "bool") is not None

def test_url_http_valid():
    assert _check_type("ENDPOINT", "http://example.com", "url") is None

def test_url_https_valid():
    assert _check_type("ENDPOINT", "https://example.com/path", "url") is None

def test_url_invalid():
    assert _check_type("ENDPOINT", "ftp://example.com", "url") is not None

def test_nonempty_valid():
    assert _check_type("NAME", "hello", "nonempty") is None

def test_nonempty_invalid():
    assert _check_type("NAME", "", "nonempty") is not None

def test_nonempty_whitespace_invalid():
    assert _check_type("NAME", "   ", "nonempty") is not None

def test_string_type_always_passes():
    assert _check_type("X", "anything", "string") is None

def test_unknown_type_always_passes():
    assert _check_type("X", "anything", "custom_type") is None


# ---------------------------------------------------------------------------
# typecheck_env integration tests
# ---------------------------------------------------------------------------

def test_returns_type_report_instance():
    report = typecheck_env({}, {})
    assert isinstance(report, TypeReport)

def test_no_issues_for_empty_inputs():
    report = typecheck_env({}, {})
    assert not report.has_issues
    assert report.issue_count == 0

def test_valid_values_added_to_passed():
    env = {"PORT": "3000", "DEBUG": "true"}
    type_map = {"PORT": "int", "DEBUG": "bool"}
    report = typecheck_env(env, type_map)
    assert not report.has_issues
    assert "PORT" in report.passed
    assert "DEBUG" in report.passed

def test_invalid_value_produces_issue():
    env = {"PORT": "not-a-number"}
    report = typecheck_env(env, {"PORT": "int"})
    assert report.has_issues
    assert report.issues[0].key == "PORT"
    assert report.issues[0].expected_type == "int"

def test_missing_key_in_env_skipped():
    """Keys in type_map but absent from env should not produce issues."""
    report = typecheck_env({}, {"PORT": "int"})
    assert not report.has_issues
    assert len(report.passed) == 0

def test_extra_env_keys_not_in_type_map_ignored():
    env = {"EXTRA": "value", "PORT": "8080"}
    report = typecheck_env(env, {"PORT": "int"})
    assert not report.has_issues
    assert "EXTRA" not in report.passed  # only type-checked keys land in passed

def test_issue_count_matches_number_of_bad_values():
    env = {"A": "bad", "B": "also-bad", "C": "3.14"}
    type_map = {"A": "int", "B": "bool", "C": "float"}
    report = typecheck_env(env, type_map)
    assert report.issue_count == 2
