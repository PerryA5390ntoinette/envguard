"""High-level pipeline that loads, interpolates, and audits an .env file."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

from envguard.loader import load_env_files
from envguard.schema import EnvSchema
from envguard.interpolator import InterpolationReport, interpolate
from envguard.auditor import ValidationReport, audit
from envguard.suggester import SuggestionReport, generate_suggestions


@dataclass
class PipelineResult:
    env_files: List[str] = field(default_factory=list)
    raw_env: dict = field(default_factory=dict)
    interpolation: Optional[InterpolationReport] = None
    validation: Optional[ValidationReport] = None
    suggestions: Optional[SuggestionReport] = None

    @property
    def success(self) -> bool:
        if self.validation is None:
            return False
        return not self.validation.has_errors


def run_pipeline(
    env_paths: List[str],
    schema: EnvSchema,
    *,
    interpolate_values: bool = True,
) -> PipelineResult:
    """Load env files, optionally interpolate, then audit against *schema*.

    Returns a :class:`PipelineResult` with all intermediate artefacts.
    """
    result = PipelineResult(env_files=list(env_paths))

    raw = load_env_files(env_paths)
    result.raw_env = raw

    if interpolate_values:
        interp_report = interpolate(raw)
        result.interpolation = interp_report
        effective_env = interp_report.resolved
    else:
        effective_env = raw

    validation_report = audit(effective_env, schema)
    result.validation = validation_report

    result.suggestions = generate_suggestions(validation_report)

    return result
