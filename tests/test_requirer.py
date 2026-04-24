"""Tests for envguard.requirer."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Optional

import pytest

from envguard.requirer import RequireEntry, RequireReport, check_required
from envguard.schema import EnvSchema, VariableSchema


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_schema(**vars_: VariableSchema) -> EnvSchema:
    return EnvSchema(variables=vars_)


def make_var(required: bool = True, pattern: Optional[str] = None) -> VariableSchema:
    return VariableSchema(required=required, pattern=pattern)


def run_check(env: Dict[str, str], **vars_: VariableSchema) -> RequireReport:
    schema = make_schema(**vars_)
    return check_required(env, schema)


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def test_returns_require_report_instance():
    report = run_check({}, DB_HOST=make_var())
    assert isinstance(report, RequireReport)


def test_missing_required_key_is_flagged():
    report = run_check({}, DB_HOST=make_var(required=True))
    assert "DB_HOST" in report.flagged_keys()


def test_present_required_key_not_flagged():
    report = run_check({"DB_HOST": "localhost"}, DB_HOST=make_var(required=True))
    assert "DB_HOST" not in report.flagged_keys()


def test_empty_string_value_is_flagged():
    report = run_check({"API_KEY": ""}, API_KEY=make_var(required=True))
    assert "API_KEY" in report.flagged_keys()


def test_whitespace_only_value_is_flagged():
    report = run_check({"API_KEY": "   "}, API_KEY=make_var(required=True))
    assert "API_KEY" in report.flagged_keys()


def test_optional_key_never_flagged_even_when_absent():
    report = run_check({}, LOG_LEVEL=make_var(required=False))
    assert report.flagged_count() == 0


def test_optional_key_present_in_env_included_as_not_flagged():
    report = run_check({"LOG_LEVEL": "debug"}, LOG_LEVEL=make_var(required=False))
    keys = [e.key for e in report.entries]
    assert "LOG_LEVEL" in keys
    assert "LOG_LEVEL" not in report.flagged_keys()


def test_flagged_count_correct():
    report = run_check(
        {"DB_HOST": "localhost"},
        DB_HOST=make_var(required=True),
        DB_PASS=make_var(required=True),
    )
    assert report.flagged_count() == 1


def test_ok_count_correct():
    report = run_check(
        {"DB_HOST": "localhost"},
        DB_HOST=make_var(required=True),
        DB_PASS=make_var(required=True),
    )
    assert report.ok_count() == 1


def test_has_issues_true_when_flagged():
    report = run_check({}, SECRET=make_var(required=True))
    assert report.has_issues() is True


def test_has_issues_false_when_all_present():
    report = run_check({"SECRET": "abc123"}, SECRET=make_var(required=True))
    assert report.has_issues() is False


def test_entry_value_is_none_when_absent():
    report = run_check({}, TOKEN=make_var(required=True))
    entry = next(e for e in report.entries if e.key == "TOKEN")
    assert entry.value is None


def test_entry_value_captured_when_present():
    report = run_check({"TOKEN": "xyz"}, TOKEN=make_var(required=True))
    entry = next(e for e in report.entries if e.key == "TOKEN")
    assert entry.value == "xyz"
