"""Core validation logic for envguard."""

import re
from dataclasses import dataclass, field
from urllib.parse import urlparse

from envguard.schema import EnvSchema, VariableSchema


@dataclass
class ValidationResult:
    variable: str
    passed: bool
    message: str
    level: str = "error"  # "error" or "warning"


@dataclass
class ValidationReport:
    results: list[ValidationResult] = field(default_factory=list)

    @property
    def errors(self) -> list[ValidationResult]:
        return [r for r in self.results if not r.passed and r.level == "error"]

    @property
    def warnings(self) -> list[ValidationResult]:
        return [r for r in self.results if not r.passed and r.level == "warning"]

    @property
    def passed(self) -> bool:
        return len(self.errors) == 0


EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def _check_type(value: str, expected_type: str) -> bool:
    if expected_type == "integer":
        try:
            int(value)
            return True
        except ValueError:
            return False
    if expected_type == "float":
        try:
            float(value)
            return True
        except ValueError:
            return False
    if expected_type == "boolean":
        return value.lower() in {"true", "false", "1", "0", "yes", "no"}
    if expected_type == "url":
        parsed = urlparse(value)
        return parsed.scheme in {"http", "https"} and bool(parsed.netloc)
    if expected_type == "email":
        return bool(EMAIL_RE.match(value))
    return True  # string accepts anything


def validate(env_vars: dict[str, str], schema: EnvSchema) -> ValidationReport:
    report = ValidationReport()
    env_keys = set(env_vars.keys())

    for var_schema in schema.variables:
        name = var_schema.name

        if name not in env_keys:
            if var_schema.required and var_schema.default is None:
                report.results.append(ValidationResult(name, False, f"Required variable '{name}' is missing."))
            else:
                report.results.append(ValidationResult(name, True, f"'{name}' not set; default will be used.", level="warning"))
            continue

        value = env_vars[name]

        if not _check_type(value, var_schema.type):
            report.results.append(ValidationResult(name, False, f"'{name}' expected type '{var_schema.type}', got value '{value}'."))
            continue

        if var_schema.pattern and not re.fullmatch(var_schema.pattern, value):
            report.results.append(ValidationResult(name, False, f"'{name}' does not match pattern '{var_schema.pattern}'."))
            continue

        if var_schema.allowed_values and value not in var_schema.allowed_values:
            report.results.append(ValidationResult(name, False, f"'{name}' value '{value}' not in allowed values: {var_schema.allowed_values}."))
            continue

        report.results.append(ValidationResult(name, True, f"'{name}' is valid."))

    return report
