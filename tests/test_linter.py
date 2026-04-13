"""Tests for envguard.linter module."""
import pytest
from envguard.linter import lint_env_lines, LintReport, LintIssue


def issues_for(lines):
    return lint_env_lines(lines).issues


def test_empty_file_no_issues():
    assert issues_for([]) == []


def test_comment_line_ignored():
    assert issues_for(["# this is a comment\n"]) == []


def test_blank_line_ignored():
    assert issues_for(["\n", "  \n"]) == []


def test_missing_equals_is_error():
    result = issues_for(["BADLINE\n"])
    assert len(result) == 1
    assert result[0].severity == "error"
    assert "'='" in result[0].message


def test_lowercase_key_warns():
    result = issues_for(["my_key=value\n"])
    severities = [i.severity for i in result]
    assert "warning" in severities
    messages = [i.message for i in result]
    assert any("UPPER_SNAKE_CASE" in m for m in messages)


def test_uppercase_key_no_case_warning():
    result = issues_for(["MY_KEY=value\n"])
    messages = [i.message for i in result]
    assert not any("UPPER_SNAKE_CASE" in m for m in messages)


def test_key_with_spaces_is_error():
    result = issues_for(["MY KEY=value\n"])
    severities = [i.severity for i in result]
    assert "error" in severities


def test_value_leading_whitespace_warns():
    result = issues_for(["MY_KEY= value\n"])
    messages = [i.message for i in result]
    assert any("whitespace" in m for m in messages)


def test_value_trailing_whitespace_warns():
    result = issues_for(["MY_KEY=value \n"])
    messages = [i.message for i in result]
    assert any("whitespace" in m for m in messages)


def test_clean_value_no_whitespace_warning():
    result = issues_for(["MY_KEY=value\n"])
    messages = [i.message for i in result]
    assert not any("whitespace" in m for m in messages)


def test_secret_key_unquoted_warns():
    result = issues_for(["API_KEY=abc123\n"])
    messages = [i.message for i in result]
    assert any("quoted" in m for m in messages)


def test_secret_key_quoted_no_warning():
    result = issues_for(["API_KEY='abc123'\n"])
    messages = [i.message for i in result]
    assert not any("quoted" in m for m in messages)


def test_error_count_and_warning_count():
    lines = ["badline\n", "my_key=value\n", "MY_KEY= value\n"]
    report = lint_env_lines(lines)
    assert report.error_count >= 1
    assert report.warning_count >= 1


def test_has_issues_false_for_clean_file():
    report = lint_env_lines(["MY_KEY=value\n"])
    assert not report.has_issues


def test_line_number_recorded():
    lines = ["GOOD=ok\n", "badline\n"]
    result = issues_for(lines)
    assert result[0].line_number == 2
