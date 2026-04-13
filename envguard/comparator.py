"""Compare two .env files and produce a structured comparison report."""

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class ComparisonEntry:
    key: str
    left_value: Optional[str]
    right_value: Optional[str]
    status: str  # 'match', 'mismatch', 'left_only', 'right_only'


@dataclass
class ComparisonReport:
    left_label: str
    right_label: str
    entries: List[ComparisonEntry] = field(default_factory=list)

    @property
    def matches(self) -> List[ComparisonEntry]:
        return [e for e in self.entries if e.status == "match"]

    @property
    def mismatches(self) -> List[ComparisonEntry]:
        return [e for e in self.entries if e.status == "mismatch"]

    @property
    def left_only(self) -> List[ComparisonEntry]:
        return [e for e in self.entries if e.status == "left_only"]

    @property
    def right_only(self) -> List[ComparisonEntry]:
        return [e for e in self.entries if e.status == "right_only"]

    @property
    def is_identical(self) -> bool:
        return len(self.mismatches) == 0 and len(self.left_only) == 0 and len(self.right_only) == 0


def compare_envs(
    left: Dict[str, str],
    right: Dict[str, str],
    left_label: str = "left",
    right_label: str = "right",
) -> ComparisonReport:
    """Compare two env dicts and return a ComparisonReport."""
    report = ComparisonReport(left_label=left_label, right_label=right_label)
    all_keys = sorted(set(left) | set(right))

    for key in all_keys:
        in_left = key in left
        in_right = key in right

        if in_left and in_right:
            status = "match" if left[key] == right[key] else "mismatch"
            report.entries.append(
                ComparisonEntry(
                    key=key,
                    left_value=left[key],
                    right_value=right[key],
                    status=status,
                )
            )
        elif in_left:
            report.entries.append(
                ComparisonEntry(key=key, left_value=left[key], right_value=None, status="left_only")
            )
        else:
            report.entries.append(
                ComparisonEntry(key=key, left_value=None, right_value=right[key], status="right_only")
            )

    return report
