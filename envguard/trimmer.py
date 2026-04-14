"""Trimmer: removes unused or redundant variables from an env dict based on a schema."""

from dataclasses import dataclass, field
from typing import Dict, List

from envguard.schema import EnvSchema


@dataclass
class TrimEntry:
    key: str
    value: str
    reason: str  # 'unknown' | 'empty_optional'


@dataclass
class TrimReport:
    trimmed: List[TrimEntry] = field(default_factory=list)
    kept: Dict[str, str] = field(default_factory=dict)

    @property
    def trimmed_count(self) -> int:
        return len(self.trimmed)

    @property
    def kept_count(self) -> int:
        return len(self.kept)

    def trimmed_keys(self) -> List[str]:
        return [e.key for e in self.trimmed]


def trim_env(
    env: Dict[str, str],
    schema: EnvSchema,
    *,
    remove_unknown: bool = True,
    remove_empty_optional: bool = False,
) -> TrimReport:
    """Return a TrimReport describing which variables were removed and which were kept.

    Args:
        env: The parsed environment dictionary.
        schema: The EnvSchema to validate against.
        remove_unknown: If True, variables not defined in the schema are trimmed.
        remove_empty_optional: If True, optional variables with empty values are trimmed.

    Returns:
        TrimReport with trimmed entries and the resulting kept dict.
    """
    report = TrimReport()
    schema_keys = {var.name for var in schema.variables}

    for key, value in env.items():
        if remove_unknown and key not in schema_keys:
            report.trimmed.append(TrimEntry(key=key, value=value, reason="unknown"))
            continue

        if remove_empty_optional and key in schema_keys:
            var_schema = next(v for v in schema.variables if v.name == key)
            if not var_schema.required and value == "":
                report.trimmed.append(
                    TrimEntry(key=key, value=value, reason="empty_optional")
                )
                continue

        report.kept[key] = value

    return report
