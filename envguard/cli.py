"""Command-line interface for envguard."""

from __future__ import annotations

import sys
from pathlib import Path

import click

from envguard.auditor import audit
from envguard.exporter import export_report
from envguard.loader import load_env_file
from envguard.reporter import print_report
from envguard.schema import EnvSchema


@click.command()
@click.argument("env_file", default=".env", metavar="ENV_FILE")
@click.option(
    "--schema",
    "schema_file",
    default=".envschema.json",
    show_default=True,
    help="Path to the JSON schema file.",
)
@click.option(
    "--no-color",
    is_flag=True,
    default=False,
    help="Disable colored output.",
)
@click.option(
    "--export",
    "export_fmt",
    default=None,
    type=click.Choice(["json", "csv"], case_sensitive=False),
    help="Export audit results to the given format and print to stdout.",
)
@click.option(
    "--output",
    "output_file",
    default=None,
    type=click.Path(dir_okay=False, writable=True),
    help="Write exported results to this file instead of stdout.",
)
def main(
    env_file: str,
    schema_file: str,
    no_color: bool,
    export_fmt: str | None,
    output_file: str | None,
) -> None:
    """Validate ENV_FILE against a schema and report issues."""
    schema_path = Path(schema_file)
    if not schema_path.exists():
        click.echo(f"Schema file not found: {schema_file}", err=True)
        sys.exit(2)

    env_path = Path(env_file)
    if not env_path.exists():
        click.echo(f"Env file not found: {env_file}", err=True)
        sys.exit(2)

    schema = EnvSchema.load(schema_path)
    env_vars = load_env_file(env_path)
    report = audit(env_vars, schema)

    if export_fmt:
        content = export_report(report, export_fmt)
        if output_file:
            Path(output_file).write_text(content, encoding="utf-8")
            click.echo(f"Results written to {output_file}")
        else:
            click.echo(content)
    else:
        print_report(report, use_color=not no_color)

    if report.error_count > 0:
        sys.exit(1)
