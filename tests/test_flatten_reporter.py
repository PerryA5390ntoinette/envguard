"""Tests for envguard.flatten_reporter."""
from __future__ import annotations

import pytest

from envguard.flattener import FlattenEntry, FlattenReport
from envguard.flatten_reporter import format_flatten_report


def make_report(*entries: FlattenEntry) -> FlattenReport:
    report = FlattenReport()
    for e in entries:
        report.add(e)
    return report


def changed_entry(orig="APP__HOST", flat="app.host", depth=1):
    return FlattenEntry(original_key=orig, flattened_key=flat, depth=depth, changed=True)


def unchanged_entry(key="PORT"):
    return FlattenEntry(original_key=key, flattened_key=key, depth=0, changed=False)


# ---------------------------------------------------------------------------

def test_header_present():
    report = make_report()
    out = format_flatten_report(report, use_color=False)
    assert "Flatten Report" in out


def test_empty_report_shows_no_variables_message():
    report = make_report()
    out = format_flatten_report(report, use_color=False)
    assert "No variables" in out


def test_changed_key_shows_arrow():
    report = make_report(changed_entry())
    out = format_flatten_report(report, use_color=False)
    assert "→" in out


def test_original_key_present_in_output():
    report = make_report(changed_entry(orig="APP__HOST"))
    out = format_flatten_report(report, use_color=False)
    assert "APP__HOST" in out


def test_flattened_key_present_in_output():
    report = make_report(changed_entry(flat="app.host"))
    out = format_flatten_report(report, use_color=False)
    assert "app.host" in out


def test_unchanged_key_shows_ok_label():
    report = make_report(unchanged_entry())
    out = format_flatten_report(report, use_color=False)
    assert "OK" in out


def test_summary_shows_total():
    report = make_report(changed_entry(), unchanged_entry())
    out = format_flatten_report(report, use_color=False)
    assert "Total: 2" in out


def test_summary_shows_flattened_count():
    report = make_report(changed_entry(), changed_entry("DB__NAME", "db.name"))
    out = format_flatten_report(report, use_color=False)
    assert "Flattened: 2" in out


def test_summary_shows_unchanged_count():
    report = make_report(unchanged_entry(), unchanged_entry("DEBUG"))
    out = format_flatten_report(report, use_color=False)
    assert "Unchanged: 2" in out


def test_depth_shown_for_changed_entry():
    report = make_report(changed_entry(depth=3))
    out = format_flatten_report(report, use_color=False)
    assert "depth=3" in out


def test_max_depth_in_summary():
    report = make_report(changed_entry(depth=2))
    out = format_flatten_report(report, use_color=False)
    assert "Max depth: 2" in out
