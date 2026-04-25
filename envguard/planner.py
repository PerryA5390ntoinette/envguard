"""planner.py — Generates a migration plan for applying env changes."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class PlanAction:
    action: str          # 'add', 'remove', 'update', 'keep'
    key: str
    old_value: Optional[str] = None
    new_value: Optional[str] = None
    reason: str = ""


@dataclass
class PlanReport:
    actions: List[PlanAction] = field(default_factory=list)

    def add(self, action: PlanAction) -> None:
        self.actions.append(action)

    @property
    def add_count(self) -> int:
        return sum(1 for a in self.actions if a.action == "add")

    @property
    def remove_count(self) -> int:
        return sum(1 for a in self.actions if a.action == "remove")

    @property
    def update_count(self) -> int:
        return sum(1 for a in self.actions if a.action == "update")

    @property
    def keep_count(self) -> int:
        return sum(1 for a in self.actions if a.action == "keep")

    @property
    def has_changes(self) -> bool:
        return self.add_count + self.remove_count + self.update_count > 0


def plan_migration(
    current: Dict[str, str],
    target: Dict[str, str],
    reason_add: str = "present in target, missing in current",
    reason_remove: str = "absent from target",
    reason_update: str = "value differs from target",
) -> PlanReport:
    """Produce a PlanReport describing what must change to move current -> target."""
    report = PlanReport()
    all_keys = set(current) | set(target)

    for key in sorted(all_keys):
        in_current = key in current
        in_target = key in target

        if in_target and not in_current:
            report.add(PlanAction("add", key, None, target[key], reason_add))
        elif in_current and not in_target:
            report.add(PlanAction("remove", key, current[key], None, reason_remove))
        elif current[key] != target[key]:
            report.add(PlanAction("update", key, current[key], target[key], reason_update))
        else:
            report.add(PlanAction("keep", key, current[key], target[key], ""))

    return report
