"""Tests for envguard.transform_reporter."""

import pytest
from envguard.transformer import TransformEntry, TransformReport
from envguard.transform_reporter import format_transform_report


def make_entry(
    key="KEY",
    original="old",
    transformed="NEW",
    rule="upper",
    skipped=False,
    skip_reason=None,
) -> TransformEntry:
    return TransformEntry(
        key=key,
        original=original,
        transformed=transformed,
        rule=rule,
        skipped=skipped,
        skip_reason=skip_reason,
    )


def make_report(*entries) -> TransformReport:
    r = TransformReport()
    r.entries.extend(entries)
    return r


def test_header_present():
    output = format_transform_report(make_report(), use_color=False)
    assert "Transform Report" in output


def test_empty_report_shows_no_transformations_message():
    output = format_transform_report(make_report(), use_color=False)
    assert "No transformations applied" in output


def test_transformed_key_present_in_output():
    entry = make_entry(key="APP_ENV", original="staging", transformed="STAGING", rule="upper")
    output = format_transform_report(make_report(entry), use_color=False)
    assert "APP_ENV" in output


def test_original_value_shown():
    entry = make_entry(original="staging", transformed="STAGING")
    output = format_transform_report(make_report(entry), use_color=False)
    assert "staging" in output


def test_transformed_value_shown():
    entry = make_entry(original="staging", transformed="STAGING")
    output = format_transform_report(make_report(entry), use_color=False)
    assert "STAGING" in output


def test_rule_name_shown():
    entry = make_entry(rule="upper")
    output = format_transform_report(make_report(entry), use_color=False)
    assert "upper" in output


def test_skipped_entry_shows_skip_label():
    entry = make_entry(skipped=True, skip_reason="key not present in env")
    output = format_transform_report(make_report(entry), use_color=False)
    assert "SKIP" in output


def test_skip_reason_shown():
    entry = make_entry(skipped=True, skip_reason="unknown rule 'rot13'")
    output = format_transform_report(make_report(entry), use_color=False)
    assert "rot13" in output


def test_summary_counts_shown():
    e1 = make_entry(key="A", skipped=False)
    e2 = make_entry(key="B", skipped=True, skip_reason="missing")
    output = format_transform_report(make_report(e1, e2), use_color=False)
    assert "Transformed: 1" in output
    assert "Skipped: 1" in output


def test_no_color_output_has_no_escape_sequences():
    entry = make_entry()
    output = format_transform_report(make_report(entry), use_color=False)
    assert "\033[" not in output
