"""Tests for envguard.deprecation_reporter."""
import pytest
from envguard.deprecator import DeprecationEntry, DeprecationReport
from envguard.deprecation_reporter import format_deprecation_report


def make_report(*entries):
    r = DeprecationReport()
    for e in entries:
        r.add(e)
    return r


def empty_report():
    return make_report()


def test_empty_report_shows_no_deprecations_message():
    out = format_deprecation_report(empty_report(), use_color=False)
    assert "No deprecated variables found" in out


def test_deprecated_key_present_in_output():
    r = make_report(
        DeprecationEntry(key="OLD_KEY", reason="Removed.", replacement="NEW_KEY")
    )
    out = format_deprecation_report(r, use_color=False)
    assert "OLD_KEY" in out


def test_reason_present_in_output():
    r = make_report(
        DeprecationEntry(key="OLD_KEY", reason="Use NEW_KEY.", replacement=None)
    )
    out = format_deprecation_report(r, use_color=False)
    assert "Use NEW_KEY" in out


def test_replacement_present_when_set():
    r = make_report(
        DeprecationEntry(key="OLD_KEY", reason="Removed.", replacement="NEW_KEY")
    )
    out = format_deprecation_report(r, use_color=False)
    assert "NEW_KEY" in out


def test_no_replacement_label_shown():
    r = make_report(
        DeprecationEntry(key="OLD_KEY", reason="Gone.", replacement=None)
    )
    out = format_deprecation_report(r, use_color=False)
    assert "(none)" in out


def test_total_count_in_summary():
    r = make_report(
        DeprecationEntry(key="A", reason="r1", replacement="B"),
        DeprecationEntry(key="C", reason="r2", replacement=None),
    )
    out = format_deprecation_report(r, use_color=False)
    assert "Total deprecated: 2" in out


def test_with_replacement_count_in_summary():
    r = make_report(
        DeprecationEntry(key="A", reason="r1", replacement="B"),
        DeprecationEntry(key="C", reason="r2", replacement=None),
    )
    out = format_deprecation_report(r, use_color=False)
    assert "1 with replacement" in out


def test_without_replacement_count_in_summary():
    r = make_report(
        DeprecationEntry(key="A", reason="r1", replacement="B"),
        DeprecationEntry(key="C", reason="r2", replacement=None),
    )
    out = format_deprecation_report(r, use_color=False)
    assert "1 without" in out


def test_header_present_when_issues_exist():
    r = make_report(
        DeprecationEntry(key="OLD", reason="old.", replacement=None)
    )
    out = format_deprecation_report(r, use_color=False)
    assert "Deprecated Variables" in out


def test_color_codes_absent_when_disabled():
    r = make_report(
        DeprecationEntry(key="OLD", reason="old.", replacement=None)
    )
    out = format_deprecation_report(r, use_color=False)
    assert "\033[" not in out
