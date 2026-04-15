"""Tests for envguard.pinner."""
from __future__ import annotations

import json
import os
import tempfile

import pytest

from envguard.pinner import (
    PinEntry,
    PinReport,
    _checksum,
    pin_env,
    save_pinfile,
    load_pinfile,
    detect_drift,
)


# ---------------------------------------------------------------------------
# _checksum
# ---------------------------------------------------------------------------

def test_checksum_is_16_hex_chars():
    cs = _checksum("hello")
    assert len(cs) == 16
    assert all(c in "0123456789abcdef" for c in cs)


def test_checksum_same_value_is_deterministic():
    assert _checksum("value") == _checksum("value")


def test_checksum_different_values_differ():
    assert _checksum("a") != _checksum("b")


# ---------------------------------------------------------------------------
# pin_env
# ---------------------------------------------------------------------------

def test_pin_env_returns_pin_report():
    report = pin_env({"FOO": "bar"})
    assert isinstance(report, PinReport)


def test_pin_env_count_matches_input():
    env = {"A": "1", "B": "2", "C": "3"}
    report = pin_env(env)
    assert report.pinned_count() == 3


def test_pin_env_source_stored():
    report = pin_env({"X": "y"}, source=".env.prod")
    assert report.source == ".env.prod"


def test_pin_env_entries_sorted_by_key():
    env = {"Z": "z", "A": "a", "M": "m"}
    report = pin_env(env)
    keys = [e.key for e in report.entries]
    assert keys == sorted(keys)


def test_pin_env_checksum_matches_value():
    env = {"SECRET": "topsecret"}
    report = pin_env(env)
    entry = report.entries[0]
    assert entry.checksum == _checksum("topsecret")


def test_pin_env_as_dict_returns_key_value_map():
    env = {"FOO": "bar", "BAZ": "qux"}
    report = pin_env(env)
    assert report.as_dict() == env


# ---------------------------------------------------------------------------
# save / load pinfile
# ---------------------------------------------------------------------------

def test_save_and_load_pinfile_roundtrip():
    env = {"DB_HOST": "localhost", "DB_PORT": "5432"}
    report = pin_env(env, source=".env")
    with tempfile.NamedTemporaryFile(suffix=".lock", delete=False) as fh:
        path = fh.name
    try:
        save_pinfile(report, path)
        loaded = load_pinfile(path)
        assert loaded.source == report.source
        assert loaded.pinned_count() == report.pinned_count()
        assert loaded.as_dict() == report.as_dict()
    finally:
        os.unlink(path)


def test_saved_pinfile_is_valid_json():
    env = {"KEY": "val"}
    report = pin_env(env)
    with tempfile.NamedTemporaryFile(suffix=".lock", delete=False, mode="w") as fh:
        path = fh.name
    try:
        save_pinfile(report, path)
        with open(path) as fh:
            data = json.load(fh)
        assert "pins" in data
    finally:
        os.unlink(path)


# ---------------------------------------------------------------------------
# detect_drift
# ---------------------------------------------------------------------------

def test_no_drift_when_values_unchanged():
    env = {"FOO": "bar"}
    report = pin_env(env)
    drifts = detect_drift(report, env)
    assert drifts == []


def test_drift_detected_when_value_changes():
    report = pin_env({"FOO": "original"})
    drifts = detect_drift(report, {"FOO": "changed"})
    assert len(drifts) == 1
    assert drifts[0].key == "FOO"


def test_drift_entry_contains_both_values():
    report = pin_env({"API_KEY": "old"})
    drifts = detect_drift(report, {"API_KEY": "new"})
    assert drifts[0].pinned_value == "old"
    assert drifts[0].current_value == "new"


def test_new_key_in_current_env_not_reported_as_drift():
    report = pin_env({"A": "1"})
    drifts = detect_drift(report, {"A": "1", "B": "2"})
    assert drifts == []


def test_multiple_drifts_all_detected():
    report = pin_env({"X": "1", "Y": "2", "Z": "3"})
    current = {"X": "changed", "Y": "2", "Z": "also_changed"}
    drifts = detect_drift(report, current)
    drifted_keys = {d.key for d in drifts}
    assert drifted_keys == {"X", "Z"}
