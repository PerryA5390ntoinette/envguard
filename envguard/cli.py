"""CLI entry point for envguard."""

import sys
from pathlib import Path

import click

from envguard.loader import load_env_file
from envguard.schema import EnvSchema
from envguard.validator import validate


@click.command()
@click.argument("env_file", default=".env", metavar="ENV_FILE")
@click.option(
    "--schema",
    "-s",
    default=".env.schema.json",
    show_default=True,
    help="Path to the JSON schema file.",
)
@click.option("--strict", is_flag=True, default=False, help="Treat warnings as errors.")
@click.option("--quiet", "-q", is_flag=True, default=False, help="Only show failures.")
def main(env_file: str, schema: str, strict: bool, quiet: bool) -> None:
    """Validate ENV_FILE against a JSON schema."""
    try:
        env_vars = load_env_file(env_file)
    except FileNotFoundError as exc:
        click.secho(f"Error: {exc}", fg="red", err=True)
        sys.exit(2)

    try:
        env_schema = EnvSchema.load(schema)
    except (FileNotFoundError, ValueError) as exc:
        click.secho(f"Schema error: {exc}", fg="red", err=True)
        sys.exit(2)

    report = validate(env_vars, env_schema)

    for result in report.results:
        if result.passed and quiet:
            continue
        if result.passed:
            click.secho(f"  ✔ {result.message}", fg="green")
        elif result.level == "warning":
            click.secho(f"  ⚠ {result.message}", fg="yellow")
        else:
            click.secho(f"  ✘ {result.message}", fg="red")

    total = len(report.results)
    errors = len(report.errors)
    warnings = len(report.warnings)
    click.echo(f"\nValidated {total} variable(s): {errors} error(s), {warnings} warning(s).")

    if not report.passed or (strict and warnings):
        sys.exit(1)
    click.secho("All checks passed.", fg="green")


if __name__ == "__main__":
    main()
