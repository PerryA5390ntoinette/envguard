"""Transform .env variable values using named rules (upper, lower, strip, quote, unquote)."""

from dataclasses import dataclass, field
from typing import Dict, List, Optional

KNOWN_RULES = {"upper", "lower", "strip", "quote", "unquote"}


@dataclass
class TransformEntry:
    key: str
    original: str
    transformed: str
    rule: str
    skipped: bool = False
    skip_reason: Optional[str] = None


@dataclass
class TransformReport:
    entries: List[TransformEntry] = field(default_factory=list)

    def transformed_count(self) -> int:
        return sum(1 for e in self.entries if not e.skipped)

    def skipped_count(self) -> int:
        return sum(1 for e in self.entries if e.skipped)

    def result_env(self) -> Dict[str, str]:
        return {e.key: e.transformed for e in self.entries}


def _apply_rule(value: str, rule: str) -> str:
    if rule == "upper":
        return value.upper()
    if rule == "lower":
        return value.lower()
    if rule == "strip":
        return value.strip()
    if rule == "quote":
        inner = value.strip('"')
        return f'"{inner}"'
    if rule == "unquote":
        return value.strip('"').strip("'")
    raise ValueError(f"Unknown rule: {rule}")


def transform_env(
    env: Dict[str, str],
    rules: Dict[str, str],
) -> TransformReport:
    """Apply per-key transformation rules to an env dict.

    Args:
        env:   The loaded environment variables.
        rules: Mapping of variable name -> rule name.

    Returns:
        A TransformReport with one entry per key in *rules*.
    """
    report = TransformReport()

    for key, rule in rules.items():
        if rule not in KNOWN_RULES:
            entry = TransformEntry(
                key=key,
                original=env.get(key, ""),
                transformed=env.get(key, ""),
                rule=rule,
                skipped=True,
                skip_reason=f"unknown rule '{rule}'",
            )
            report.entries.append(entry)
            continue

        if key not in env:
            entry = TransformEntry(
                key=key,
                original="",
                transformed="",
                rule=rule,
                skipped=True,
                skip_reason="key not present in env",
            )
            report.entries.append(entry)
            continue

        original = env[key]
        transformed = _apply_rule(original, rule)
        report.entries.append(
            TransformEntry(key=key, original=original, transformed=transformed, rule=rule)
        )

    return report
