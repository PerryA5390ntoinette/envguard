"""Tests for envguard.exporter."""

from __future__ import annotations

import csv
import io
import json

import pytest

from envguard.exporter import export_csv, export_json, export_report
from envguard.validator import ValidationReport, ValidationResult


def make_report() -> ValidationReport:
    report = ValidationReport()
    report.add_error("DB_HOST", "missing required variable")
    report.add_warning("LOG_LEVEL", "not in allowed values")
    report.add_passed("SECRET_KEY", "ok")
    return report


class TestExportJson:
    def test_summary_counts(self):
        report = make_report()
        data = json.loads(export_json(report))
        assert data["summary"]["errors"] == 1
        assert data["summary"]["warnings"] == 1
        assert data["summary"]["passed"] == 1

    def test_results_length(self):
        report = make_report()
        data = json.loads(export_json(report))
        assert len(data["results"]) == 3

    def test_result_fields(self):
        report = make_report()
        data = json.loads(export_json(report))
        first = data["results"][0]
        assert set(first.keys()) == {"variable", "status", "message"}

    def test_error_status_value(self):
        report = make_report()
        data = json.loads(export_json(report))
        error_entries = [r for r in data["results"] if r["status"] == "error"]
        assert len(error_entries) == 1
        assert error_entries[0]["variable"] == "DB_HOST"

    def test_empty_report(self):
        report = ValidationReport()
        data = json.loads(export_json(report))
        assert data["summary"]["errors"] == 0
        assert data["results"] == []


class TestExportCsv:
    def test_csv_has_header(self):
        report = make_report()
        lines = export_csv(report).splitlines()
        assert lines[0] == "variable,status,message"

    def test_csv_row_count(self):
        report = make_report()
        reader = csv.DictReader(io.StringIO(export_csv(report)))
        rows = list(reader)
        assert len(rows) == 3

    def test_csv_warning_row(self):
        report = make_report()
        reader = csv.DictReader(io.StringIO(export_csv(report)))
        rows = {r["variable"]: r for r in reader}
        assert rows["LOG_LEVEL"]["status"] == "warning"

    def test_empty_report_csv(self):
        report = ValidationReport()
        lines = export_csv(report).splitlines()
        assert lines == ["variable,status,message"]


class TestExportReport:
    def test_json_format(self):
        report = make_report()
        output = export_report(report, "json")
        data = json.loads(output)
        assert "summary" in data

    def test_csv_format(self):
        report = make_report()
        output = export_report(report, "csv")
        assert output.startswith("variable,status,message")

    def test_case_insensitive(self):
        report = make_report()
        output = export_report(report, "JSON")
        assert json.loads(output) is not None

    def test_unsupported_format_raises(self):
        report = make_report()
        with pytest.raises(ValueError, match="Unsupported export format"):
            export_report(report, "xml")
