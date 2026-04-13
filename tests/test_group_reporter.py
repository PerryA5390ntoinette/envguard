"""Tests for envguard.group_reporter."""

import pytest
from envguard.grouper import group_env, GroupReport
from envguard.group_reporter import format_group_report


def make_report(env: dict) -> GroupReport:
    return group_env(env)


class TestFormatGroupReport:
    def test_header_present(self):
        report = make_report({})
        out = format_group_report(report, use_color=False)
        assert "Variable Groups" in out

    def test_empty_env_shows_no_variables_message(self):
        report = make_report({})
        out = format_group_report(report, use_color=False)
        assert "No variables found" in out

    def test_group_name_present(self):
        report = make_report({"DB_HOST": "localhost", "DB_PORT": "5432"})
        out = format_group_report(report, use_color=False)
        assert "[DB]" in out

    def test_key_listed_under_group(self):
        report = make_report({"DB_HOST": "localhost"})
        out = format_group_report(report, use_color=False)
        assert "DB_HOST" in out

    def test_ungrouped_label_present_when_needed(self):
        report = make_report({"PORT": "8080"})
        out = format_group_report(report, use_color=False)
        assert "ungrouped" in out

    def test_ungrouped_key_listed(self):
        report = make_report({"PORT": "8080"})
        out = format_group_report(report, use_color=False)
        assert "PORT" in out

    def test_total_line_present(self):
        report = make_report({"DB_HOST": "h", "DB_PORT": "p"})
        out = format_group_report(report, use_color=False)
        assert "Total:" in out

    def test_total_count_correct(self):
        report = make_report({"DB_HOST": "h", "DB_PORT": "p", "PORT": "8080"})
        out = format_group_report(report, use_color=False)
        assert "3 variable(s)" in out

    def test_group_count_in_total_line(self):
        report = make_report({"DB_HOST": "h", "AWS_KEY": "k"})
        out = format_group_report(report, use_color=False)
        assert "2 group(s)" in out

    def test_color_disabled_no_escape_codes(self):
        report = make_report({"DB_HOST": "h"})
        out = format_group_report(report, use_color=False)
        assert "\033[" not in out

    def test_color_enabled_contains_escape_codes(self):
        report = make_report({"DB_HOST": "h"})
        out = format_group_report(report, use_color=True)
        assert "\033[" in out
