"""CLI sub-commands for pinning and drift-checking .env files."""
from __future__ import annotations

import argparse
import sys

from envguard.loader import load_env_file
from envguard.pinner import pin_env, save_pinfile, load_pinfile, detect_drift
from envguard.pin_reporter import print_pin_report, print_drift_report


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="envguard-pin",
        description="Pin and drift-check .env variable values.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    pin_p = sub.add_parser("pin", help="Pin current env values to a lockfile.")
    pin_p.add_argument("env_file", help="Path to the .env file.")
    pin_p.add_argument(
        "--output", "-o", default=".env.lock", help="Output lockfile path (default: .env.lock)."
    )
    pin_p.add_argument("--color", action="store_true", help="Enable colored output.")

    drift_p = sub.add_parser("drift", help="Check current env against a pinfile.")
    drift_p.add_argument("env_file", help="Path to the .env file.")
    drift_p.add_argument(
        "--pinfile", "-p", default=".env.lock", help="Path to the lockfile (default: .env.lock)."
    )
    drift_p.add_argument("--color", action="store_true", help="Enable colored output.")
    drift_p.add_argument(
        "--fail-on-drift", action="store_true", help="Exit with code 1 if drift is detected."
    )

    return parser


def run(argv: list[str] | None = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "pin":
        env = load_env_file(args.env_file)
        report = pin_env(env, source=args.env_file)
        save_pinfile(report, args.output)
        print_pin_report(report, use_color=args.color)
        print(f"\nPinfile saved to: {args.output}")

    elif args.command == "drift":
        try:
            pinned = load_pinfile(args.pinfile)
        except FileNotFoundError:
            print(f"Error: pinfile not found: {args.pinfile}", file=sys.stderr)
            sys.exit(2)
        env = load_env_file(args.env_file)
        drifts = detect_drift(pinned, env)
        print_drift_report(drifts, use_color=args.color)
        if args.fail_on_drift and drifts:
            sys.exit(1)


if __name__ == "__main__":
    run()
