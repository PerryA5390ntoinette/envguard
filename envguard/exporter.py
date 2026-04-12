"""Export audit results to different output formats (JSON, CSV)."""

from __future__ import annotations

import csv
import io
import json
from typing import Any

from envguard.validator import ValidationReport, ValidationResult


def _result_to_dict(result: ValidationResult) -> dict[str, Any]:
    """Convert a ValidationResult to a plain dictionary."""
    return {
        "variable": result.variable,
        "status": result.status,
        "message": result.message,
    }


def export_json(report: ValidationReport, indent: int = 2) -> str:
    """Serialize a ValidationReport to a JSON string."""
    data: dict[str, Any] = {
        "summary": {
            "errors": report.error_count,
            "warnings": report.warning_count,
            "passed": report.passed_count,
        },
        "results": [_result_to_dict(r) for r in report.results],
    }
    return json.dumps(data, indent=indent)


def export_csv(report: ValidationReport) -> str:
    """Serialize a ValidationReport to a CSV string."""
    output = io.StringIO()
    fieldnames = ["variable", "status", "message"]
    writer = csv.DictWriter(output, fieldnames=fieldnames, lineterminator="\n")
    writer.writeheader()
    for result in report.results:
        writer.writerow(_result_to_dict(result))
    return output.getvalue()


def export_report(report: ValidationReport, fmt: str) -> str:
    """Export a report in the requested format ('json' or 'csv').

    Raises ValueError for unsupported formats.
    """
    fmt = fmt.lower()
    if fmt == "json":
        return export_json(report)
    if fmt == "csv":
        return export_csv(report)
    raise ValueError(f"Unsupported export format: {fmt!r}. Choose 'json' or 'csv'.")
