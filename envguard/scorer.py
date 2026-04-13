"""Scores an .env file based on audit, lint, and redaction results."""
from dataclasses import dataclass, field
from typing import List

MAX_SCORE = 100

_DEDUCTIONS = {
    "error": 10,
    "warning": 3,
    "lint_error": 8,
    "lint_warning": 2,
    "exposed_secret": 15,
}


@dataclass
class ScoreBreakdown:
    audit_errors: int = 0
    audit_warnings: int = 0
    lint_errors: int = 0
    lint_warnings: int = 0
    exposed_secrets: int = 0
    deductions: List[str] = field(default_factory=list)


@dataclass
class ScoreReport:
    score: int
    grade: str
    breakdown: ScoreBreakdown


def _grade(score: int) -> str:
    if score >= 90:
        return "A"
    if score >= 75:
        return "B"
    if score >= 60:
        return "C"
    if score >= 40:
        return "D"
    return "F"


def compute_score(
    audit_errors: int = 0,
    audit_warnings: int = 0,
    lint_errors: int = 0,
    lint_warnings: int = 0,
    exposed_secrets: int = 0,
) -> ScoreReport:
    breakdown = ScoreBreakdown(
        audit_errors=audit_errors,
        audit_warnings=audit_warnings,
        lint_errors=lint_errors,
        lint_warnings=lint_warnings,
        exposed_secrets=exposed_secrets,
    )

    total_deduction = (
        audit_errors * _DEDUCTIONS["error"]
        + audit_warnings * _DEDUCTIONS["warning"]
        + lint_errors * _DEDUCTIONS["lint_error"]
        + lint_warnings * _DEDUCTIONS["lint_warning"]
        + exposed_secrets * _DEDUCTIONS["exposed_secret"]
    )

    if audit_errors > 0:
        breakdown.deductions.append(f"-{audit_errors * _DEDUCTIONS['error']} audit errors")
    if audit_warnings > 0:
        breakdown.deductions.append(f"-{audit_warnings * _DEDUCTIONS['warning']} audit warnings")
    if lint_errors > 0:
        breakdown.deductions.append(f"-{lint_errors * _DEDUCTIONS['lint_error']} lint errors")
    if lint_warnings > 0:
        breakdown.deductions.append(f"-{lint_warnings * _DEDUCTIONS['lint_warning']} lint warnings")
    if exposed_secrets > 0:
        breakdown.deductions.append(f"-{exposed_secrets * _DEDUCTIONS['exposed_secret']} exposed secrets")

    score = max(0, MAX_SCORE - total_deduction)
    return ScoreReport(score=score, grade=_grade(score), breakdown=breakdown)
