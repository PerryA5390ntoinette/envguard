"""envguard.labeler — attach custom labels/tags to env variables based on rules."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class LabelEntry:
    key: str
    value: str
    labels: List[str] = field(default_factory=list)

    @property
    def has_labels(self) -> bool:
        return len(self.labels) > 0


@dataclass
class LabelReport:
    entries: List[LabelEntry] = field(default_factory=list)

    def add(self, entry: LabelEntry) -> None:
        self.entries.append(entry)

    @property
    def labeled_count(self) -> int:
        return sum(1 for e in self.entries if e.has_labels)

    @property
    def unlabeled_count(self) -> int:
        return sum(1 for e in self.entries if not e.has_labels)

    @property
    def all_labels(self) -> List[str]:
        seen: List[str] = []
        for entry in self.entries:
            for lbl in entry.labels:
                if lbl not in seen:
                    seen.append(lbl)
        return seen

    def entries_for_label(self, label: str) -> List[LabelEntry]:
        return [e for e in self.entries if label in e.labels]


def _apply_rules(
    key: str,
    value: str,
    rules: Dict[str, List[str]],
) -> List[str]:
    """Return labels whose rule patterns match *key* (case-insensitive prefix/substring)."""
    import re

    matched: List[str] = []
    for label, patterns in rules.items():
        for pattern in patterns:
            if re.search(pattern, key, re.IGNORECASE):
                matched.append(label)
                break
    return matched


DEFAULT_RULES: Dict[str, List[str]] = {
    "secret": [r"password", r"secret", r"token", r"api[_]?key", r"private"],
    "network": [r"host", r"port", r"url", r"endpoint", r"domain"],
    "database": [r"db", r"database", r"mongo", r"postgres", r"mysql", r"redis"],
    "feature_flag": [r"feature", r"flag", r"enable", r"disable", r"toggle"],
}


def label_env(
    env: Dict[str, str],
    rules: Optional[Dict[str, List[str]]] = None,
) -> LabelReport:
    """Assign labels to every variable in *env* using *rules* (defaults to DEFAULT_RULES)."""
    active_rules = rules if rules is not None else DEFAULT_RULES
    report = LabelReport()
    for key, value in env.items():
        labels = _apply_rules(key, value, active_rules)
        report.add(LabelEntry(key=key, value=value, labels=labels))
    return report
