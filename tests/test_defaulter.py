"""Tests for envguard.defaulter."""
import pytest
from envguard.defaulter import apply_defaults, DefaultReport
from envguard.schema import EnvSchema, VariableSchema


def make_schema(*vars_: VariableSchema) -> EnvSchema:
    return EnvSchema(variables=list(vars_))


def make_var(name: str, default=None, required: bool = False) -> VariableSchema:
    return VariableSchema(name=name, required=required, default=default)


def test_apply_defaults_returns_tuple():
    schema = make_schema(make_var("PORT", default="8080"))
    result = apply_defaults({}, schema)
    assert isinstance(result, tuple) and len(result) == 2


def test_report_is_default_report_instance():
    schema = make_schema(make_var("PORT", default="8080"))
    _, report = apply_defaults({}, schema)
    assert isinstance(report, DefaultReport)


def test_missing_key_gets_default_applied():
    schema = make_schema(make_var("PORT", default="8080"))
    updated, _ = apply_defaults({}, schema)
    assert updated["PORT"] == "8080"


def test_present_key_not_overwritten_by_default():
    schema = make_schema(make_var("PORT", default="8080"))
    updated, _ = apply_defaults({"PORT": "3000"}, schema)
    assert updated["PORT"] == "3000"


def test_overwrite_flag_replaces_existing_value():
    schema = make_schema(make_var("PORT", default="8080"))
    updated, _ = apply_defaults({"PORT": "3000"}, schema, overwrite=True)
    assert updated["PORT"] == "8080"


def test_var_without_default_is_ignored():
    schema = make_schema(make_var("SECRET"))
    updated, report = apply_defaults({}, schema)
    assert "SECRET" not in updated
    assert report.filled_count() == 0


def test_filled_count_increments_for_applied_default():
    schema = make_schema(make_var("HOST", default="localhost"))
    _, report = apply_defaults({}, schema)
    assert report.filled_count() == 1


def test_skipped_count_increments_when_key_present():
    schema = make_schema(make_var("HOST", default="localhost"))
    _, report = apply_defaults({"HOST": "example.com"}, schema)
    assert report.skipped_count() == 1


def test_filled_keys_contains_applied_key():
    schema = make_schema(make_var("DB_HOST", default="127.0.0.1"))
    _, report = apply_defaults({}, schema)
    assert "DB_HOST" in report.filled_keys()


def test_original_env_not_mutated():
    env = {"EXISTING": "yes"}
    schema = make_schema(make_var("PORT", default="8080"))
    apply_defaults(env, schema)
    assert "PORT" not in env


def test_multiple_defaults_all_applied():
    schema = make_schema(
        make_var("A", default="1"),
        make_var("B", default="2"),
        make_var("C", default="3"),
    )
    updated, report = apply_defaults({}, schema)
    assert updated == {"A": "1", "B": "2", "C": "3"}
    assert report.filled_count() == 3


def test_result_env_returns_only_filled_entries():
    schema = make_schema(
        make_var("A", default="1"),
        make_var("B", default="2"),
    )
    _, report = apply_defaults({"A": "existing"}, schema)
    result = report.result_env()
    assert "B" in result
    assert "A" not in result
