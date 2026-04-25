"""Tests for envguard.flattener."""
from __future__ import annotations

import pytest

from envguard.flattener import (
    FlattenEntry,
    FlattenReport,
    _depth,
    _flatten_key,
    flatten_env,
)


# ---------------------------------------------------------------------------
# Unit helpers
# ---------------------------------------------------------------------------

def run_flatten(env, separator="__", output_sep="."):
    return flatten_env(env, separator=separator, output_sep=output_sep)


# ---------------------------------------------------------------------------
# _flatten_key
# ---------------------------------------------------------------------------

def test_flatten_key_no_separator_unchanged():
    assert _flatten_key("DATABASE_URL") == "DATABASE_URL"


def test_flatten_key_single_level():
    assert _flatten_key("APP__HOST") == "app.host"


def test_flatten_key_two_levels():
    assert _flatten_key("APP__DB__HOST") == "app.db.host"


def test_flatten_key_custom_output_sep():
    assert _flatten_key("APP__DB__HOST", output_sep="_") == "app_db_host"


# ---------------------------------------------------------------------------
# _depth
# ---------------------------------------------------------------------------

def test_depth_no_separator_is_zero():
    assert _depth("DATABASE_URL") == 0


def test_depth_one_separator_is_one():
    assert _depth("APP__HOST") == 1


def test_depth_two_separators_is_two():
    assert _depth("APP__DB__HOST") == 2


# ---------------------------------------------------------------------------
# flatten_env
# ---------------------------------------------------------------------------

def test_returns_tuple():
    result = run_flatten({})
    assert isinstance(result, tuple) and len(result) == 2


def test_report_is_flatten_report_instance():
    _, report = run_flatten({})
    assert isinstance(report, FlattenReport)


def test_empty_env_produces_empty_report():
    _, report = run_flatten({})
    assert report.entries == []


def test_plain_key_not_changed():
    _, report = run_flatten({"DATABASE_URL": "postgres://"})
    assert report.entries[0].changed is False


def test_nested_key_is_changed():
    _, report = run_flatten({"APP__HOST": "localhost"})
    assert report.entries[0].changed is True


def test_flattened_key_in_result_env():
    result_env, _ = run_flatten({"APP__HOST": "localhost"})
    assert "app.host" in result_env
    assert result_env["app.host"] == "localhost"


def test_original_key_absent_from_result_env():
    result_env, _ = run_flatten({"APP__HOST": "localhost"})
    assert "APP__HOST" not in result_env


def test_changed_count_correct():
    env = {"APP__HOST": "localhost", "PORT": "8080", "DB__NAME": "mydb"}
    _, report = run_flatten(env)
    assert report.changed_count == 2


def test_unchanged_count_correct():
    env = {"APP__HOST": "localhost", "PORT": "8080"}
    _, report = run_flatten(env)
    assert report.unchanged_count == 1


def test_max_depth_reflects_deepest_key():
    env = {"A__B__C": "x", "D__E": "y", "F": "z"}
    _, report = run_flatten(env)
    assert report.max_depth == 2


def test_entry_depth_populated():
    _, report = run_flatten({"APP__DB__HOST": "localhost"})
    assert report.entries[0].depth == 2


def test_custom_separator_respected():
    result_env, report = run_flatten({"APP.DB.HOST": "localhost"}, separator=".", output_sep="_")
    assert "app_db_host" in result_env
    assert report.changed_count == 1
