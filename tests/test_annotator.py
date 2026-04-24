"""Tests for envguard.annotator."""
import pytest
from unittest.mock import MagicMock
from envguard.annotator import (
    annotate_env,
    AnnotationReport,
    AnnotationEntry,
    _build_annotation,
)
from envguard.schema import EnvSchema, VariableSchema


def make_schema(**vars_kwargs) -> EnvSchema:
    variables = {}
    for name, kwargs in vars_kwargs.items():
        variables[name] = VariableSchema(name=name, **kwargs)
    schema = MagicMock(spec=EnvSchema)
    schema.variables = variables
    return schema


# --- _build_annotation ---

def test_build_annotation_returns_none_for_unknown_key():
    schema = make_schema()
    assert _build_annotation("MISSING", schema) is None


def test_build_annotation_includes_description():
    schema = make_schema(DB_HOST={"description": "Database host", "required": True})
    result = _build_annotation("DB_HOST", schema)
    assert result is not None
    assert "Database host" in result


def test_build_annotation_marks_optional():
    schema = make_schema(LOG_LEVEL={"required": False})
    result = _build_annotation("LOG_LEVEL", schema)
    assert result is not None
    assert "optional" in result


def test_build_annotation_includes_allowed_values():
    schema = make_schema(
        ENV={"allowed_values": ["dev", "prod", "staging"], "required": True}
    )
    result = _build_annotation("ENV", schema)
    assert "dev" in result
    assert "prod" in result


def test_build_annotation_includes_pattern():
    schema = make_schema(PORT={"pattern": r"^\d+$", "required": True})
    result = _build_annotation("PORT", schema)
    assert r"^\d+$" in result


def test_build_annotation_returns_none_when_no_metadata():
    schema = make_schema(BARE={"required": True})
    result = _build_annotation("BARE", schema)
    assert result is None


# --- annotate_env ---

def test_annotate_env_returns_report_instance():
    schema = make_schema()
    report = annotate_env([], schema)
    assert isinstance(report, AnnotationReport)


def test_blank_line_passed_through_unchanged():
    schema = make_schema()
    report = annotate_env(["", "   "], schema)
    for entry in report.entries:
        assert not entry.was_changed


def test_comment_line_passed_through_unchanged():
    schema = make_schema()
    report = annotate_env(["# This is a comment"], schema)
    assert report.entries[0].was_changed is False


def test_line_without_equals_passed_through_unchanged():
    schema = make_schema()
    report = annotate_env(["NOEQUALS"], schema)
    assert report.entries[0].was_changed is False


def test_key_not_in_schema_left_unchanged():
    schema = make_schema()
    report = annotate_env(["UNKNOWN_KEY=value"], schema)
    assert report.entries[0].was_changed is False


def test_key_in_schema_with_description_is_annotated():
    schema = make_schema(API_URL={"description": "API endpoint", "required": True})
    report = annotate_env(["API_URL=https://example.com"], schema)
    assert report.entries[0].was_changed is True
    assert "API endpoint" in report.entries[0].annotated_line


def test_existing_comment_preserved_when_overwrite_false():
    schema = make_schema(HOST={"description": "Hostname", "required": True})
    report = annotate_env(["HOST=localhost  # already documented"], schema, overwrite=False)
    assert report.entries[0].was_changed is False


def test_existing_comment_replaced_when_overwrite_true():
    schema = make_schema(HOST={"description": "Hostname", "required": True})
    report = annotate_env(["HOST=localhost  # old comment"], schema, overwrite=True)
    assert report.entries[0].was_changed is True
    assert "Hostname" in report.entries[0].annotated_line
    assert "old comment" not in report.entries[0].annotated_line


def test_annotated_count_correct():
    schema = make_schema(
        A={"description": "First", "required": True},
        B={"description": "Second", "required": True},
    )
    lines = ["A=1", "B=2", "C=3"]
    report = annotate_env(lines, schema)
    assert report.annotated_count() == 2


def test_unchanged_count_correct():
    schema = make_schema(A={"description": "First", "required": True})
    lines = ["A=1", "B=2", "", "# comment"]
    report = annotate_env(lines, schema)
    assert report.unchanged_count() == 3


def test_result_lines_length_matches_input():
    schema = make_schema(X={"description": "Var", "required": True})
    lines = ["X=1", "Y=2", ""]
    report = annotate_env(lines, schema)
    assert len(report.result_lines()) == len(lines)
