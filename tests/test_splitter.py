"""Tests for envguard.splitter."""
from __future__ import annotations

import pytest

from envguard.splitter import SplitEntry, SplitReport, split_env


def run_split(env, prefix_map=None, default_bucket="default"):
    return split_env(env, prefix_map=prefix_map, default_bucket=default_bucket)


# ---------------------------------------------------------------------------
# Basic return types
# ---------------------------------------------------------------------------

def test_returns_split_report_instance():
    report = run_split({})
    assert isinstance(report, SplitReport)


def test_empty_env_produces_empty_report():
    report = run_split({})
    assert report.total == 0
    assert report.bucket_count == 0


# ---------------------------------------------------------------------------
# Default bucket
# ---------------------------------------------------------------------------

def test_no_prefix_map_all_keys_in_default():
    env = {"FOO": "1", "BAR": "2"}
    report = run_split(env)
    assert report.bucket_names == ["default"]
    assert report.env_for("default") == env


def test_custom_default_bucket_name():
    env = {"KEY": "val"}
    report = run_split(env, default_bucket="misc")
    assert "misc" in report.bucket_names


# ---------------------------------------------------------------------------
# Prefix matching
# ---------------------------------------------------------------------------

def test_prefix_routes_to_correct_bucket():
    env = {"DB_HOST": "localhost", "APP_NAME": "envguard"}
    report = run_split(env, prefix_map={"DB_": "database", "APP_": "app"})
    assert report.env_for("database") == {"DB_HOST": "localhost"}
    assert report.env_for("app") == {"APP_NAME": "envguard"}


def test_unmatched_key_goes_to_default():
    env = {"DB_HOST": "localhost", "LOG_LEVEL": "debug"}
    report = run_split(env, prefix_map={"DB_": "database"})
    assert "LOG_LEVEL" in report.env_for("default")


def test_longest_prefix_wins():
    env = {"DB_REPLICA_HOST": "replica"}
    report = run_split(
        env,
        prefix_map={"DB_": "database", "DB_REPLICA_": "replica"},
    )
    assert "DB_REPLICA_HOST" in report.env_for("replica")
    assert "DB_REPLICA_HOST" not in report.env_for("database")


# ---------------------------------------------------------------------------
# Counts and bucket introspection
# ---------------------------------------------------------------------------

def test_total_matches_input_size():
    env = {"A": "1", "B": "2", "C": "3"}
    report = run_split(env)
    assert report.total == 3


def test_bucket_count_reflects_distinct_buckets():
    env = {"DB_HOST": "h", "APP_PORT": "80", "OTHER": "x"}
    report = run_split(
        env,
        prefix_map={"DB_": "database", "APP_": "app"},
    )
    assert report.bucket_count == 3  # database, app, default


def test_env_for_unknown_bucket_returns_empty_dict():
    report = run_split({"FOO": "bar"})
    assert report.env_for("nonexistent") == {}


def test_entry_fields_populated():
    env = {"TOKEN": "abc"}
    report = run_split(env)
    entry = report.entries[0]
    assert isinstance(entry, SplitEntry)
    assert entry.key == "TOKEN"
    assert entry.value == "abc"
    assert entry.bucket == "default"


def test_original_env_not_mutated():
    env = {"X": "1"}
    original = dict(env)
    run_split(env, prefix_map={"X": "bucket"})
    assert env == original
