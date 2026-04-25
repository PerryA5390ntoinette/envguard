"""Tests for envguard.clone_reporter."""
import pytest
from envguard.cloner import clone_env, CloneReport
from envguard.clone_reporter import format_clone_report


def make_report(env=None, key_map=None, overrides=None):
    env = env or {}
    _, report = clone_env(env, key_map=key_map, overrides=overrides)
    return report


def test_header_present():
    report = make_report({"A": "1"})
    output = format_clone_report(report, use_color=False)
    assert "Clone Report" in output


def test_empty_env_shows_no_variables_message():
    report = make_report({})
    output = format_clone_report(report, use_color=False)
    assert "No variables cloned" in output


def test_key_present_in_output():
    report = make_report({"DB_HOST": "localhost"})
    output = format_clone_report(report, use_color=False)
    assert "DB_HOST" in output


def test_value_present_in_output():
    report = make_report({"DB_PORT": "5432"})
    output = format_clone_report(report, use_color=False)
    assert "5432" in output


def test_remapped_label_shown():
    report = make_report({"OLD": "val"}, key_map={"OLD": "NEW"})
    output = format_clone_report(report, use_color=False)
    assert "remapped" in output


def test_overridden_label_shown():
    report = make_report({"PORT": "8080"}, overrides={"PORT": "9090"})
    output = format_clone_report(report, use_color=False)
    assert "overridden" in output


def test_remap_arrow_shown():
    report = make_report({"OLD": "v"}, key_map={"OLD": "NEW"})
    output = format_clone_report(report, use_color=False)
    assert "OLD -> NEW" in output


def test_total_count_shown():
    report = make_report({"A": "1", "B": "2"})
    output = format_clone_report(report, use_color=False)
    assert "Total: 2" in output


def test_remapped_count_shown():
    report = make_report({"A": "1", "B": "2"}, key_map={"A": "A2"})
    output = format_clone_report(report, use_color=False)
    assert "Remapped: 1" in output


def test_overridden_count_shown():
    report = make_report({"A": "1"}, overrides={"A": "99"})
    output = format_clone_report(report, use_color=False)
    assert "Overridden: 1" in output


def test_no_remapped_label_for_plain_key():
    report = make_report({"PLAIN": "value"})
    output = format_clone_report(report, use_color=False)
    assert "remapped" not in output


def test_empty_value_shown_as_empty_label():
    report = make_report({"EMPTY_KEY": ""})
    output = format_clone_report(report, use_color=False)
    assert "(empty)" in output
