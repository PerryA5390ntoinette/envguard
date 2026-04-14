"""caster.py — coerce env variable string values to their declared types."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class CastEntry:
    key: str
    raw: str
    cast_value: Any
    cast_type: str
    success: bool
    error: Optional[str] = None


@dataclass
class CastReport:
    entries: List[CastEntry] = field(default_factory=list)

    def success_count(self) -> int:
        return sum(1 for e in self.entries if e.success)

    def failure_count(self) -> int:
        return sum(1 for e in self.entries if not e.success)

    def has_failures(self) -> bool:
        return self.failure_count() > 0

    def cast_env(self) -> Dict[str, Any]:
        """Return a dict of successfully cast key→value pairs."""
        return {e.key: e.cast_value for e in self.entries if e.success}


_CASTERS = {
    "int": int,
    "float": float,
    "bool": lambda v: _cast_bool(v),
    "str": str,
}


def _cast_bool(value: str) -> bool:
    normalized = value.strip().lower()
    if normalized in {"true", "1", "yes", "on"}:
        return True
    if normalized in {"false", "0", "no", "off"}:
        return False
    raise ValueError(f"Cannot interpret {value!r} as bool")


def _cast_value(raw: str, cast_type: str):
    caster = _CASTERS.get(cast_type)
    if caster is None:
        raise ValueError(f"Unknown type {cast_type!r}")
    return caster(raw)


def cast_env(
    env: Dict[str, str],
    type_map: Dict[str, str],
) -> CastReport:
    """Cast each key in *env* according to *type_map*.

    Keys absent from *type_map* are treated as ``str`` and always succeed.
    """
    report = CastReport()
    for key, raw in env.items():
        declared = type_map.get(key, "str")
        try:
            cast_value = _cast_value(raw, declared)
            report.entries.append(
                CastEntry(key=key, raw=raw, cast_value=cast_value,
                          cast_type=declared, success=True)
            )
        except (ValueError, TypeError) as exc:
            report.entries.append(
                CastEntry(key=key, raw=raw, cast_value=None,
                          cast_type=declared, success=False,
                          error=str(exc))
            )
    return report
