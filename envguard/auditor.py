"""Auditor module: cross-checks loaded .env values against an EnvSchema."""

from typing import Dict
from envguard.schema import EnvSchema, VariableSchema
from envguard.validator import ValidationReport


def _check_required(name: str, spec: VariableSchema, env: Dict[str, str], report: ValidationReport) -> None:
    """Emit an error if a required variable is absent."""
    if spec.required and name not in env:
        report.add_error(name, "required variable is missing")


def _check_pattern(name: str, spec: VariableSchema, value: str, report: ValidationReport) -> None:
    """Emit an error if the value does not match the declared regex pattern."""
    if spec.pattern is None:
        return
    import re
    if not re.fullmatch(spec.pattern, value):
        report.add_error(
            name,
            f"value does not match pattern '{spec.pattern}'",
        )


def _check_allowed_values(name: str, spec: VariableSchema, value: str, report: ValidationReport) -> None:
    """Emit an error if the value is not in the allowed set."""
    if not spec.allowed_values:
        return
    if value not in spec.allowed_values:
        allowed = ", ".join(spec.allowed_values)
        report.add_error(name, f"value '{value}' is not in allowed values: [{allowed}]")


def _check_unknown(env: Dict[str, str], schema: EnvSchema, report: ValidationReport) -> None:
    """Emit a warning for every variable present in .env but not declared in the schema."""
    for name in env:
        if name not in schema.variables:
            report.add_warning(name, "variable is not declared in schema")


def audit(env: Dict[str, str], schema: EnvSchema) -> ValidationReport:
    """Run all audit checks and return a populated ValidationReport."""
    report = ValidationReport()

    for name, spec in schema.variables.items():
        if name in env:
            value = env[name]
            _check_pattern(name, spec, value, report)
            _check_allowed_values(name, spec, value, report)
            report.add_passed(name)
        else:
            if spec.default is not None:
                report.add_warning(name, f"variable missing; default '{spec.default}' will be used")
            else:
                _check_required(name, spec, env, report)

    _check_unknown(env, schema, report)
    return report
