"""CLI entry point for the filter subcommand."""
from __future__ import annotations
import argparse
from envguard.loader import load_env_files
from envguard.filterer import filter_env
from envguard.filter_reporter import print_filter_report


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="envguard filter",
        description="Filter .env variables by prefix, pattern, or explicit key list.",
    )
    parser.add_argument("files", nargs="+", help=".env file(s) to filter")
    parser.add_argument("--prefix", default=None, help="Keep only keys with this prefix")
    parser.add_argument("--pattern", default=None, help="Regex pattern to match key names")
    parser.add_argument(
        "--key", dest="keys", action="append", default=None,
        help="Explicit key to include (repeatable)",
    )
    parser.add_argument(
        "--exclude", dest="exclude_pattern", default=None,
        help="Regex pattern to exclude key names",
    )
    parser.add_argument("--no-color", action="store_true", help="Disable colored output")
    return parser


def run(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    env = load_env_files(args.files)
    report = filter_env(
        env,
        pattern=args.pattern,
        prefix=args.prefix,
        keys=args.keys,
        exclude_pattern=args.exclude_pattern,
    )
    print_filter_report(report, use_color=not args.no_color)
    return 0 if report.matched_count() > 0 else 1


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(run())
