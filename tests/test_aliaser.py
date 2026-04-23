"""Tests for envguard.aliaser and envguard.alias_reporter."""
from __future__ import annotations

import pytest

from envguard.aliaser import AliasEntry, AliasReport, apply_aliases
from envguard.alias_reporter import format_alias_report


def run_alias(env, alias_map, **kwargs):
    return apply_aliases(env, alias_map, **kwargs)


# ---------------------------------------------------------------------------
# apply_aliases – core behaviour
# ---------------------------------------------------------------------------

def test_returns_tuple_of_env_and_report():
    new_env, report = run_alias({"OLD_KEY": "val"}, {"OLD_KEY": "NEW_KEY"})
    assert isinstance(new_env, dict)
    assert isinstance(report, AliasReport)


def test_alias_remapped_to_canonical():
    new_env, _ = run_alias({"OLD_KEY": "hello"}, {"OLD_KEY": "NEW_KEY"})
    assert new_env.get("NEW_KEY") == "hello"


def test_alias_removed_from_env():
    new_env, _ = run_alias({"OLD_KEY": "hello"}, {"OLD_KEY": "NEW_KEY"})
    assert "OLD_KEY" not in new_env


def test_unrelated_keys_preserved():
    new_env, _ = run_alias(
        {"OLD_KEY": "v", "UNRELATED": "x"}, {"OLD_KEY": "NEW_KEY"}
    )
    assert new_env.get("UNRELATED") == "x"


def test_missing_alias_not_in_report():
    _, report = run_alias({"OTHER": "v"}, {"OLD_KEY": "NEW_KEY"})
    assert report.resolved_count() == 0
    assert len(report.entries) == 0


def test_resolved_count_increments():
    _, report = run_alias(
        {"A": "1", "B": "2"}, {"A": "A_NEW", "B": "B_NEW"}
    )
    assert report.resolved_count() == 2


def test_canonical_not_overwritten_by_default():
    new_env, report = run_alias(
        {"OLD": "alias_val", "NEW": "canonical_val"}, {"OLD": "NEW"}
    )
    assert new_env["NEW"] == "canonical_val"
    assert report.unresolved_count() == 1


def test_canonical_overwritten_when_flag_set():
    new_env, report = run_alias(
        {"OLD": "alias_val", "NEW": "canonical_val"}, {"OLD": "NEW"}, overwrite=True
    )
    assert new_env["NEW"] == "alias_val"
    assert report.resolved_count() == 1


def test_original_env_not_mutated():
    original = {"OLD": "v"}
    run_alias(original, {"OLD": "NEW"})
    assert "OLD" in original


def test_resolved_keys_list():
    _, report = run_alias({"X": "1", "Y": "2"}, {"X": "X2", "Y": "Y2"})
    assert set(report.resolved_keys()) == {"X", "Y"}


# ---------------------------------------------------------------------------
# alias_reporter – formatting
# ---------------------------------------------------------------------------

def test_format_report_contains_header():
    _, report = run_alias({"OLD": "v"}, {"OLD": "NEW"})
    output = format_alias_report(report, use_color=False)
    assert "Alias Remapping Report" in output


def test_format_report_shows_alias_and_canonical():
    _, report = run_alias({"OLD_DB": "localhost"}, {"OLD_DB": "DB_HOST"})
    output = format_alias_report(report, use_color=False)
    assert "OLD_DB" in output
    assert "DB_HOST" in output


def test_format_empty_report_shows_no_aliases_message():
    report = AliasReport()
    output = format_alias_report(report, use_color=False)
    assert "No aliases processed" in output


def test_format_report_shows_resolved_count():
    _, report = run_alias({"A": "1"}, {"A": "A_CANONICAL"})
    output = format_alias_report(report, use_color=False)
    assert "Remapped: 1" in output
