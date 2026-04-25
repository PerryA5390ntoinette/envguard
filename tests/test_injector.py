"""Tests for envguard.injector."""
from __future__ import annotations

import os
import pytest

from envguard.injector import InjectionReport, inject_env


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

def run_inject(env, **kwargs):
    return inject_env(env, **kwargs)


# ---------------------------------------------------------------------------
# return type
# ---------------------------------------------------------------------------

def test_returns_tuple_of_env_and_report():
    result, report = run_inject({})
    assert isinstance(result, dict)
    assert isinstance(report, InjectionReport)


def test_empty_inputs_produce_empty_report():
    _, report = run_inject({})
    assert report.injected_count == 0


# ---------------------------------------------------------------------------
# defaults
# ---------------------------------------------------------------------------

def test_default_applied_when_key_absent():
    env, report = run_inject({}, defaults={"PORT": "8080"})
    assert env["PORT"] == "8080"
    assert report.injected_count == 1


def test_default_not_applied_when_key_present():
    env, report = run_inject({"PORT": "9000"}, defaults={"PORT": "8080"})
    assert env["PORT"] == "9000"
    assert report.injected_count == 0


def test_default_source_label_is_defaults():
    _, report = run_inject({}, defaults={"X": "1"})
    assert report.entries[0].source == "defaults"


# ---------------------------------------------------------------------------
# from_os
# ---------------------------------------------------------------------------

def test_os_key_injected_when_present_and_overwrite_true(monkeypatch):
    monkeypatch.setenv("MY_VAR", "hello")
    env, report = run_inject({"MY_VAR": "old"}, from_os=["MY_VAR"], overwrite=True)
    assert env["MY_VAR"] == "hello"
    assert report.entries[0].replaced is True


def test_os_key_not_injected_when_overwrite_false_and_key_exists(monkeypatch):
    monkeypatch.setenv("MY_VAR", "hello")
    env, report = run_inject({"MY_VAR": "old"}, from_os=["MY_VAR"], overwrite=False)
    assert env["MY_VAR"] == "old"
    assert report.injected_count == 0


def test_os_key_injected_when_absent_from_env(monkeypatch):
    monkeypatch.setenv("NEW_KEY", "value")
    env, report = run_inject({}, from_os=["NEW_KEY"])
    assert env["NEW_KEY"] == "value"
    assert report.entries[0].source == "os"


def test_missing_os_key_not_added(monkeypatch):
    monkeypatch.delenv("DEFINITELY_ABSENT", raising=False)
    env, report = run_inject({}, from_os=["DEFINITELY_ABSENT"])
    assert "DEFINITELY_ABSENT" not in env
    assert report.injected_count == 0


# ---------------------------------------------------------------------------
# overrides
# ---------------------------------------------------------------------------

def test_override_replaces_existing_value():
    env, report = run_inject({"KEY": "old"}, overrides={"KEY": "new"})
    assert env["KEY"] == "new"
    assert report.entries[0].replaced is True


def test_override_adds_new_key():
    env, report = run_inject({}, overrides={"EXTRA": "yes"})
    assert env["EXTRA"] == "yes"
    assert report.entries[0].replaced is False


def test_override_source_label_is_override():
    _, report = run_inject({}, overrides={"Z": "1"})
    assert report.entries[0].source == "override"


# ---------------------------------------------------------------------------
# aggregates
# ---------------------------------------------------------------------------

def test_replaced_count_correct():
    _, report = run_inject(
        {"A": "1"},
        defaults={"B": "2"},
        overrides={"A": "99"},
    )
    assert report.replaced_count == 1


def test_sources_used_lists_unique_sources():
    _, report = run_inject(
        {},
        defaults={"D": "1"},
        overrides={"O": "2"},
    )
    assert set(report.sources_used) == {"defaults", "override"}


def test_original_env_not_mutated():
    original = {"KEY": "original"}
    inject_env(original, overrides={"KEY": "changed"})
    assert original["KEY"] == "original"
