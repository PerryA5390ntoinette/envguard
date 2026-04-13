"""Tests for envguard.rename_reporter."""
from __future__ import annotations

import pytest

from envguard.renamer import RenameEntry, RenameReport
from envguard.rename_reporter import format_rename_report


def make_report(*entries: RenameEntry) -> RenameReport:
    return RenameReport(entries=list(entries))


def ok_entry(old="OLD", new="NEW", value="val") -> RenameEntry:
    return RenameEntry(old_name=old, new_name=new, value=value)


def skip_entry(old="OLD", new="NEW", reason="source key not found") -> RenameEntry:
    return RenameEntry(old_name=old, new_name=new, value="", skipped=True, skip_reason=reason)


# ---------------------------------------------------------------------------
# Header
# ---------------------------------------------------------------------------

def test_header_present():
    out = format_rename_report(make_report(), use_color=False)
    assert "Rename Report" in out


def test_empty_report_message():
    out = format_rename_report(make_report(), use_color=False)
    assert "No renames requested" in out


# ---------------------------------------------------------------------------
# OK entries
# ---------------------------------------------------------------------------

def test_ok_label_present():
    out = format_rename_report(make_report(ok_entry()), use_color=False)
    assert "OK" in out


def test_ok_entry_shows_arrow():
    out = format_rename_report(make_report(ok_entry(old="A", new="B")), use_color=False)
    assert "A -> B" in out


# ---------------------------------------------------------------------------
# Skipped entries
# ---------------------------------------------------------------------------

def test_skip_label_present():
    out = format_rename_report(make_report(skip_entry()), use_color=False)
    assert "SKIP" in out


def test_skip_reason_shown():
    out = format_rename_report(make_report(skip_entry(reason="target key 'X' already exists")), use_color=False)
    assert "already exists" in out


# ---------------------------------------------------------------------------
# Summary counts
# ---------------------------------------------------------------------------

def test_renamed_count_in_output():
    report = make_report(ok_entry(), ok_entry(old="C", new="D"))
    out = format_rename_report(report, use_color=False)
    assert "Renamed: 2" in out


def test_skipped_count_in_output():
    report = make_report(skip_entry(), skip_entry(old="X", new="Y"))
    out = format_rename_report(report, use_color=False)
    assert "Skipped: 2" in out


def test_mixed_counts():
    report = make_report(ok_entry(), skip_entry())
    out = format_rename_report(report, use_color=False)
    assert "Renamed: 1" in out
    assert "Skipped: 1" in out


# ---------------------------------------------------------------------------
# Color flag
# ---------------------------------------------------------------------------

def test_no_ansi_when_color_disabled():
    out = format_rename_report(make_report(ok_entry()), use_color=False)
    assert "\033[" not in out


def test_ansi_present_when_color_enabled():
    out = format_rename_report(make_report(ok_entry()), use_color=True)
    assert "\033[" in out
