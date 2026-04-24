"""Tests for envguard.inheritor."""
import pytest
from envguard.inheritor import inherit_env, InheritReport


def run_inherit(base, override):
    env, report = inherit_env(base, override)
    return env, report


def test_returns_tuple_of_env_and_report():
    env, report = run_inherit({}, {})
    assert isinstance(env, dict)
    assert isinstance(report, InheritReport)


def test_empty_inputs_produce_empty_report():
    env, report = run_inherit({}, {})
    assert env == {}
    assert report.entries == []


def test_base_only_key_is_inherited():
    env, report = run_inherit({"FOO": "bar"}, {})
    assert env["FOO"] == "bar"
    assert report.inherited_count == 1
    assert report.overridden_count == 0
    assert report.added_count == 0


def test_override_only_key_is_added():
    env, report = run_inherit({}, {"NEW_KEY": "value"})
    assert env["NEW_KEY"] == "value"
    assert report.added_count == 1
    assert report.inherited_count == 0
    assert report.overridden_count == 0


def test_shared_key_uses_override_value():
    env, report = run_inherit({"DB_HOST": "localhost"}, {"DB_HOST": "prod.db"})
    assert env["DB_HOST"] == "prod.db"


def test_shared_key_marked_overridden():
    _, report = run_inherit({"DB_HOST": "localhost"}, {"DB_HOST": "prod.db"})
    assert report.overridden_count == 1


def test_shared_key_source_is_merged():
    _, report = run_inherit({"X": "1"}, {"X": "2"})
    entry = next(e for e in report.entries if e.key == "X")
    assert entry.source == "merged"
    assert entry.overridden is True


def test_base_only_entry_source_is_base():
    _, report = run_inherit({"ONLY_BASE": "v"}, {})
    entry = report.entries[0]
    assert entry.source == "base"
    assert entry.overridden is False


def test_override_only_entry_source_is_override():
    _, report = run_inherit({}, {"ONLY_OV": "v"})
    entry = report.entries[0]
    assert entry.source == "override"
    assert entry.overridden is False


def test_result_env_contains_all_keys():
    env, _ = run_inherit({"A": "1", "B": "2"}, {"B": "99", "C": "3"})
    assert set(env.keys()) == {"A", "B", "C"}


def test_original_dicts_not_mutated():
    base = {"A": "1"}
    override = {"B": "2"}
    run_inherit(base, override)
    assert base == {"A": "1"}
    assert override == {"B": "2"}


def test_mixed_scenario_counts():
    base = {"SHARED": "old", "BASE_ONLY": "x"}
    override = {"SHARED": "new", "OV_ONLY": "y"}
    _, report = run_inherit(base, override)
    assert report.inherited_count == 1
    assert report.overridden_count == 1
    assert report.added_count == 1
