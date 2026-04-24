"""Tests for envguard.tracer."""
import pytest
from envguard.tracer import TraceEntry, TraceReport, trace_envs


def run_trace(sources, names=None):
    if names is None:
        names = [f"source{i}" for i in range(len(sources))]
    return trace_envs(sources, names)


def test_single_source_all_keys_traced():
    report = run_trace([{"A": "1", "B": "2"}], ["base.env"])
    assert report.total == 2


def test_single_source_no_overrides():
    report = run_trace([{"A": "1"}], ["base.env"])
    assert report.overridden_count == 0


def test_all_keys_contains_unique_keys():
    report = run_trace([{"A": "1", "B": "2"}], ["base.env"])
    assert set(report.all_keys) == {"A", "B"}


def test_override_detected_across_two_sources():
    report = run_trace(
        [{"DB_HOST": "localhost"}, {"DB_HOST": "prod.db"}],
        ["base.env", "prod.env"],
    )
    assert report.overridden_count == 1


def test_final_value_reflects_last_source():
    report = run_trace(
        [{"X": "old"}, {"X": "new"}],
        ["a.env", "b.env"],
    )
    final_entries = report.for_key("X")
    last = final_entries[-1]
    assert last.value == "new"


def test_overridden_entry_records_previous_value():
    report = run_trace(
        [{"KEY": "alpha"}, {"KEY": "beta"}],
        ["first.env", "second.env"],
    )
    entries = report.for_key("KEY")
    overridden = [e for e in entries if e.was_overridden]
    assert len(overridden) == 1
    assert overridden[0].previous_value is None  # first entry has no prior
    assert entries[-1].previous_value == "alpha"


def test_non_overlapping_keys_no_overrides():
    report = run_trace(
        [{"A": "1"}, {"B": "2"}],
        ["x.env", "y.env"],
    )
    assert report.overridden_count == 0
    assert set(report.all_keys) == {"A", "B"}


def test_for_key_returns_all_entries_for_key():
    report = run_trace(
        [{"PORT": "3000"}, {"PORT": "8080"}, {"PORT": "9090"}],
        ["dev.env", "staging.env", "prod.env"],
    )
    entries = report.for_key("PORT")
    assert len(entries) == 3


def test_source_name_recorded_on_entry():
    report = run_trace([{"TOKEN": "abc"}], ["secrets.env"])
    entries = report.for_key("TOKEN")
    assert any(e.source == "secrets.env" for e in entries)


def test_empty_sources_returns_empty_report():
    report = run_trace([], [])
    assert report.total == 0
    assert report.all_keys == []


def test_trace_entry_was_overridden_false_by_default():
    entry = TraceEntry(key="K", value="v", source="x.env")
    assert not entry.was_overridden


def test_trace_entry_was_overridden_true_when_set():
    entry = TraceEntry(key="K", value="v", source="x.env", overridden_by="y.env")
    assert entry.was_overridden
