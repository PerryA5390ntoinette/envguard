"""Tests for envguard.inject_reporter."""
from __future__ import annotations

import pytest

from envguard.injector import InjectionEntry, InjectionReport
from envguard.inject_reporter import format_inject_report


def make_report(*entries: InjectionEntry) -> InjectionReport:
    report = InjectionReport()
    for e in entries:
        report.add(e)
    return report


def _entry(key="KEY", value="val", source="defaults", replaced=False):
    return InjectionEntry(key=key, value=value, source=source, replaced=replaced)


# ---------------------------------------------------------------------------
# header
# ---------------------------------------------------------------------------

def test_header_present():
    report = make_report()
    out = format_inject_report(report, use_color=False)
    assert "Injection Report" in out


def test_empty_report_shows_no_injected_message():
    report = make_report()
    out = format_inject_report(report, use_color=False)
    assert "No variables were injected" in out


# ---------------------------------------------------------------------------
# entry rendering
# ---------------------------------------------------------------------------

def test_key_present_in_output():
    report = make_report(_entry(key="MY_KEY"))
    out = format_inject_report(report, use_color=False)
    assert "MY_KEY" in out


def test_value_present_in_output():
    report = make_report(_entry(value="secret123"))
    out = format_inject_report(report, use_color=False)
    assert "secret123" in out


def test_source_label_present():
    report = make_report(_entry(source="os"))
    out = format_inject_report(report, use_color=False)
    assert "[os]" in out


def test_replaced_label_shown_when_replaced():
    report = make_report(_entry(replaced=True))
    out = format_inject_report(report, use_color=False)
    assert "replaced" in out


def test_replaced_label_absent_when_not_replaced():
    report = make_report(_entry(replaced=False))
    out = format_inject_report(report, use_color=False)
    assert "replaced" not in out


# ---------------------------------------------------------------------------
# summary line
# ---------------------------------------------------------------------------

def test_injected_count_in_summary():
    report = make_report(_entry(), _entry(key="B"))
    out = format_inject_report(report, use_color=False)
    assert "Injected: 2" in out


def test_replaced_count_in_summary():
    report = make_report(_entry(replaced=True), _entry(replaced=False))
    out = format_inject_report(report, use_color=False)
    assert "Replaced: 1" in out


def test_sources_listed_in_summary():
    report = make_report(
        _entry(source="defaults"),
        _entry(key="B", source="override"),
    )
    out = format_inject_report(report, use_color=False)
    assert "defaults" in out
    assert "override" in out
