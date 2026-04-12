"""Tests for envguard.suggester."""

import pytest

from envguard.suggester import Suggestion, SuggestionReport, suggest, _suggest_for_result
from envguard.validator import ValidationReport, ValidationResult


def make_error(variable: str, message: str) -> ValidationResult:
    return ValidationResult(variable=variable, status="error", message=message)


def make_warning(variable: str, message: str) -> ValidationResult:
    return ValidationResult(variable=variable, status="warning", message=message)


def make_report(*results: ValidationResult) -> ValidationReport:
    report = ValidationReport()
    for r in results:
        report.results.append(r)
    return report


# --- _suggest_for_result ---

def test_suggest_missing_required():
    result = make_error("DATABASE_URL", "Missing required variable 'DATABASE_URL'")
    suggestion = _suggest_for_result(result)
    assert suggestion is not None
    assert suggestion.variable == "DATABASE_URL"
    assert "DATABASE_URL=<value>" in suggestion.fix


def test_suggest_pattern_mismatch():
    result = make_error("PORT", "Value does not match pattern: ^[0-9]+$")
    suggestion = _suggest_for_result(result)
    assert suggestion is not None
    assert "pattern" in suggestion.message.lower()
    assert "^[0-9]+$" in suggestion.fix


def test_suggest_invalid_allowed_value():
    result = make_error("ENV", "Not one of allowed values: development, staging, production")
    suggestion = _suggest_for_result(result)
    assert suggestion is not None
    assert "invalid value" in suggestion.message.lower()
    assert "development" in suggestion.fix


def test_suggest_unknown_variable():
    result = make_error("MYSTERY_VAR", "Unknown variable not in schema")
    suggestion = _suggest_for_result(result)
    assert suggestion is not None
    assert "not defined in the schema" in suggestion.message
    assert "Remove" in suggestion.fix or "schema" in suggestion.fix


def test_suggest_unrecognized_error_returns_none():
    result = make_error("SOME_VAR", "Some completely unrelated error message")
    suggestion = _suggest_for_result(result)
    assert suggestion is None


# --- suggest (full report) ---

def test_suggest_only_processes_errors():
    warning = make_warning("OPTIONAL_VAR", "Missing required variable 'OPTIONAL_VAR'")
    report = make_report(warning)
    suggestion_report = suggest(report)
    assert not suggestion_report.has_suggestions


def test_suggest_multiple_errors():
    r1 = make_error("DB_URL", "Missing required variable 'DB_URL'")
    r2 = make_error("LOG_LEVEL", "Not one of allowed values: debug, info, warn")
    report = make_report(r1, r2)
    suggestion_report = suggest(report)
    assert suggestion_report.has_suggestions
    assert len(suggestion_report.suggestions) == 2


def test_suggest_empty_report():
    report = ValidationReport()
    suggestion_report = suggest(report)
    assert not suggestion_report.has_suggestions
    assert suggestion_report.suggestions == []


def test_suggestion_report_add():
    sr = SuggestionReport()
    s = Suggestion(variable="X", message="msg", fix="X=value")
    sr.add(s)
    assert len(sr.suggestions) == 1
    assert sr.has_suggestions
