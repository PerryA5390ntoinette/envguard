"""CLI sub-command for deprecation checking."""
from __future__ import annotations

import argparse
import json
import sys
from typing import Dict, Optional

from envguard.loader import load_env_file
from envguard.deprecator import check_deprecations
from envguard.deprecation_reporter import print_deprecation_report


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="envguard-deprecate",
        description="Check .env files for deprecated variable names.",
    )
    parser.add_argument(
        "env_file",
        help="Path to the .env file to check.",
    )
    parser.add_argument(
        "--deprecations",
        required=True,
        metavar="FILE",
        help="JSON file mapping deprecated keys to {reason, replacement}.",
    )
    parser.add_argument(
        "--no-color",
        action="store_true",
        default=False,
        help="Disable colored output.",
    )
    parser.add_argument(
        "--exit-code",
        action="store_true",
        default=False,
        help="Exit with code 1 if deprecations are found.",
    )
    return parser


def _load_deprecations(path: str) -> Dict[str, Dict[str, Optional[str]]]:
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def run(argv=None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        env = load_env_file(args.env_file)
    except FileNotFoundError:
        print(f"Error: env file not found: {args.env_file}", file=sys.stderr)
        return 2

    try:
        dep_map = _load_deprecations(args.deprecations)
    except (FileNotFoundError, json.JSONDecodeError) as exc:
        print(f"Error loading deprecations file: {exc}", file=sys.stderr)
        return 2

    report = check_deprecations(env, dep_map)
    print_deprecation_report(report, use_color=not args.no_color)

    if args.exit_code and report.has_deprecations:
        return 1
    return 0


if __name__ == "__main__":  # pragma: no cover
    sys.exit(run())
