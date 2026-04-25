"""Tests for envguard.resolver."""
import pytest

from envguard.resolver import ResolveEntry, ResolveReport, resolve_layers


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

def run_resolve(layers, labels=None):
    return resolve_layers(layers, labels)


# ---------------------------------------------------------------------------
# basic structure
# ---------------------------------------------------------------------------

def test_returns_resolve_report_instance():
    report = run_resolve([{"A": "1"}])
    assert isinstance(report, ResolveReport)


def test_empty_layers_produce_empty_report():
    report = run_resolve([])
    assert report.resolved_count() == 0


def test_single_layer_all_keys_present():
    env = {"HOST": "localhost", "PORT": "5432"}
    report = run_resolve([env])
    assert report.resolved_count() == 2


def test_result_env_matches_single_layer():
    env = {"HOST": "localhost", "PORT": "5432"}
    report = run_resolve([env])
    assert report.result_env() == env


# ---------------------------------------------------------------------------
# source labelling
# ---------------------------------------------------------------------------

def test_source_label_defaults_to_layer_index():
    report = run_resolve([{"X": "1"}])
    entry = report.for_key("X")
    assert entry.source == "layer_0"


def test_custom_labels_applied():
    report = run_resolve([{"X": "1"}], labels=[".env.base"])
    entry = report.for_key("X")
    assert entry.source == ".env.base"


def test_sources_list_populated():
    report = run_resolve([{}, {}], labels=["base", "override"])
    assert report.sources == ["base", "override"]


def test_labels_length_mismatch_raises():
    with pytest.raises(ValueError):
        resolve_layers([{"A": "1"}, {"B": "2"}], labels=["only_one"])


# ---------------------------------------------------------------------------
# override detection
# ---------------------------------------------------------------------------

def test_later_layer_wins():
    report = run_resolve([{"KEY": "base"}, {"KEY": "override"}])
    entry = report.for_key("KEY")
    assert entry.value == "override"


def test_override_count_reflects_changed_keys():
    report = run_resolve(
        [{"A": "1", "B": "x"}, {"A": "2", "B": "x"}],
        labels=["base", "top"],
    )
    assert report.overridden_count() == 1


def test_overridden_by_set_on_entry():
    report = run_resolve([{"K": "old"}, {"K": "new"}], labels=["base", "top"])
    entry = report.for_key("K")
    assert entry.overridden_by == "top"


def test_original_value_stored_on_overridden_entry():
    report = run_resolve([{"K": "old"}, {"K": "new"}], labels=["base", "top"])
    entry = report.for_key("K")
    assert entry.original_value == "old"


def test_unchanged_key_has_no_override_info():
    report = run_resolve([{"K": "same"}, {"K": "same"}])
    entry = report.for_key("K")
    assert entry.overridden_by is None
    assert entry.original_value is None


# ---------------------------------------------------------------------------
# multi-layer merging
# ---------------------------------------------------------------------------

def test_keys_from_all_layers_present():
    report = run_resolve([{"A": "1"}, {"B": "2"}, {"C": "3"}])
    assert set(report.result_env().keys()) == {"A", "B", "C"}


def test_three_layer_override_final_wins():
    report = run_resolve(
        [{"X": "first"}, {"X": "second"}, {"X": "third"}],
        labels=["l1", "l2", "l3"],
    )
    assert report.result_env()["X"] == "third"


def test_for_key_returns_none_for_missing_key():
    report = run_resolve([{"A": "1"}])
    assert report.for_key("MISSING") is None
