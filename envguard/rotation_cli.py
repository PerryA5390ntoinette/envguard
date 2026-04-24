"""rotation_cli.py – CLI entry-point for the rotation-check sub-command."""
from __future__ import annotations

import argparse
import sys

from envguard.loader import load_env_files
from envguard.rotator import check_rotation
from envguard.rotation_reporter import print_rotation_report


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="envguard rotate",
        description="Flag environment variables that may need rotation.",
    )
    parser.add_argument(
        "env_files",
        nargs="+",
        metavar="FILE",
        help="One or more .env files to inspect.",
    )
    parser.add_argument(
        "--no-color",
        action="store_true",
        default=False,
        help="Disable ANSI colour output.",
    )
    parser.add_argument(
        "--fail-on-candidates",
        action="store_true",
        default=False,
        help="Exit with code 1 when rotation candidates are found.",
    )
    return parser


def run(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    env = load_env_files(args.env_files)
    report = check_rotation(env)
    print_rotation_report(report, use_color=not args.no_color)

    if args.fail_on_candidates and report.has_candidates:
        return 1
    return 0


if __name__ == "__main__":  # pragma: no cover
    sys.exit(run())
