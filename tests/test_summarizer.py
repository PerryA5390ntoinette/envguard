"""Tests for envguard.summarizer."""

from unittest.mock import MagicMock

from envguard.summarizer import summarize, SummaryReport, SummaryLine
from envguard.pipeline import PipelineResult
from envguard.validator import ValidationReport, ValidationResult


def make_pipeline_result(
    sources=None,
    raw_env=None,
    audit_report=None,
    interpolation_report=None,
    lint_report=None,
    score_report=None,
):
    result = MagicMock(spec=PipelineResult)
    result.sources = sources or []
    result.raw_env = raw_env or {}
    result.audit_report = audit_report
    result.interpolation_report = interpolation_report
    result.lint_report = lint_report
    result.score_report = score_report
    return result


def test_summarize_returns_summary_report():
    result = make_pipeline_result()
    report = summarize(result)
    assert isinstance(report, SummaryReport)


def test_source_populated_from_sources():
    result = make_pipeline_result(sources=[".env", ".env.local"])
    report = summarize(result)
    assert ".env" in report.source
    assert ".env.local" in report.source


def test_source_unknown_when_empty():
    result = make_pipeline_result(sources=[])
    report = summarize(result)
    assert "unknown" in report.source


def test_variables_loaded_count():
    result = make_pipeline_result(raw_env={"A": "1", "B": "2", "C": "3"})
    report = summarize(result)
    labels = {line.label: line.value for line in report.lines}
    assert labels["Variables loaded"] == "3"


def test_audit_errors_counted():
    audit = MagicMock()
    audit.results = [
        MagicMock(status="error"),
        MagicMock(status="error"),
        MagicMock(status="warning"),
        MagicMock(status="pass"),
    ]
    result = make_pipeline_result(audit_report=audit)
    report = summarize(result)
    labels = {line.label: line.value for line in report.lines}
    assert labels["Audit errors"] == "2"
    assert labels["Audit warnings"] == "1"
    assert labels["Audit passed"] == "1"


def test_interpolation_warnings_counted():
    interp = MagicMock()
    interp.warnings = [MagicMock(), MagicMock()]
    result = make_pipeline_result(interpolation_report=interp)
    report = summarize(result)
    labels = {line.label: line.value for line in report.lines}
    assert labels["Interpolation warnings"] == "2"


def test_lint_counts_included():
    lint = MagicMock()
    lint.error_count.return_value = 3
    lint.warning_count.return_value = 1
    result = make_pipeline_result(lint_report=lint)
    report = summarize(result)
    labels = {line.label: line.value for line in report.lines}
    assert labels["Lint errors"] == "3"
    assert labels["Lint warnings"] == "1"


def test_score_included():
    score = MagicMock()
    score.score = 85
    score.grade = "B"
    result = make_pipeline_result(score_report=score)
    report = summarize(result)
    labels = {line.label: line.value for line in report.lines}
    assert "85" in labels["Score"]
    assert "B" in labels["Score"]


def test_no_audit_report_skips_audit_lines():
    result = make_pipeline_result(audit_report=None)
    report = summarize(result)
    labels = [line.label for line in report.lines]
    assert "Audit errors" not in labels


def test_summary_line_has_icon_label_value():
    result = make_pipeline_result(raw_env={"X": "1"})
    report = summarize(result)
    line = report.lines[0]
    assert isinstance(line, SummaryLine)
    assert line.icon
    assert line.label
    assert line.value
