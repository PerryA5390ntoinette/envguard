"""Annotates .env variables with inline comments based on schema metadata."""
from dataclasses import dataclass, field
from typing import Dict, List, Optional
from envguard.schema import EnvSchema


@dataclass
class AnnotationEntry:
    key: str
    original_line: str
    annotated_line: str
    annotation: str
    was_changed: bool


@dataclass
class AnnotationReport:
    entries: List[AnnotationEntry] = field(default_factory=list)

    def annotated_count(self) -> int:
        return sum(1 for e in self.entries if e.was_changed)

    def unchanged_count(self) -> int:
        return sum(1 for e in self.entries if not e.was_changed)

    def result_lines(self) -> List[str]:
        return [e.annotated_line for e in self.entries]


def _build_annotation(key: str, schema: EnvSchema) -> Optional[str]:
    """Build an inline comment string from schema metadata for a given key."""
    var = schema.variables.get(key)
    if var is None:
        return None
    parts = []
    if var.description:
        parts.append(var.description)
    if not var.required:
        parts.append("optional")
    if var.allowed_values:
        parts.append("allowed: " + ", ".join(str(v) for v in var.allowed_values))
    if var.pattern:
        parts.append(f"pattern: {var.pattern}")
    return "; ".join(parts) if parts else None


def annotate_env(
    env_lines: List[str],
    schema: EnvSchema,
    overwrite: bool = False,
) -> AnnotationReport:
    """Annotate each KEY=VALUE line with schema-derived inline comments.

    Args:
        env_lines: Raw lines from a .env file.
        schema: Parsed EnvSchema used to source metadata.
        overwrite: If True, replace any existing inline comment; otherwise skip
                   lines that already carry a comment.
    Returns:
        AnnotationReport with per-line entries.
    """
    report = AnnotationReport()
    for raw in env_lines:
        line = raw.rstrip("\n")
        stripped = line.strip()
        # Pass through blank lines and comment-only lines unchanged.
        if not stripped or stripped.startswith("#"):
            report.entries.append(
                AnnotationEntry(
                    key="",
                    original_line=line,
                    annotated_line=line,
                    annotation="",
                    was_changed=False,
                )
            )
            continue
        if "=" not in stripped:
            report.entries.append(
                AnnotationEntry(
                    key="",
                    original_line=line,
                    annotated_line=line,
                    annotation="",
                    was_changed=False,
                )
            )
            continue
        # Separate value portion from any existing inline comment.
        key_part, _, rest = stripped.partition("=")
        key = key_part.strip()
        has_existing_comment = "  #" in rest or rest.strip().startswith("#")
        if has_existing_comment and not overwrite:
            report.entries.append(
                AnnotationEntry(
                    key=key,
                    original_line=line,
                    annotated_line=line,
                    annotation="",
                    was_changed=False,
                )
            )
            continue
        annotation = _build_annotation(key, schema)
        if annotation is None:
            report.entries.append(
                AnnotationEntry(
                    key=key,
                    original_line=line,
                    annotated_line=line,
                    annotation="",
                    was_changed=False,
                )
            )
            continue
        # Strip any pre-existing inline comment before appending the new one.
        if has_existing_comment and overwrite:
            value_clean = rest.split("  #")[0].rstrip()
            base_line = f"{key}={value_clean}"
        else:
            base_line = line.rstrip()
        new_line = f"{base_line}  # {annotation}"
        report.entries.append(
            AnnotationEntry(
                key=key,
                original_line=line,
                annotated_line=new_line,
                annotation=annotation,
                was_changed=True,
            )
        )
    return report
