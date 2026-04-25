"""Tests for envguard.cloner."""
import pytest
from envguard.cloner import clone_env, CloneReport, CloneEntry


def run_clone(env, key_map=None, overrides=None):
    return clone_env(env, key_map=key_map, overrides=overrides)


def test_returns_tuple_of_env_and_report():
    result = run_clone({"A": "1"})
    assert isinstance(result, tuple)
    assert len(result) == 2


def test_report_is_clone_report_instance():
    _, report = run_clone({"A": "1"})
    assert isinstance(report, CloneReport)


def test_empty_env_produces_empty_report():
    env, report = run_clone({})
    assert report.total == 0
    assert env == {}


def test_simple_clone_preserves_key_and_value():
    env, report = run_clone({"HOST": "localhost"})
    assert env["HOST"] == "localhost"
    assert report.total == 1


def test_cloned_env_contains_all_keys():
    source = {"A": "1", "B": "2", "C": "3"}
    env, report = run_clone(source)
    assert set(env.keys()) == {"A", "B", "C"}


def test_key_map_renames_key():
    env, report = run_clone({"OLD_KEY": "value"}, key_map={"OLD_KEY": "NEW_KEY"})
    assert "NEW_KEY" in env
    assert "OLD_KEY" not in env


def test_key_map_preserves_value():
    env, _ = run_clone({"OLD_KEY": "myvalue"}, key_map={"OLD_KEY": "NEW_KEY"})
    assert env["NEW_KEY"] == "myvalue"


def test_remapped_entry_sets_was_remapped_true():
    _, report = run_clone({"OLD": "v"}, key_map={"OLD": "NEW"})
    entry = report.entries[0]
    assert entry.was_remapped is True


def test_non_remapped_entry_sets_was_remapped_false():
    _, report = run_clone({"KEY": "v"})
    assert report.entries[0].was_remapped is False


def test_remapped_count_correct():
    _, report = run_clone(
        {"A": "1", "B": "2"},
        key_map={"A": "A2"}
    )
    assert report.remapped_count == 1


def test_override_replaces_value():
    env, _ = run_clone({"PORT": "8080"}, overrides={"PORT": "9090"})
    assert env["PORT"] == "9090"


def test_overridden_entry_sets_was_overridden_true():
    _, report = run_clone({"PORT": "8080"}, overrides={"PORT": "9090"})
    assert report.entries[0].was_overridden is True


def test_non_overridden_entry_sets_was_overridden_false():
    _, report = run_clone({"PORT": "8080"})
    assert report.entries[0].was_overridden is False


def test_overridden_count_correct():
    _, report = run_clone(
        {"A": "1", "B": "2"},
        overrides={"B": "99"}
    )
    assert report.overridden_count == 1


def test_remap_then_override_applies_to_new_key():
    env, report = run_clone(
        {"OLD": "original"},
        key_map={"OLD": "NEW"},
        overrides={"NEW": "replaced"}
    )
    assert env["NEW"] == "replaced"
    entry = report.entries[0]
    assert entry.was_remapped is True
    assert entry.was_overridden is True


def test_original_env_not_mutated():
    source = {"A": "1"}
    run_clone(source, key_map={"A": "B"}, overrides={"B": "99"})
    assert source == {"A": "1"}


def test_result_env_from_report_matches_returned_env():
    env, report = run_clone({"X": "10", "Y": "20"})
    assert env == report.result_env
