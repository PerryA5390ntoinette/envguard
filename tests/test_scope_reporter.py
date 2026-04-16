"""Tests for envguard.scope_reporter."""
import pytest
from envguard.scoper import scope_env
from envguard.scope_reporter import format_scope_report


def make_report(env: dict):
    return scope_env(env)


def test_empty_env_shows_no_variables_message():
    report = make_report({})
    output = format_scope_report(report, use_color=False)
    assert "No variables found" in output


def test_header_present():
    report = make_report({"FOO": "bar"})
    output = format_scope_report(report, use_color=False)
    assert "Scope Report" in output


def test_scope_label_present():
    report = make_report({"DEV_HOST": "localhost"})
    output = format_scope_report(report, use_color=False)
    assert "DEV" in output


def test_key_present_in_output():
    report = make_report({"STAGING_DB": "mydb"})
    output = format_scope_report(report, use_color=False)
    assert "STAGING_DB" in output


def test_global_count_in_output():
    report = make_report({"PLAIN_KEY": "value"})
    output = format_scope_report(report, use_color=False)
    assert "Global: 1" in output


def test_total_count_in_output():
    report = make_report({"A": "1", "B": "2", "DEV_C": "3"})
    output = format_scope_report(report, use_color=False)
    assert "Total: 3" in output


def test_multiple_scopes_shown():
    report = make_report({"DEV_A": "1", "PROD_B": "2"})
    output = format_scope_report(report, use_color=False)
    assert "DEV" in output
    assert "PROD" in output


def test_color_output_contains_ansi():
    report = make_report({"DEV_X": "val"})
    output = format_scope_report(report, use_color=True)
    assert "\033[" in output


def test_no_color_output_lacks_ansi():
    report = make_report({"DEV_X": "val"})
    output = format_scope_report(report, use_color=False)
    assert "\033[" not in output
