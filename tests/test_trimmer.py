"""Tests for envguard.trimmer."""

import pytest

from envguard.schema import EnvSchema, VariableSchema
from envguard.trimmer import TrimEntry, TrimReport, trim_env


def make_schema(*vars_: VariableSchema) -> EnvSchema:
    return EnvSchema(variables=list(vars_))


def make_var(name: str, required: bool = True) -> VariableSchema:
    return VariableSchema(name=name, required=required)


# ---------------------------------------------------------------------------
# Basic structure
# ---------------------------------------------------------------------------

def test_trim_returns_report_instance():
    schema = make_schema(make_var("PORT"))
    result = trim_env({"PORT": "8080"}, schema)
    assert isinstance(result, TrimReport)


def test_empty_env_produces_empty_report():
    schema = make_schema(make_var("PORT"))
    result = trim_env({}, schema)
    assert result.trimmed_count == 0
    assert result.kept_count == 0


# ---------------------------------------------------------------------------
# Unknown variable removal
# ---------------------------------------------------------------------------

def test_unknown_key_is_trimmed_by_default():
    schema = make_schema(make_var("PORT"))
    result = trim_env({"PORT": "8080", "GHOST": "value"}, schema)
    assert "GHOST" in result.trimmed_keys()


def test_unknown_key_has_reason_unknown():
    schema = make_schema(make_var("PORT"))
    result = trim_env({"GHOST": "value"}, schema)
    assert result.trimmed[0].reason == "unknown"


def test_known_key_is_kept():
    schema = make_schema(make_var("PORT"))
    result = trim_env({"PORT": "8080"}, schema)
    assert "PORT" in result.kept


def test_remove_unknown_false_keeps_unknown_key():
    schema = make_schema(make_var("PORT"))
    result = trim_env({"PORT": "8080", "GHOST": "value"}, schema, remove_unknown=False)
    assert "GHOST" in result.kept
    assert result.trimmed_count == 0


# ---------------------------------------------------------------------------
# Empty optional removal
# ---------------------------------------------------------------------------

def test_empty_optional_not_trimmed_by_default():
    schema = make_schema(make_var("DEBUG", required=False))
    result = trim_env({"DEBUG": ""}, schema)
    assert "DEBUG" in result.kept


def test_empty_optional_trimmed_when_flag_set():
    schema = make_schema(make_var("DEBUG", required=False))
    result = trim_env({"DEBUG": ""}, schema, remove_empty_optional=True)
    assert "DEBUG" in result.trimmed_keys()


def test_empty_optional_has_reason_empty_optional():
    schema = make_schema(make_var("DEBUG", required=False))
    result = trim_env({"DEBUG": ""}, schema, remove_empty_optional=True)
    assert result.trimmed[0].reason == "empty_optional"


def test_non_empty_optional_kept_even_when_flag_set():
    schema = make_schema(make_var("DEBUG", required=False))
    result = trim_env({"DEBUG": "true"}, schema, remove_empty_optional=True)
    assert "DEBUG" in result.kept


def test_empty_required_not_trimmed_when_flag_set():
    schema = make_schema(make_var("PORT", required=True))
    result = trim_env({"PORT": ""}, schema, remove_empty_optional=True)
    assert "PORT" in result.kept


# ---------------------------------------------------------------------------
# Counts
# ---------------------------------------------------------------------------

def test_trimmed_count_reflects_removed_entries():
    schema = make_schema(make_var("PORT"))
    result = trim_env({"PORT": "8080", "A": "1", "B": "2"}, schema)
    assert result.trimmed_count == 2


def test_kept_count_reflects_retained_entries():
    schema = make_schema(make_var("PORT"), make_var("HOST"))
    result = trim_env({"PORT": "8080", "HOST": "localhost", "EXTRA": "x"}, schema)
    assert result.kept_count == 2
