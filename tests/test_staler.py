"""Tests for envguard.staler."""
import pytest
from envguard.staler import detect_stale, StaleReport, StaleEntry
from envguard.schema import EnvSchema, VariableSchema


def make_schema(*keys: str) -> EnvSchema:
    variables = {k: VariableSchema(name=k) for k in keys}
    return EnvSchema(variables=variables)


def test_empty_env_returns_empty_report():
    report = detect_stale({}, make_schema())
    assert isinstance(report, StaleReport)
    assert report.stale_count == 0


def test_known_key_not_flagged():
    schema = make_schema("DB_HOST")
    report = detect_stale({"DB_HOST": "localhost"}, schema)
    assert report.stale_count == 0


def test_unknown_key_flagged():
    schema = make_schema("DB_HOST")
    report = detect_stale({"DB_HOST": "localhost", "OLD_KEY": "val"}, schema)
    assert report.stale_count == 1
    assert report.stale_keys == ["OLD_KEY"]


def test_multiple_unknown_keys_all_flagged():
    schema = make_schema("A")
    env = {"A": "1", "B": "2", "C": "3"}
    report = detect_stale(env, schema)
    assert report.stale_count == 2
    assert set(report.stale_keys) == {"B", "C"}


def test_entry_has_correct_key_and_value():
    schema = make_schema()
    report = detect_stale({"GHOST": "haunted"}, schema)
    entry = report.entries[0]
    assert entry.key == "GHOST"
    assert entry.value == "haunted"


def test_entry_reason_populated():
    schema = make_schema()
    report = detect_stale({"X": "y"}, schema)
    assert report.entries[0].reason != ""


def test_allowlist_key_not_flagged():
    schema = make_schema()
    report = detect_stale({"LEGACY_KEY": "old"}, schema, allowlist=["LEGACY_KEY"])
    assert report.stale_count == 0


def test_has_stale_false_when_clean():
    schema = make_schema("Z")
    report = detect_stale({"Z": "1"}, schema)
    assert report.has_stale is False


def test_has_stale_true_when_stale():
    schema = make_schema()
    report = detect_stale({"OLD": "val"}, schema)
    assert report.has_stale is True


def test_original_env_not_mutated():
    env = {"A": "1", "B": "2"}
    schema = make_schema("A")
    detect_stale(env, schema)
    assert set(env.keys()) == {"A", "B"}
