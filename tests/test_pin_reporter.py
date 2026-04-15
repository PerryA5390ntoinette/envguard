"""Tests for envguard.pin_reporter."""
from __future__ import annotations

import pytest

from envguard.pinner import pin_env, detect_drift
from envguard.pin_reporter import format_pin_report, format_drift_report


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

def make_pin_report(env=None):
    return pin_env(env or {"FOO": "bar", "BAZ": "qux"}, source=".env")


# ---------------------------------------------------------------------------
# format_pin_report
# ---------------------------------------------------------------------------

def test_header_present_in_pin_report():
    report = make_pin_report()
    output = format_pin_report(report)
    assert "Pinned Variables" in output


def test_total_count_in_pin_report():
    report = make_pin_report({"A": "1", "B": "2"})
    output = format_pin_report(report)
    assert "2 total" in output


def test_key_present_in_pin_report():
    report = make_pin_report({"MY_VAR": "hello"})
    output = format_pin_report(report)
    assert "MY_VAR" in output


def test_checksum_present_in_pin_report():
    report = make_pin_report({"MY_VAR": "hello"})
    output = format_pin_report(report)
    cs = report.entries[0].checksum
    assert cs in output


def test_empty_pin_report_shows_message():
    report = pin_env({})
    output = format_pin_report(report)
    assert "No variables pinned" in output


def test_pin_report_no_color_has_no_escape_codes():
    report = make_pin_report()
    output = format_pin_report(report, use_color=False)
    assert "\033[" not in output


def test_pin_report_with_color_has_escape_codes():
    report = make_pin_report()
    output = format_pin_report(report, use_color=True)
    assert "\033[" in output


# ---------------------------------------------------------------------------
# format_drift_report
# ---------------------------------------------------------------------------

def test_drift_header_present():
    drifts = []
    output = format_drift_report(drifts)
    assert "Drift Detection" in output


def test_no_drift_message_when_empty():
    output = format_drift_report([])
    assert "No drift detected" in output


def test_drifted_key_shown_in_report():
    pinned = pin_env({"SECRET": "old"})
    drifts = detect_drift(pinned, {"SECRET": "new"})
    output = format_drift_report(drifts)
    assert "SECRET" in output


def test_pinned_and_current_values_shown():
    pinned = pin_env({"TOKEN": "abc"})
    drifts = detect_drift(pinned, {"TOKEN": "xyz"})
    output = format_drift_report(drifts)
    assert "abc" in output
    assert "xyz" in output


def test_drift_count_in_header():
    pinned = pin_env({"A": "1", "B": "2"})
    drifts = detect_drift(pinned, {"A": "changed", "B": "also_changed"})
    output = format_drift_report(drifts)
    assert "2 drift" in output


def test_drift_report_no_color_no_escape():
    pinned = pin_env({"K": "v"})
    drifts = detect_drift(pinned, {"K": "w"})
    output = format_drift_report(drifts, use_color=False)
    assert "\033[" not in output
