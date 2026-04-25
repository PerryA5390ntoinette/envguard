"""Core validation logic for envguard."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional

from envguard.schema import EnvSchema, VariableSchema


@dataclass
class ValidationResult:
    level: str  # 'error' | 'warning' | 'info'
    variable: str
    message: str


@dataclass
class ValidationReport:
    errors: List[ValidationResult] = field(default_factory=list)
    warnings: List[ValidationResult] = field(default_factory=list)
    passed: List[ValidationResult] = field(default_factory=list)

    def add_error(self, variable: str, message: str) -> None:
        self.errors.append(ValidationResult(level="error", variable=variable, message=message))

    def add_warning(self, variable: str, message: str) -> None:
        self.warnings.append(ValidationResult(level="warning", variable=variable, message=message))

    def add_passed(self, variable: str, message: str = "OK") -> None:
        self.passed.append(ValidationResult(level="info", variable=variable, message=message))

    @property
    def is_valid(self) -> bool:
        return len(self.errors) == 0


def _has_error_for(var_name: str, report: ValidationReport) -> bool:
    """Return True if the report already contains an error for the given variable."""
    return any(e.variable == var_name for e in report.errors)


def _check_required(var_name: str, schema: VariableSchema, env: Dict[str, str], report: ValidationReport) -> bool:
    """Returns True if the variable is present (or not required)."""
    if var_name not in env or env[var_name] == "":
        if schema.required:
            report.add_error(var_name, "Missing required variable")
            return False
        elif schema.default is None:
            report.add_warning(var_name, "Optional variable is not set and has no default")
            return False
    return True


def _check_pattern(var_name: str, schema: VariableSchema, value: str, report: ValidationReport) -> None:
    if schema.pattern and not re.fullmatch(schema.pattern, value):
        report.add_warning(
            var_name,
            f"Value does not match expected pattern '{schema.pattern}'",
        )


def _check_allowed_values(var_name: str, schema: VariableSchema, value: str, report: ValidationReport) -> None:
    if schema.allowed_values and value not in schema.allowed_values:
        allowed = ", ".join(schema.allowed_values)
        report.add_error(
            var_name,
            f"Value '{value}' is not one of the allowed values: [{allowed}]",
        )


def validate(env: Dict[str, str], schema: EnvSchema) -> ValidationReport:
    """Validate a parsed env dictionary against an EnvSchema."""
    report = ValidationReport()

    for var_name, var_schema in schema.variables.items():
        present = _check_required(var_name, var_schema, env, report)
        if not present:
            continue

        value = env.get(var_name, var_schema.default or "")
        _check_pattern(var_name, var_schema, value, report)
        _check_allowed_values(var_name, var_schema, value, report)

        if not _has_error_for(var_name, report):
            report.add_passed(var_name)

    return report
