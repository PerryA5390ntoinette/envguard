"""Tests for envguard.auditor."""

import pytest
from envguard.auditor import audit
from envguard.schema import EnvSchema, VariableSchema


def make_schema(**variables: VariableSchema) -> EnvSchema:
    return EnvSchema(variables=variables)


def make_var(
    required: bool = True,
    pattern: str = None,
    allowed_values=None,
    default: str = None,
) -> VariableSchema:
    return VariableSchema(
        required=required,
        pattern=pattern,
        allowed_values=allowed_values or [],
        default=default,
    )


# --- required variable checks ---

def test_missing_required_variable_produces_error():
    schema = make_schema(DATABASE_URL=make_var(required=True))
    report = audit({}, schema)
    assert any(r.name == "DATABASE_URL" for r in report.errors)


def test_present_required_variable_passes():
    schema = make_schema(DATABASE_URL=make_var(required=True))
    report = audit({"DATABASE_URL": "postgres://localhost/db"}, schema)
    assert not report.errors
    assert any(r.name == "DATABASE_URL" for r in report.passed)


def test_missing_optional_variable_no_error():
    schema = make_schema(DEBUG=make_var(required=False))
    report = audit({}, schema)
    assert not report.errors


# --- default value handling ---

def test_missing_variable_with_default_produces_warning():
    schema = make_schema(LOG_LEVEL=make_var(required=True, default="INFO"))
    report = audit({}, schema)
    assert not report.errors
    assert any(r.name == "LOG_LEVEL" for r in report.warnings)


# --- pattern checks ---

def test_value_matching_pattern_passes():
    schema = make_schema(PORT=make_var(pattern=r"\d+"))
    report = audit({"PORT": "8080"}, schema)
    assert not report.errors


def test_value_not_matching_pattern_produces_error():
    schema = make_schema(PORT=make_var(pattern=r"\d+"))
    report = audit({"PORT": "not-a-number"}, schema)
    assert any(r.name == "PORT" for r in report.errors)


# --- allowed_values checks ---

def test_value_in_allowed_values_passes():
    schema = make_schema(ENV=make_var(allowed_values=["dev", "staging", "prod"]))
    report = audit({"ENV": "prod"}, schema)
    assert not report.errors


def test_value_not_in_allowed_values_produces_error():
    schema = make_schema(ENV=make_var(allowed_values=["dev", "staging", "prod"]))
    report = audit({"ENV": "test"}, schema)
    assert any(r.name == "ENV" for r in report.errors)


# --- unknown variable checks ---

def test_unknown_variable_produces_warning():
    schema = make_schema(DATABASE_URL=make_var())
    report = audit({"DATABASE_URL": "postgres://", "MYSTERY_VAR": "42"}, schema)
    assert any(r.name == "MYSTERY_VAR" for r in report.warnings)


def test_no_warnings_for_known_variables():
    schema = make_schema(DATABASE_URL=make_var())
    report = audit({"DATABASE_URL": "postgres://"}, schema)
    assert not report.warnings
