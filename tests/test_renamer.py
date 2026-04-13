"""Tests for envguard.renamer."""
from __future__ import annotations

import pytest

from envguard.renamer import rename_vars, RenameEntry, RenameReport


def run_rename(env, renames, overwrite=False):
    return rename_vars(env, renames, overwrite=overwrite)


# ---------------------------------------------------------------------------
# Basic rename behaviour
# ---------------------------------------------------------------------------

def test_simple_rename_moves_key():
    new_env, _ = run_rename({"OLD_KEY": "hello"}, {"OLD_KEY": "NEW_KEY"})
    assert "NEW_KEY" in new_env
    assert "OLD_KEY" not in new_env


def test_renamed_value_preserved():
    new_env, _ = run_rename({"OLD_KEY": "my_value"}, {"OLD_KEY": "NEW_KEY"})
    assert new_env["NEW_KEY"] == "my_value"


def test_unrelated_keys_untouched():
    new_env, _ = run_rename({"OLD": "v", "OTHER": "x"}, {"OLD": "NEW"})
    assert new_env["OTHER"] == "x"


def test_original_env_not_mutated():
    env = {"OLD": "v"}
    run_rename(env, {"OLD": "NEW"})
    assert "OLD" in env  # original unchanged


# ---------------------------------------------------------------------------
# Report contents
# ---------------------------------------------------------------------------

def test_report_entry_created_for_rename():
    _, report = run_rename({"A": "1"}, {"A": "B"})
    assert len(report.entries) == 1
    assert report.entries[0].old_name == "A"
    assert report.entries[0].new_name == "B"


def test_renamed_count_correct():
    _, report = run_rename({"A": "1", "C": "3"}, {"A": "B", "C": "D"})
    assert report.renamed_count() == 2


def test_skipped_count_zero_on_success():
    _, report = run_rename({"A": "1"}, {"A": "B"})
    assert report.skipped_count() == 0


# ---------------------------------------------------------------------------
# Missing source key
# ---------------------------------------------------------------------------

def test_missing_source_key_is_skipped():
    new_env, report = run_rename({"OTHER": "v"}, {"MISSING": "NEW"})
    assert report.skipped_count() == 1
    assert report.entries[0].skip_reason == "source key not found"


def test_missing_source_key_env_unchanged():
    new_env, _ = run_rename({"OTHER": "v"}, {"MISSING": "NEW"})
    assert new_env == {"OTHER": "v"}


# ---------------------------------------------------------------------------
# Conflict / overwrite
# ---------------------------------------------------------------------------

def test_existing_target_skipped_without_overwrite():
    env = {"OLD": "1", "NEW": "existing"}
    new_env, report = run_rename(env, {"OLD": "NEW"}, overwrite=False)
    assert report.skipped_count() == 1
    assert "OLD" in new_env  # old key still present
    assert new_env["NEW"] == "existing"  # target untouched


def test_existing_target_overwritten_when_flag_set():
    env = {"OLD": "fresh", "NEW": "stale"}
    new_env, report = run_rename(env, {"OLD": "NEW"}, overwrite=True)
    assert report.renamed_count() == 1
    assert new_env["NEW"] == "fresh"
    assert "OLD" not in new_env


def test_empty_renames_returns_identical_env():
    env = {"A": "1"}
    new_env, report = run_rename(env, {})
    assert new_env == env
    assert report.renamed_count() == 0
