"""Tests for envguard.transformer."""

import pytest
from envguard.transformer import (
    transform_env,
    TransformReport,
    TransformEntry,
    KNOWN_RULES,
)


def run_transform(env: dict, rules: dict) -> TransformReport:
    return transform_env(env, rules)


def test_upper_rule_uppercases_value():
    report = run_transform({"APP_ENV": "production"}, {"APP_ENV": "upper"})
    assert report.entries[0].transformed == "PRODUCTION"


def test_lower_rule_lowercases_value():
    report = run_transform({"APP_ENV": "STAGING"}, {"APP_ENV": "lower"})
    assert report.entries[0].transformed == "staging"


def test_strip_rule_removes_whitespace():
    report = run_transform({"HOST": "  localhost  "}, {"HOST": "strip"})
    assert report.entries[0].transformed == "localhost"


def test_quote_rule_wraps_value_in_double_quotes():
    report = run_transform({"MSG": "hello"}, {"MSG": "quote"})
    assert report.entries[0].transformed == '"hello"'


def test_quote_rule_does_not_double_quote():
    report = run_transform({"MSG": '"hello"'}, {"MSG": "quote"})
    assert report.entries[0].transformed == '"hello"'


def test_unquote_rule_removes_double_quotes():
    report = run_transform({"MSG": '"world"'}, {"MSG": "unquote"})
    assert report.entries[0].transformed == "world"


def test_unquote_rule_removes_single_quotes():
    report = run_transform({"MSG": "'world'"}, {"MSG": "unquote"})
    assert report.entries[0].transformed == "world"


def test_original_value_preserved_in_entry():
    report = run_transform({"K": "hello"}, {"K": "upper"})
    assert report.entries[0].original == "hello"


def test_transformed_count_correct():
    env = {"A": "foo", "B": "bar"}
    report = run_transform(env, {"A": "upper", "B": "lower"})
    assert report.transformed_count() == 2


def test_skipped_count_for_unknown_rule():
    report = run_transform({"X": "val"}, {"X": "reverse"})
    assert report.skipped_count() == 1


def test_skipped_when_key_not_in_env():
    report = run_transform({}, {"MISSING": "upper"})
    assert report.entries[0].skipped is True
    assert "not present" in (report.entries[0].skip_reason or "")


def test_unknown_rule_marks_entry_skipped():
    report = run_transform({"K": "v"}, {"K": "rot13"})
    assert report.entries[0].skipped is True
    assert "rot13" in (report.entries[0].skip_reason or "")


def test_result_env_contains_transformed_values():
    env = {"PORT": "8080", "HOST": "  localhost  "}
    report = run_transform(env, {"HOST": "strip"})
    result = report.result_env()
    assert result["HOST"] == "localhost"


def test_empty_rules_produces_empty_report():
    report = run_transform({"A": "1"}, {})
    assert report.transformed_count() == 0
    assert report.skipped_count() == 0


def test_known_rules_set_contains_expected_entries():
    assert "upper" in KNOWN_RULES
    assert "lower" in KNOWN_RULES
    assert "strip" in KNOWN_RULES
    assert "quote" in KNOWN_RULES
    assert "unquote" in KNOWN_RULES
