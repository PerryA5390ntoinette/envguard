"""Tests for envguard.grouper."""

import pytest
from envguard.grouper import group_env, _extract_prefix, GroupEntry, GroupReport


# ---------------------------------------------------------------------------
# _extract_prefix
# ---------------------------------------------------------------------------

def test_extract_prefix_with_underscore():
    prefix, had = _extract_prefix("DB_HOST")
    assert prefix == "DB"
    assert had is True


def test_extract_prefix_no_separator():
    prefix, had = _extract_prefix("PORT")
    assert prefix == "PORT"
    assert had is False


def test_extract_prefix_multiple_underscores():
    prefix, had = _extract_prefix("AWS_SECRET_KEY")
    assert prefix == "AWS"
    assert had is True


# ---------------------------------------------------------------------------
# group_env — basic grouping
# ---------------------------------------------------------------------------

def test_empty_env_returns_empty_report():
    report = group_env({})
    assert report.total() == 0
    assert report.all_groups() == []
    assert report.ungrouped == []


def test_single_prefix_group_created():
    env = {"DB_HOST": "localhost", "DB_PORT": "5432"}
    report = group_env(env)
    assert "DB" in report.all_groups()
    assert len(report.entries_for("DB")) == 2


def test_multiple_prefix_groups():
    env = {
        "DB_HOST": "localhost",
        "DB_PORT": "5432",
        "AWS_KEY": "abc",
        "AWS_SECRET": "xyz",
    }
    report = group_env(env)
    assert set(report.all_groups()) == {"DB", "AWS"}


def test_no_separator_key_goes_to_ungrouped():
    env = {"PORT": "8080"}
    report = group_env(env)
    assert len(report.ungrouped) == 1
    assert report.ungrouped[0].key == "PORT"


def test_group_entries_preserve_values():
    env = {"DB_HOST": "localhost"}
    report = group_env(env)
    entry = report.entries_for("DB")[0]
    assert entry.value == "localhost"


def test_min_group_size_moves_small_groups_to_ungrouped():
    env = {"DB_HOST": "localhost", "AWS_KEY": "abc", "AWS_SECRET": "xyz"}
    report = group_env(env, min_group_size=2)
    assert "AWS" in report.all_groups()
    assert "DB" not in report.all_groups()
    ungrouped_keys = [e.key for e in report.ungrouped]
    assert "DB_HOST" in ungrouped_keys


def test_total_count_matches_input():
    env = {"DB_HOST": "h", "DB_PORT": "p", "PORT": "8080"}
    report = group_env(env)
    assert report.total() == 3


def test_all_groups_sorted_alphabetically():
    env = {"Z_ONE": "1", "A_TWO": "2", "M_THREE": "3"}
    report = group_env(env)
    assert report.all_groups() == ["A", "M", "Z"]


def test_entries_for_unknown_group_returns_empty():
    report = GroupReport()
    assert report.entries_for("MISSING") == []


def test_group_entry_group_field_matches_prefix():
    env = {"APP_DEBUG": "true"}
    report = group_env(env)
    entry = report.entries_for("APP")[0]
    assert entry.group == "APP"
