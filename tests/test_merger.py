"""Tests for envguard.merger module."""

import pytest
from envguard.merger import merge_envs, MergeConflict, MergeReport


def run_merge(env_maps, strategy="last-wins", detect_conflicts=True):
    return merge_envs(env_maps, strategy=strategy, detect_conflicts=detect_conflicts)


# --- Basic merging ---

def test_single_source_no_conflicts():
    report = run_merge([("a.env", {"FOO": "1", "BAR": "2"})])
    assert report.merged == {"FOO": "1", "BAR": "2"}
    assert not report.has_conflicts


def test_two_sources_non_overlapping_keys():
    report = run_merge([("a.env", {"FOO": "1"}), ("b.env", {"BAR": "2"})])
    assert report.merged == {"FOO": "1", "BAR": "2"}
    assert not report.has_conflicts


def test_sources_list_populated():
    report = run_merge([("a.env", {}), ("b.env", {})])
    assert report.sources == ["a.env", "b.env"]


# --- Conflict detection ---

def test_conflict_detected_for_differing_values():
    report = run_merge([
        ("a.env", {"FOO": "old"}),
        ("b.env", {"FOO": "new"}),
    ])
    assert report.has_conflicts
    assert len(report.conflicts) == 1
    assert report.conflicts[0].key == "FOO"


def test_conflict_values_contain_both_sources():
    report = run_merge([
        ("a.env", {"FOO": "old"}),
        ("b.env", {"FOO": "new"}),
    ])
    conflict = report.conflicts[0]
    sources = [s for s, _ in conflict.values]
    assert "a.env" in sources
    assert "b.env" in sources


def test_no_conflict_when_same_value_in_both_sources():
    report = run_merge([
        ("a.env", {"FOO": "same"}),
        ("b.env", {"FOO": "same"}),
    ])
    assert not report.has_conflicts


def test_detect_conflicts_false_suppresses_conflict_list():
    report = run_merge(
        [("a.env", {"FOO": "old"}), ("b.env", {"FOO": "new"})],
        detect_conflicts=False,
    )
    assert not report.has_conflicts


# --- Strategy ---

def test_last_wins_strategy():
    report = run_merge([
        ("a.env", {"FOO": "first"}),
        ("b.env", {"FOO": "second"}),
    ], strategy="last-wins")
    assert report.merged["FOO"] == "second"


def test_first_wins_strategy():
    report = run_merge([
        ("a.env", {"FOO": "first"}),
        ("b.env", {"FOO": "second"}),
    ], strategy="first-wins")
    assert report.merged["FOO"] == "first"


# --- Three sources ---

def test_three_sources_conflict_accumulates():
    report = run_merge([
        ("a.env", {"KEY": "v1"}),
        ("b.env", {"KEY": "v2"}),
        ("c.env", {"KEY": "v3"}),
    ])
    assert report.has_conflicts
    conflict = report.conflicts[0]
    assert len(conflict.values) == 3


def test_empty_env_maps_returns_empty_report():
    report = run_merge([])
    assert report.merged == {}
    assert not report.has_conflicts
    assert report.sources == []
