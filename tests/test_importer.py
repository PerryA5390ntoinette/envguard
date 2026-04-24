"""Tests for envguard.importer."""
from __future__ import annotations

import json
import os
import tempfile

import pytest

from envguard.importer import (
    ImportEntry,
    ImportReport,
    import_from_json,
    import_from_shell,
    merge_into,
)


# ---------------------------------------------------------------------------
# import_from_shell
# ---------------------------------------------------------------------------

def test_shell_import_returns_tuple():
    env, report = import_from_shell(keys=[])
    assert isinstance(env, dict)
    assert isinstance(report, ImportReport)


def test_shell_import_specific_key(monkeypatch):
    monkeypatch.setenv("EG_TEST_VAR", "hello")
    env, report = import_from_shell(keys=["EG_TEST_VAR"])
    assert env.get("EG_TEST_VAR") == "hello"
    assert report.imported_count() == 1


def test_shell_import_key_not_in_env_is_skipped(monkeypatch):
    monkeypatch.delenv("EG_MISSING_KEY", raising=False)
    env, report = import_from_shell(keys=["EG_MISSING_KEY"])
    assert "EG_MISSING_KEY" not in env
    assert report.imported_count() == 0


def test_shell_import_prefix_filter(monkeypatch):
    monkeypatch.setenv("MYAPP_HOST", "localhost")
    monkeypatch.setenv("MYAPP_PORT", "5432")
    monkeypatch.setenv("OTHER_VAR", "nope")
    env, report = import_from_shell(prefix="MYAPP_")
    assert "MYAPP_HOST" in env
    assert "MYAPP_PORT" in env
    assert "OTHER_VAR" not in env


def test_shell_import_entry_source_is_shell(monkeypatch):
    monkeypatch.setenv("EG_SRC_CHECK", "val")
    _, report = import_from_shell(keys=["EG_SRC_CHECK"])
    assert report.entries[0].source == "shell"


def test_shell_import_result_env_matches_entries(monkeypatch):
    monkeypatch.setenv("EG_RESULT_ENV", "42")
    _, report = import_from_shell(keys=["EG_RESULT_ENV"])
    assert report.result_env()["EG_RESULT_ENV"] == "42"


# ---------------------------------------------------------------------------
# import_from_json
# ---------------------------------------------------------------------------

def _write_json(data: dict) -> str:
    fh = tempfile.NamedTemporaryFile(
        mode="w", suffix=".json", delete=False, encoding="utf-8"
    )
    json.dump(data, fh)
    fh.close()
    return fh.name


def test_json_import_returns_tuple():
    path = _write_json({"FOO": "bar"})
    env, report = import_from_json(path)
    assert isinstance(env, dict)
    assert isinstance(report, ImportReport)


def test_json_import_reads_string_value():
    path = _write_json({"DB_HOST": "localhost"})
    env, _ = import_from_json(path)
    assert env["DB_HOST"] == "localhost"


def test_json_import_converts_int_to_string():
    path = _write_json({"PORT": 5432})
    env, _ = import_from_json(path)
    assert env["PORT"] == "5432"


def test_json_import_skips_nested_objects():
    path = _write_json({"NESTED": {"a": 1}, "FLAT": "ok"})
    env, report = import_from_json(path)
    assert "NESTED" not in env
    assert "FLAT" in env
    assert "NESTED" in report.skipped


def test_json_import_prefix_filter():
    path = _write_json({"APP_NAME": "envguard", "APP_ENV": "prod", "OTHER": "x"})
    env, report = import_from_json(path, prefix="APP_")
    assert "APP_NAME" in env
    assert "OTHER" not in env


def test_json_import_entry_source_is_json():
    path = _write_json({"KEY": "val"})
    _, report = import_from_json(path)
    assert report.entries[0].source == "json"


# ---------------------------------------------------------------------------
# merge_into
# ---------------------------------------------------------------------------

def test_merge_into_adds_new_keys():
    result = merge_into({"A": "1"}, {"B": "2"})
    assert result["B"] == "2"


def test_merge_into_does_not_overwrite_by_default():
    result = merge_into({"A": "original"}, {"A": "new"})
    assert result["A"] == "original"


def test_merge_into_overwrites_when_flag_set():
    result = merge_into({"A": "original"}, {"A": "new"}, overwrite=True)
    assert result["A"] == "new"


def test_merge_into_does_not_mutate_base():
    base = {"A": "1"}
    merge_into(base, {"B": "2"})
    assert "B" not in base
