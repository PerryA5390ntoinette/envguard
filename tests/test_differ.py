"""Tests for envguard.differ module."""

from unittest.mock import patch

import pytest

from envguard.differ import DiffEntry, DiffReport, diff_env_files


BASE_ENV = {"HOST": "localhost", "PORT": "5432", "DEBUG": "true"}
TARGET_ENV = {"HOST": "prod.example.com", "PORT": "5432", "LOG_LEVEL": "info"}


def run_diff(base: dict, target: dict) -> DiffReport:
    with patch("envguard.differ.load_env_file", side_effect=[base, target]):
        return diff_env_files(".env.base", ".env.target")


def test_added_key_detected():
    report = run_diff(BASE_ENV, TARGET_ENV)
    keys = [e.key for e in report.added]
    assert "LOG_LEVEL" in keys


def test_removed_key_detected():
    report = run_diff(BASE_ENV, TARGET_ENV)
    keys = [e.key for e in report.removed]
    assert "DEBUG" in keys


def test_changed_key_detected():
    report = run_diff(BASE_ENV, TARGET_ENV)
    keys = [e.key for e in report.changed]
    assert "HOST" in keys


def test_unchanged_key_detected():
    report = run_diff(BASE_ENV, TARGET_ENV)
    keys = [e.key for e in report.unchanged]
    assert "PORT" in keys


def test_changed_entry_has_old_and_new_values():
    report = run_diff(BASE_ENV, TARGET_ENV)
    changed = {e.key: e for e in report.changed}
    assert changed["HOST"].old_value == "localhost"
    assert changed["HOST"].new_value == "prod.example.com"


def test_added_entry_has_no_old_value():
    report = run_diff(BASE_ENV, TARGET_ENV)
    added = {e.key: e for e in report.added}
    assert added["LOG_LEVEL"].old_value is None
    assert added["LOG_LEVEL"].new_value == "info"


def test_removed_entry_has_no_new_value():
    report = run_diff(BASE_ENV, TARGET_ENV)
    removed = {e.key: e for e in report.removed}
    assert removed["DEBUG"].new_value is None
    assert removed["DEBUG"].old_value == "true"


def test_has_differences_true_when_changes_exist():
    report = run_diff(BASE_ENV, TARGET_ENV)
    assert report.has_differences is True


def test_has_differences_false_when_identical():
    report = run_diff(BASE_ENV, BASE_ENV)
    assert report.has_differences is False


def test_identical_envs_produce_only_unchanged():
    report = run_diff(BASE_ENV, BASE_ENV)
    assert len(report.added) == 0
    assert len(report.removed) == 0
    assert len(report.changed) == 0
    assert len(report.unchanged) == len(BASE_ENV)


def test_empty_base_all_added():
    report = run_diff({}, TARGET_ENV)
    assert len(report.added) == len(TARGET_ENV)
    assert report.removed == []
    assert report.changed == []


def test_empty_target_all_removed():
    report = run_diff(BASE_ENV, {})
    assert len(report.removed) == len(BASE_ENV)
    assert report.added == []
    assert report.changed == []
