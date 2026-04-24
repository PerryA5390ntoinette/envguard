"""Tests for envguard.padder."""

import pytest
from envguard.padder import pad_env, PadReport, PadEntry, DEFAULT_PLACEHOLDER


def run_pad(env, keys, placeholder=None):
    if placeholder is not None:
        return pad_env(env, keys, placeholder=placeholder)
    return pad_env(env, keys)


def test_returns_tuple_of_env_and_report():
    result_env, report = run_pad({}, [])
    assert isinstance(result_env, dict)
    assert isinstance(report, PadReport)


def test_empty_keys_produces_empty_report():
    _, report = run_pad({"A": "1"}, [])
    assert report.padded_count() == 0
    assert report.kept_count() == 0
    assert report.entries == []


def test_present_key_is_kept_not_padded():
    env, report = run_pad({"A": "hello"}, ["A"])
    assert report.kept_count() == 1
    assert report.padded_count() == 0
    assert env["A"] == "hello"


def test_missing_key_is_padded_with_default():
    env, report = run_pad({}, ["MISSING_KEY"])
    assert report.padded_count() == 1
    assert env["MISSING_KEY"] == DEFAULT_PLACEHOLDER


def test_missing_key_uses_custom_placeholder():
    env, report = run_pad({}, ["MY_VAR"], placeholder="TODO")
    assert env["MY_VAR"] == "TODO"


def test_padded_keys_lists_only_missing():
    env = {"A": "1"}
    _, report = run_pad(env, ["A", "B", "C"])
    assert set(report.padded_keys()) == {"B", "C"}


def test_original_env_not_mutated():
    original = {"A": "1"}
    run_pad(original, ["A", "B"])
    assert "B" not in original


def test_existing_value_preserved_in_result():
    env, _ = run_pad({"PORT": "8080"}, ["PORT", "HOST"])
    assert env["PORT"] == "8080"


def test_entry_was_present_flag_true_for_existing_key():
    _, report = run_pad({"X": "val"}, ["X"])
    entry = report.entries[0]
    assert entry.was_present is True


def test_entry_was_present_flag_false_for_missing_key():
    _, report = run_pad({}, ["X"])
    entry = report.entries[0]
    assert entry.was_present is False


def test_mixed_env_counts_correct():
    env = {"A": "1", "B": "2"}
    _, report = run_pad(env, ["A", "B", "C", "D"])
    assert report.kept_count() == 2
    assert report.padded_count() == 2


def test_entry_placeholder_stored_on_entry():
    _, report = run_pad({}, ["KEY"], placeholder="FILL_ME")
    assert report.entries[0].placeholder == "FILL_ME"


def test_all_entries_recorded_in_order():
    keys = ["Z", "A", "M"]
    _, report = run_pad({"A": "x"}, keys)
    recorded_keys = [e.key for e in report.entries]
    assert recorded_keys == keys
