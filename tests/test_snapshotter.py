"""Tests for envguard.snapshotter."""
import json
import os
import tempfile

import pytest

from envguard.snapshotter import (
    Snapshot,
    SnapshotDiff,
    diff_snapshots,
    load_snapshot,
    save_snapshot,
    take_snapshot,
)


ENV_A = {"DB_HOST": "localhost", "DB_PORT": "5432", "SECRET": "abc"}
ENV_B = {"DB_HOST": "prod.db", "DB_PORT": "5432", "API_KEY": "xyz"}


def test_take_snapshot_stores_env():
    snap = take_snapshot(ENV_A, source="test.env")
    assert snap.env == ENV_A


def test_take_snapshot_records_source():
    snap = take_snapshot(ENV_A, source="test.env")
    assert snap.source == "test.env"


def test_take_snapshot_has_timestamp():
    snap = take_snapshot(ENV_A, source="test.env")
    assert snap.timestamp  # non-empty string


def test_snapshot_round_trips_via_dict():
    snap = take_snapshot(ENV_A, source="test.env")
    restored = Snapshot.from_dict(snap.to_dict())
    assert restored.env == snap.env
    assert restored.source == snap.source
    assert restored.timestamp == snap.timestamp


def test_save_and_load_snapshot(tmp_path):
    snap = take_snapshot(ENV_A, source="test.env")
    path = str(tmp_path / "snap.json")
    save_snapshot(snap, path)
    loaded = load_snapshot(path)
    assert loaded.env == snap.env
    assert loaded.source == snap.source


def test_save_snapshot_creates_valid_json(tmp_path):
    snap = take_snapshot(ENV_A, source="test.env")
    path = str(tmp_path / "snap.json")
    save_snapshot(snap, path)
    with open(path) as fh:
        data = json.load(fh)
    assert "env" in data
    assert "timestamp" in data
    assert "source" in data


def test_diff_detects_added_key():
    old = take_snapshot(ENV_A, source="old.env")
    new = take_snapshot(ENV_B, source="new.env")
    diff = diff_snapshots(old, new)
    assert "API_KEY" in diff.added


def test_diff_detects_removed_key():
    old = take_snapshot(ENV_A, source="old.env")
    new = take_snapshot(ENV_B, source="new.env")
    diff = diff_snapshots(old, new)
    assert "SECRET" in diff.removed


def test_diff_detects_changed_key():
    old = take_snapshot(ENV_A, source="old.env")
    new = take_snapshot(ENV_B, source="new.env")
    diff = diff_snapshots(old, new)
    assert "DB_HOST" in diff.changed
    assert diff.changed["DB_HOST"] == ("localhost", "prod.db")


def test_diff_detects_unchanged_key():
    old = take_snapshot(ENV_A, source="old.env")
    new = take_snapshot(ENV_B, source="new.env")
    diff = diff_snapshots(old, new)
    assert "DB_PORT" in diff.unchanged


def test_diff_has_changes_true_when_differences():
    old = take_snapshot(ENV_A, source="old.env")
    new = take_snapshot(ENV_B, source="new.env")
    diff = diff_snapshots(old, new)
    assert diff.has_changes is True


def test_diff_has_changes_false_for_identical_envs():
    old = take_snapshot(ENV_A, source="old.env")
    new = take_snapshot(ENV_A, source="new.env")
    diff = diff_snapshots(old, new)
    assert diff.has_changes is False
