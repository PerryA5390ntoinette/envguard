"""Scope variables by environment target (dev, staging, prod)."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional

KNOWN_SCOPES = ("dev", "development", "staging", "prod", "production", "test")


@dataclass
class ScopeEntry:
    key: str
    value: str
    scope: str  # detected scope label or "global"


@dataclass
class ScopeReport:
    entries: List[ScopeEntry] = field(default_factory=list)
    _by_scope: Dict[str, List[ScopeEntry]] = field(default_factory=dict, repr=False)

    def add(self, entry: ScopeEntry) -> None:
        self.entries.append(entry)
        self._by_scope.setdefault(entry.scope, []).append(entry)

    def scopes(self) -> List[str]:
        return list(self._by_scope.keys())

    def entries_for(self, scope: str) -> List[ScopeEntry]:
        return self._by_scope.get(scope, [])

    def total(self) -> int:
        return len(self.entries)

    def global_count(self) -> int:
        return len(self._by_scope.get("global", []))


def _detect_scope(key: str) -> str:
    lower = key.lower()
    for scope in KNOWN_SCOPES:
        if lower.startswith(scope + "_") or lower.endswith("_" + scope):
            normalized = "prod" if scope in ("prod", "production") else scope
            normalized = "dev" if scope == "development" else normalized
            return normalized
    return "global"


def scope_env(env: Dict[str, str]) -> ScopeReport:
    report = ScopeReport()
    for key, value in env.items():
        scope = _detect_scope(key)
        report.add(ScopeEntry(key=key, value=value, scope=scope))
    return report
