"""Tests for envguard schema loading, env parsing, and validation."""

import json
import textwrap
from pathlib import Path

import pytest

from envguard.loader import load_env_file, parse_env_line
from envguard.schema import EnvSchema, VariableSchema
from envguard.validator import validate


# ---------------------------------------------------------------------------
# parse_env_line
# ---------------------------------------------------------------------------

def test_parse_simple_pair():
    assert parse_env_line("KEY=value") == ("KEY", "value")

def test_parse_quoted_value():
    assert parse_env_line('SECRET="my secret"') == ("SECRET", "my secret")

def test_parse_comment_returns_none():
    assert parse_env_line("# this is a comment") is None

def test_parse_blank_line_returns_none():
    assert parse_env_line("   ") is None

def test_parse_no_equals_returns_none():
    assert parse_env_line("NOEQUALS") is None


# ---------------------------------------------------------------------------
# load_env_file
# ---------------------------------------------------------------------------

def test_load_env_file(tmp_path: Path):
    env_file = tmp_path / ".env"
    env_file.write_text("APP_ENV=production\nDEBUG=false\n# ignored\n")
    result = load_env_file(env_file)
    assert result == {"APP_ENV": "production", "DEBUG": "false"}

def test_load_env_file_not_found(tmp_path: Path):
    with pytest.raises(FileNotFoundError):
        load_env_file(tmp_path / "missing.env")


# ---------------------------------------------------------------------------
# EnvSchema
# ---------------------------------------------------------------------------

def test_schema_from_dict():
    data = {"variables": {"PORT": {"type": "integer", "required": True}}}
    schema = EnvSchema.from_dict(data)
    assert len(schema.variables) == 1
    assert schema.variables[0].name == "PORT"
    assert schema.variables[0].type == "integer"

def test_schema_invalid_type_raises():
    with pytest.raises(ValueError, match="Invalid type"):
        VariableSchema(name="X", type="uuid")

def test_schema_load_from_file(tmp_path: Path):
    schema_file = tmp_path / ".env.schema.json"
    schema_file.write_text(json.dumps({"variables": {"DB_URL": {"type": "url"}}}))
    schema = EnvSchema.load(schema_file)
    assert schema.variables[0].name == "DB_URL"


# ---------------------------------------------------------------------------
# validate
# ---------------------------------------------------------------------------

def _make_schema(*vars_: VariableSchema) -> EnvSchema:
    return EnvSchema(variables=list(vars_))

def test_validate_passes_for_valid_vars():
    schema = _make_schema(VariableSchema(name="PORT", type="integer"))
    report = validate({"PORT": "8080"}, schema)
    assert report.passed
    assert len(report.errors) == 0

def test_validate_missing_required_var():
    schema = _make_schema(VariableSchema(name="SECRET_KEY", required=True))
    report = validate({}, schema)
    assert not report.passed
    assert any("SECRET_KEY" in e.message for e in report.errors)

def test_validate_type_mismatch():
    schema = _make_schema(VariableSchema(name="PORT", type="integer"))
    report = validate({"PORT": "not-a-number"}, schema)
    assert not report.passed

def test_validate_allowed_values():
    schema = _make_schema(VariableSchema(name="ENV", allowed_values=["dev", "prod"]))
    report = validate({"ENV": "staging"}, schema)
    assert not report.passed

def test_validate_pattern():
    schema = _make_schema(VariableSchema(name="VERSION", pattern=r"\d+\.\d+\.\d+"))
    report = validate({"VERSION": "1.2.3"}, schema)
    assert report.passed
    report2 = validate({"VERSION": "v1.2"}, schema)
    assert not report2.passed

def test_validate_optional_missing_is_warning():
    schema = _make_schema(VariableSchema(name="LOG_LEVEL", required=False, default="info"))
    report = validate({}, schema)
    assert report.passed
    assert len(report.warnings) == 1
