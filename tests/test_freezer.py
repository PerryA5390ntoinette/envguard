"""Tests for envguard.freezer."""
from __future__ import annotations

import pytest

from envguard.freezer import (
    FreezeEntry,
    FreezeReport,
    _hash_value,
    check_freeze,
    freeze_env,
)


# ---------------------------------------------------------------------------
# _hash_value
# ---------------------------------------------------------------------------

def test_hash_value_is_16_hex_chars():
    h = _hash_value("hello")
    assert len(h) == 16
    assert all(c in "0123456789abcdef" for c in h)


def test_hash_value_is_deterministic():
    assert _hash_value("same") == _hash_value("same")


def test_hash_value_differs_for_different_input():
    assert _hash_value("foo") != _hash_value("bar")


# ---------------------------------------------------------------------------
# freeze_env
# ---------------------------------------------------------------------------

def test_freeze_env_returns_dict_with_same_keys():
    env = {"A": "1", "B": "2"}
    manifest = freeze_env(env)
    assert set(manifest.keys()) == {"A", "B"}


def test_freeze_env_values_are_hashes():
    env = {"KEY": "value"}
    manifest = freeze_env(env)
    assert manifest["KEY"] == _hash_value("value")


def test_freeze_env_empty_input():
    assert freeze_env({}) == {}


# ---------------------------------------------------------------------------
# check_freeze — no drift
# ---------------------------------------------------------------------------

def test_stable_key_not_flagged():
    env = {"PORT": "8080"}
    manifest = freeze_env(env)
    report = check_freeze(env, manifest)
    assert report.drifted_count == 0
    assert report.stable_count == 1


def test_no_drift_returns_has_drift_false():
    env = {"A": "x", "B": "y"}
    manifest = freeze_env(env)
    report = check_freeze(env, manifest)
    assert not report.has_drift


# ---------------------------------------------------------------------------
# check_freeze — with drift
# ---------------------------------------------------------------------------

def test_changed_value_flagged_as_drifted():
    manifest = freeze_env({"SECRET": "original"})
    report = check_freeze({"SECRET": "changed"}, manifest)
    assert report.has_drift
    assert "SECRET" in report.drifted_keys


def test_removed_key_flagged_as_drifted():
    manifest = freeze_env({"GONE": "value"})
    report = check_freeze({}, manifest)
    assert "GONE" in report.drifted_keys


def test_new_key_flagged_by_default():
    manifest = freeze_env({"OLD": "v"})
    report = check_freeze({"OLD": "v", "NEW": "n"}, manifest)
    new_entry = next(e for e in report.entries if e.key == "NEW")
    assert new_entry.drifted


def test_new_key_ignored_when_ignore_new_true():
    manifest = freeze_env({"OLD": "v"})
    report = check_freeze({"OLD": "v", "NEW": "n"}, manifest, ignore_new=True)
    assert all(e.key != "NEW" for e in report.entries)


# ---------------------------------------------------------------------------
# FreezeReport properties
# ---------------------------------------------------------------------------

def test_drifted_keys_lists_only_drifted():
    manifest = freeze_env({"A": "1", "B": "2"})
    report = check_freeze({"A": "1", "B": "changed"}, manifest)
    assert report.drifted_keys == ["B"]


def test_stable_and_drifted_counts_sum_to_total():
    env = {"X": "a", "Y": "b", "Z": "c"}
    manifest = freeze_env(env)
    modified = {**env, "Y": "different"}
    report = check_freeze(modified, manifest)
    assert report.stable_count + report.drifted_count == len(report.entries)
