"""Tests for envguard.mapper."""
import pytest
from envguard.mapper import map_env, MapReport


def run_map(env, mapping, **kwargs):
    return map_env(env, mapping, **kwargs)


# ---------------------------------------------------------------------------
# Basic behaviour
# ---------------------------------------------------------------------------

def test_returns_tuple_of_env_and_report():
    env, report = run_map({}, {})
    assert isinstance(env, dict)
    assert isinstance(report, MapReport)


def test_empty_env_produces_empty_report():
    _, report = run_map({}, {"OLD": "NEW"})
    assert report.entries == []


def test_simple_remap_changes_key():
    env, report = run_map({"OLD_KEY": "value"}, {"OLD_KEY": "NEW_KEY"})
    assert "NEW_KEY" in env
    assert env["NEW_KEY"] == "value"


def test_original_key_removed_after_remap():
    env, _ = run_map({"OLD_KEY": "value"}, {"OLD_KEY": "NEW_KEY"})
    assert "OLD_KEY" not in env


def test_remapped_value_preserved():
    env, _ = run_map({"A": "hello"}, {"A": "B"})
    assert env["B"] == "hello"


def test_unmapped_key_kept_by_default():
    env, _ = run_map({"UNRELATED": "x"}, {})
    assert "UNRELATED" in env


def test_unmapped_key_dropped_when_keep_false():
    env, _ = run_map({"UNRELATED": "x"}, {}, keep_unmapped=False)
    assert "UNRELATED" not in env


def test_multiple_remaps():
    src = {"A": "1", "B": "2", "C": "3"}
    mapping = {"A": "X", "B": "Y"}
    env, report = run_map(src, mapping)
    assert env["X"] == "1"
    assert env["Y"] == "2"
    assert env["C"] == "3"  # kept


# ---------------------------------------------------------------------------
# Counts
# ---------------------------------------------------------------------------

def test_remapped_count():
    _, report = run_map({"A": "1", "B": "2"}, {"A": "X"})
    assert report.remapped_count() == 1


def test_skipped_count():
    _, report = run_map({"A": "1", "B": "2"}, {"A": "X"})
    assert report.skipped_count() == 1


def test_remapped_keys_list():
    _, report = run_map({"A": "1", "B": "2"}, {"A": "X", "B": "Y"})
    assert sorted(report.remapped_keys()) == ["A", "B"]


def test_no_remaps_when_mapping_empty():
    _, report = run_map({"A": "1"}, {})
    assert report.remapped_count() == 0
    assert report.skipped_count() == 1


# ---------------------------------------------------------------------------
# result_env helper
# ---------------------------------------------------------------------------

def test_result_env_matches_returned_dict():
    env, report = run_map({"K": "v"}, {"K": "NEW_K"})
    assert env == report.result_env()


def test_entry_remapped_flag_true_for_mapped_key():
    _, report = run_map({"A": "1"}, {"A": "B"})
    entry = report.entries[0]
    assert entry.remapped is True
    assert entry.original_key == "A"
    assert entry.new_key == "B"


def test_entry_remapped_flag_false_for_unmapped_key():
    _, report = run_map({"A": "1"}, {})
    entry = report.entries[0]
    assert entry.remapped is False
    assert entry.original_key == "A"
    assert entry.new_key == "A"
