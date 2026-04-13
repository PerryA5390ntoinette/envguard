"""Orchestrates the full envguard pipeline from load to score."""
from dataclasses import dataclass, field
from typing import Dict, Optional

from envguard.schema import EnvSchema
from envguard.loader import load_env_file
from envguard.interpolator import interpolate, InterpolationReport
from envguard.auditor import audit
from envguard.validator import ValidationReport
from envguard.linter import lint, LintReport
from envguard.redactor import redact_env, RedactionReport
from envguard.scorer import compute_score, ScoreReport


@dataclass
class PipelineResult:
    raw_env: Dict[str, str] = field(default_factory=dict)
    interpolation_report: Optional[InterpolationReport] = None
    validation_report: Optional[ValidationReport] = None
    lint_report: Optional[LintReport] = None
    redaction_report: Optional[RedactionReport] = None
    score_report: Optional[ScoreReport] = None

    def success(self) -> bool:
        if self.validation_report and self.validation_report.has_errors():
            return False
        if self.lint_report and self.lint_report.error_count() > 0:
            return False
        return True


def run_pipeline(
    env_path: str,
    schema: EnvSchema,
    interpolate_vars: bool = True,
    score: bool = True,
) -> PipelineResult:
    result = PipelineResult()

    result.raw_env = load_env_file(env_path)

    env = dict(result.raw_env)

    if interpolate_vars:
        interp = interpolate(env)
        result.interpolation_report = interp
        env = interp.resolved

    result.validation_report = audit(env, schema)

    with open(env_path, "r", encoding="utf-8") as fh:
        lines = fh.readlines()
    result.lint_report = lint(lines)

    result.redaction_report = redact_env(env)

    if score:
        vr = result.validation_report
        lr = result.lint_report
        rr = result.redaction_report
        result.score_report = compute_score(
            audit_errors=vr.error_count() if vr else 0,
            audit_warnings=vr.warning_count() if vr else 0,
            lint_errors=lr.error_count() if lr else 0,
            lint_warnings=lr.warning_count() if lr else 0,
            exposed_secrets=rr.redaction_count() if rr else 0,
        )

    return result
