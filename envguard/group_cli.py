"""CLI helpers for the 'group' subcommand."""

from __future__ import annotations

import argparse
import sys
from typing import List

from envguard.loader import load_env_files
from envguard.grouper import group_env
from envguard.group_reporter import print_group_report


def build_parser(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    """Attach the 'group' subcommand to an existing subparsers action."""
    parser = subparsers.add_parser(
        "group",
        help="Group environment variables by key prefix.",
    )
    parser.add_argument(
        "env_files",
        nargs="+",
        metavar="FILE",
        help="One or more .env files to group.",
    )
    parser.add_argument(
        "--separator",
        default="_",
        metavar="SEP",
        help="Prefix separator (default: '_').",
    )
    parser.add_argument(
        "--min-group-size",
        type=int,
        default=1,
        dest="min_group_size",
        metavar="N",
        help="Minimum variables required to form a group (default: 1).",
    )
    parser.add_argument(
        "--no-color",
        action="store_true",
        default=False,
        help="Disable colored output.",
    )
    parser.set_defaults(func=run)


def run(args: argparse.Namespace) -> int:
    """Execute the group subcommand. Returns exit code."""
    try:
        env = load_env_files(args.env_files)
    except FileNotFoundError as exc:
        print(f"envguard group: error: {exc}", file=sys.stderr)
        return 1

    report = group_env(
        env,
        separator=args.separator,
        min_group_size=args.min_group_size,
    )
    print_group_report(report, use_color=not args.no_color)
    return 0
