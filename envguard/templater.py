"""Template generator: produces a .env.template file from a schema or existing env."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from envguard.schema import EnvSchema


@dataclass
class TemplateEntry:
    key: str
    placeholder: str
    required: bool
    description: str = ""
    example: str = ""


@dataclass
class TemplateReport:
    entries: List[TemplateEntry] = field(default_factory=list)
    source: str = ""

    @property
    def total(self) -> int:
        return len(self.entries)

    @property
    def required_count(self) -> int:
        return sum(1 for e in self.entries if e.required)

    @property
    def optional_count(self) -> int:
        return sum(1 for e in self.entries if not e.required)


def _make_placeholder(key: str, example: Optional[str] = None) -> str:
    """Return a descriptive placeholder string for a template entry."""
    if example:
        return example
    return f"<{key.lower()}>"


def generate_template(schema: EnvSchema, env: Optional[Dict[str, str]] = None) -> TemplateReport:
    """Build a TemplateReport from a schema, optionally seeding examples from env."""
    report = TemplateReport(source=schema.source if hasattr(schema, 'source') else "")
    for var in schema.variables:
        example = ""
        if env and var.name in env:
            raw = env[var.name]
            # Redact sensitive-looking values
            lower = var.name.lower()
            if any(k in lower for k in ("password", "secret", "token", "key", "auth")):
                example = "<redacted>"
            else:
                example = raw
        placeholder = _make_placeholder(var.name, example or var.default)
        entry = TemplateEntry(
            key=var.name,
            placeholder=placeholder,
            required=var.required,
            description=getattr(var, 'description', ""),
            example=example,
        )
        report.entries.append(entry)
    return report


def render_template(report: TemplateReport, comments: bool = True) -> str:
    """Render the template report to a .env.template string."""
    lines: List[str] = []
    for entry in report.entries:
        if comments:
            req_label = "required" if entry.required else "optional"
            desc = f"  # {entry.description}" if entry.description else ""
            lines.append(f"# [{req_label}]{desc}")
        lines.append(f"{entry.key}={entry.placeholder}")
        if comments:
            lines.append("")
    return "\n".join(lines).rstrip() + "\n"
