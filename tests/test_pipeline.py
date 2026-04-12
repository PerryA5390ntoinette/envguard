"""Tests for envguard.pipeline."""
import pytest
from unittest.mock import patch

from envguard.pipeline import run_pipeline, PipelineResult
from envguard.schema import EnvSchema, VariableSchema


def make_schema(vars_: dict) -> EnvSchema:
    variables = {
        k: VariableSchema(
            name=k,
            required=v.get("required", False),
            pattern=v.get("pattern"),
            allowed_values=v.get("allowed_values"),
        )
        for k, v in vars_.items()
    }
    return EnvSchema(variables=variables)


FAKE_ENV = {"APP_ENV": "production", "PORT": "8080"}


@patch("envguard.pipeline.load_env_files", return_value=FAKE_ENV)
def test_pipeline_returns_result_instance(mock_load):
    schema = make_schema({"APP_ENV": {"required": True}})
    result = run_pipeline([".env"], schema)
    assert isinstance(result, PipelineResult)


@patch("envguard.pipeline.load_env_files", return_value=FAKE_ENV)
def test_pipeline_populates_raw_env(mock_load):
    schema = make_schema({})
    result = run_pipeline([".env"], schema)
    assert result.raw_env == FAKE_ENV


@patch("envguard.pipeline.load_env_files", return_value=FAKE_ENV)
def test_pipeline_interpolation_report_present_by_default(mock_load):
    schema = make_schema({})
    result = run_pipeline([".env"], schema)
    assert result.interpolation is not None


@patch("envguard.pipeline.load_env_files", return_value=FAKE_ENV)
def test_pipeline_interpolation_skipped_when_disabled(mock_load):
    schema = make_schema({})
    result = run_pipeline([".env"], schema, interpolate_values=False)
    assert result.interpolation is None


@patch("envguard.pipeline.load_env_files", return_value=FAKE_ENV)
def test_pipeline_success_when_required_vars_present(mock_load):
    schema = make_schema({"APP_ENV": {"required": True}, "PORT": {"required": True}})
    result = run_pipeline([".env"], schema)
    assert result.success is True


@patch("envguard.pipeline.load_env_files", return_value=FAKE_ENV)
def test_pipeline_failure_when_required_var_missing(mock_load):
    schema = make_schema({"MISSING_VAR": {"required": True}})
    result = run_pipeline([".env"], schema)
    assert result.success is False


@patch("envguard.pipeline.load_env_files", return_value=FAKE_ENV)
def test_pipeline_suggestions_populated(mock_load):
    schema = make_schema({"MISSING_VAR": {"required": True}})
    result = run_pipeline([".env"], schema)
    assert result.suggestions is not None


@patch("envguard.pipeline.load_env_files", return_value=FAKE_ENV)
def test_pipeline_env_files_recorded(mock_load):
    schema = make_schema({})
    result = run_pipeline([".env", ".env.local"], schema)
    assert result.env_files == [".env", ".env.local"]


@patch("envguard.pipeline.load_env_files", return_value={"BASE": "http://x.com", "URL": "${BASE}/v1"})
def test_pipeline_interpolates_references(mock_load):
    schema = make_schema({})
    result = run_pipeline([".env"], schema)
    assert result.interpolation is not None
    assert result.interpolation.resolved["URL"] == "http://x.com/v1"
