"""Tests for envguard.templater and envguard.template_reporter."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

import pytest

from envguard.templater import (
    TemplateEntry,
    TemplateReport,
    _make_placeholder,
    generate_template,
    render_template,
)
from envguard.template_reporter import format_template_report


# ---------------------------------------------------------------------------
# Minimal schema stubs
# ---------------------------------------------------------------------------

@dataclass
class _Var:
    name: str
    required: bool = True
    default: Optional[str] = None
    description: str = ""


@dataclass
class _Schema:
    variables: List[_Var] = field(default_factory=list)
    source: str = "test"


def make_schema(*vars_: _Var) -> _Schema:
    return _Schema(variables=list(vars_))


# ---------------------------------------------------------------------------
# _make_placeholder
# ---------------------------------------------------------------------------

def test_placeholder_uses_example_when_provided():
    assert _make_placeholder("DB_HOST", "localhost") == "localhost"


def test_placeholder_falls_back_to_key_based_string():
    result = _make_placeholder("DB_HOST")
    assert result == "<db_host>"


def test_placeholder_lowercases_key():
    result = _make_placeholder("API_URL")
    assert "api_url" in result


# ---------------------------------------------------------------------------
# generate_template
# ---------------------------------------------------------------------------

def test_generate_returns_template_report():
    schema = make_schema(_Var("PORT", required=True))
    report = generate_template(schema)
    assert isinstance(report, TemplateReport)


def test_generate_total_matches_schema_variables():
    schema = make_schema(_Var("A"), _Var("B"), _Var("C"))
    report = generate_template(schema)
    assert report.total == 3


def test_generate_required_count():
    schema = make_schema(_Var("A", required=True), _Var("B", required=False))
    report = generate_template(schema)
    assert report.required_count == 1
    assert report.optional_count == 1


def test_generate_uses_env_value_as_example_for_plain_key():
    schema = make_schema(_Var("APP_URL", required=True))
    report = generate_template(schema, env={"APP_URL": "http://localhost"})
    assert report.entries[0].example == "http://localhost"


def test_generate_redacts_sensitive_key():
    schema = make_schema(_Var("DB_PASSWORD", required=True))
    report = generate_template(schema, env={"DB_PASSWORD": "supersecret"})
    assert report.entries[0].example == "<redacted>"


def test_generate_redacts_token_key():
    schema = make_schema(_Var("AUTH_TOKEN", required=True))
    report = generate_template(schema, env={"AUTH_TOKEN": "tok_abc123"})
    assert report.entries[0].example == "<redacted>"


def test_generate_uses_default_when_no_env():
    schema = make_schema(_Var("LOG_LEVEL", required=False, default="info"))
    report = generate_template(schema)
    assert report.entries[0].placeholder == "info"


# ---------------------------------------------------------------------------
# render_template
# ---------------------------------------------------------------------------

def test_render_includes_key():
    entry = TemplateEntry(key="PORT", placeholder="<port>", required=True)
    report = TemplateReport(entries=[entry])
    output = render_template(report)
    assert "PORT=<port>" in output


def test_render_includes_required_comment():
    entry = TemplateEntry(key="PORT", placeholder="<port>", required=True)
    report = TemplateReport(entries=[entry])
    output = render_template(report, comments=True)
    assert "required" in output


def test_render_no_comments_omits_hash_lines():
    entry = TemplateEntry(key="PORT", placeholder="<port>", required=False)
    report = TemplateReport(entries=[entry])
    output = render_template(report, comments=False)
    assert "#" not in output


def test_render_ends_with_newline():
    report = TemplateReport(entries=[
        TemplateEntry(key="X", placeholder="<x>", required=True)
    ])
    assert render_template(report).endswith("\n")


# ---------------------------------------------------------------------------
# format_template_report
# ---------------------------------------------------------------------------

def test_format_report_header_present():
    report = TemplateReport()
    out = format_template_report(report, use_color=False)
    assert "Template Report" in out


def test_format_report_empty_shows_message():
    report = TemplateReport()
    out = format_template_report(report, use_color=False)
    assert "No variables" in out


def test_format_report_key_present():
    entry = TemplateEntry(key="DB_HOST", placeholder="<db_host>", required=True)
    report = TemplateReport(entries=[entry])
    out = format_template_report(report, use_color=False)
    assert "DB_HOST" in out


def test_format_report_summary_counts():
    entries = [
        TemplateEntry(key="A", placeholder="<a>", required=True),
        TemplateEntry(key="B", placeholder="<b>", required=False),
    ]
    report = TemplateReport(entries=entries)
    out = format_template_report(report, use_color=False)
    assert "Total: 2" in out
    assert "Required: 1" in out
    assert "Optional: 1" in out
