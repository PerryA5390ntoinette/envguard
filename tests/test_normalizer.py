"""Tests for envguard.normalizer."""
import pytest
from envguard.normalizer import (
    NormalizeEntry,
    NormalizeReport,
    normalize_env,
)


def run_normalize(env, keys=None):
    return normalize_env(env, keys=keys)


# ---------------------------------------------------------------------------
# NormalizeReport helpers
# ---------------------------------------------------------------------------

def test_changed_count_reflects_mutations():
    env = {"FLAG": "True", "NAME": "alice"}
    _, report = run_normalize(env)
    assert report.changed_count == 1  # FLAG -> true


def test_unchanged_count_reflects_clean_values():
    env = {"FLAG": "true", "NAME": "alice"}
    _, report = run_normalize(env)
    assert report.unchanged_count == 2


def test_result_env_contains_all_keys():
    env = {"A": "1", "B": "hello"}
    result, _ = run_normalize(env)
    assert set(result.keys()) == {"A", "B"}


# ---------------------------------------------------------------------------
# Boolean normalisation
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("raw", ["True", "TRUE", "Yes", "YES", "On", "ON", "1"])
def test_truthy_values_normalize_to_true(raw):
    result, report = run_normalize({"FLAG": raw})
    assert result["FLAG"] == "true"
    assert report.entries[0].rule == "boolean"


@pytest.mark.parametrize("raw", ["False", "FALSE", "No", "NO", "Off", "OFF", "0"])
def test_falsy_values_normalize_to_false(raw):
    result, report = run_normalize({"FLAG": raw})
    assert result["FLAG"] == "false"
    assert report.entries[0].rule == "boolean"


def test_already_canonical_true_unchanged():
    result, report = run_normalize({"FLAG": "true"})
    assert result["FLAG"] == "true"
    assert not report.entries[0].changed


# ---------------------------------------------------------------------------
# Quote stripping
# ---------------------------------------------------------------------------

def test_double_quoted_value_stripped():
    result, report = run_normalize({"HOST": '"localhost"'})
    assert result["HOST"] == "localhost"
    assert report.entries[0].rule == "trim_quotes"


def test_single_quoted_value_stripped():
    result, report = run_normalize({"HOST": "'localhost'"}) 
    assert result["HOST"] == "localhost"
    assert report.entries[0].rule == "trim_quotes"


def test_mismatched_quotes_not_stripped():
    result, _ = run_normalize({"HOST": "'localhost\""})
    assert result["HOST"] == "'localhost\""


# ---------------------------------------------------------------------------
# Whitespace stripping
# ---------------------------------------------------------------------------

def test_leading_trailing_whitespace_stripped():
    result, report = run_normalize({"KEY": "  hello  "})
    assert result["KEY"] == "hello"
    assert report.entries[0].rule == "strip"


def test_internal_whitespace_preserved():
    result, _ = run_normalize({"KEY": "hello world"})
    assert result["KEY"] == "hello world"


# ---------------------------------------------------------------------------
# Selective key targeting
# ---------------------------------------------------------------------------

def test_only_targeted_keys_normalized():
    env = {"A": "  trimmed  ", "B": "  untouched  "}
    result, report = run_normalize(env, keys=["A"])
    assert result["A"] == "trimmed"
    assert result["B"] == "  untouched  "


def test_keys_none_normalizes_all():
    env = {"A": "TRUE", "B": "FALSE"}
    result, report = run_normalize(env, keys=None)
    assert result["A"] == "true"
    assert result["B"] == "false"
    assert report.changed_count == 2


def test_empty_env_returns_empty_report():
    result, report = run_normalize({})
    assert result == {}
    assert report.changed_count == 0
    assert report.unchanged_count == 0
