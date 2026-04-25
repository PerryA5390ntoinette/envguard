"""Tests for envguard.pruner."""
import pytest
from envguard.pruner import prune_env, PruneReport


def run_prune(env, *, keys=None, patterns=None):
    return prune_env(env, keys=keys, patterns=patterns)


# --- return types ---

def test_returns_tuple_of_env_and_report():
    env, report = run_prune({"A": "1"})
    assert isinstance(env, dict)
    assert isinstance(report, PruneReport)


def test_empty_env_produces_empty_report():
    env, report = run_prune({})
    assert report.pruned_count() == 0
    assert report.kept_count() == 0


# --- explicit key pruning ---

def test_explicit_key_is_pruned():
    env, report = run_prune({"SECRET": "abc", "HOST": "localhost"}, keys=["SECRET"])
    assert "SECRET" not in env
    assert "HOST" in env


def test_explicit_key_reason_is_explicit():
    _, report = run_prune({"TOKEN": "x"}, keys=["TOKEN"])
    entry = report.entries[0]
    assert entry.reason == "explicit"
    assert entry.pruned is True


def test_explicit_key_not_in_env_does_not_error():
    env, report = run_prune({"A": "1"}, keys=["MISSING"])
    assert env == {"A": "1"}
    assert report.pruned_count() == 0


# --- pattern pruning ---

def test_pattern_prunes_matching_key():
    env, report = run_prune({"DB_PASSWORD": "s3cr3t", "DB_HOST": "localhost"}, patterns=[".*PASSWORD"])
    assert "DB_PASSWORD" not in env
    assert "DB_HOST" in env


def test_pattern_reason_is_pattern():
    _, report = run_prune({"API_KEY": "abc"}, patterns=["API_.*"])
    pruned = [e for e in report.entries if e.pruned]
    assert pruned[0].reason == "pattern"


def test_pattern_non_matching_key_kept():
    env, _ = run_prune({"PORT": "8080"}, patterns=[".*SECRET.*"])
    assert "PORT" in env


# --- counts ---

def test_pruned_count_correct():
    _, report = run_prune({"A": "1", "B": "2", "C": "3"}, keys=["A", "C"])
    assert report.pruned_count() == 2


def test_kept_count_correct():
    _, report = run_prune({"A": "1", "B": "2"}, keys=["A"])
    assert report.kept_count() == 1


def test_pruned_keys_list():
    _, report = run_prune({"X": "1", "Y": "2"}, keys=["X"])
    assert report.pruned_keys() == ["X"]


# --- result_env ---

def test_result_env_excludes_pruned():
    env, report = run_prune({"KEEP": "yes", "DROP": "no"}, keys=["DROP"])
    assert env == {"KEEP": "yes"}


def test_original_env_not_mutated():
    original = {"A": "1", "B": "2"}
    prune_env(original, keys=["A"])
    assert "A" in original


# --- combined keys and patterns ---

def test_keys_and_patterns_combined():
    env, report = run_prune(
        {"SECRET": "s", "DB_PASS": "p", "HOST": "h"},
        keys=["SECRET"],
        patterns=["DB_.*"],
    )
    assert "SECRET" not in env
    assert "DB_PASS" not in env
    assert "HOST" in env
    assert report.pruned_count() == 2
