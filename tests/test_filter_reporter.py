"""Tests for envguard.filter_reporter."""
import pytest
from envguard.filterer import FilterReport, FilterEntry
from envguard.filter_reporter import format_filter_report


def make_report(
    entries: list[tuple[str, str, str]] | None = None,
    excluded: list[str] | None = None,
) -> FilterReport:
    report = FilterReport()
    for key, value, matched_by in (entries or []):
        report.entries.append(FilterEntry(key=key, value=value, matched_by=matched_by))
    report.excluded = excluded or []
    return report


def test_header_present():
    report = make_report()
    output = format_filter_report(report, use_color=False)
    assert "Filter Report" in output


def test_empty_report_shows_no_match_message():
    report = make_report()
    output = format_filter_report(report, use_color=False)
    assert "No variables matched" in output


def test_matched_key_present_in_output():
    report = make_report(entries=[("DB_HOST", "localhost", "prefix")])
    output = format_filter_report(report, use_color=False)
    assert "DB_HOST" in output


def test_matched_value_present_in_output():
    report = make_report(entries=[("DB_HOST", "localhost", "prefix")])
    output = format_filter_report(report, use_color=False)
    assert "localhost" in output


def test_matched_by_label_present():
    report = make_report(entries=[("APP_KEY", "secret", "pattern")])
    output = format_filter_report(report, use_color=False)
    assert "pattern" in output


def test_matched_count_shown():
    report = make_report(
        entries=[("A", "1", "key"), ("B", "2", "key")],
    )
    output = format_filter_report(report, use_color=False)
    assert "2" in output


def test_excluded_keys_shown():
    report = make_report(
        entries=[("A", "1", "prefix")],
        excluded=["IGNORED_KEY"],
    )
    output = format_filter_report(report, use_color=False)
    assert "IGNORED_KEY" in output


def test_excluded_count_shown():
    report = make_report(
        entries=[("A", "1", "prefix")],
        excluded=["X", "Y"],
    )
    output = format_filter_report(report, use_color=False)
    assert "2" in output


def test_no_color_produces_plain_text():
    report = make_report(entries=[("K", "v", "key")])
    output = format_filter_report(report, use_color=False)
    assert "\033[" not in output


def test_with_color_contains_ansi_codes():
    report = make_report(entries=[("K", "v", "key")])
    output = format_filter_report(report, use_color=True)
    assert "\033[" in output
