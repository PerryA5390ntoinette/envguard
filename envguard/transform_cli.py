"""CLI sub-command for applying value transformations to a .env file."""

import argparse
import json
import sys
from envguard.loader import load_env_file
from envguard.transformer import transform_env
from envguard.transform_reporter import print_transform_report


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="envguard transform",
        description="Apply named transformation rules to .env variable values.",
    )
    parser.add_argument("env_file", help="Path to the .env file to transform.")
    parser.add_argument(
        "--rule",
        metavar="KEY=RULE",
        action="append",
        default=[],
        help=(
            "Rule to apply in KEY=RULE format. "
            "Rules: upper, lower, strip, quote, unquote. "
            "Repeatable."
        ),
    )
    parser.add_argument(
        "--rules-file",
        metavar="FILE",
        help="JSON file mapping variable names to rule names.",
    )
    parser.add_argument("--no-color", action="store_true", help="Disable colored output.")
    return parser


def _parse_rules(rule_args: list, rules_file: str | None) -> dict:
    rules: dict = {}
    if rules_file:
        with open(rules_file) as fh:
            rules.update(json.load(fh))
    for item in rule_args:
        if "=" not in item:
            print(f"Invalid --rule format (expected KEY=RULE): {item}", file=sys.stderr)
            sys.exit(1)
        key, rule = item.split("=", 1)
        rules[key.strip()] = rule.strip()
    return rules


def run(argv: list | None = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)

    env = load_env_file(args.env_file)
    rules = _parse_rules(args.rule, args.rules_file)

    if not rules:
        print("No rules specified. Use --rule KEY=RULE or --rules-file.", file=sys.stderr)
        sys.exit(1)

    report = transform_env(env, rules)
    print_transform_report(report, use_color=not args.no_color)


if __name__ == "__main__":  # pragma: no cover
    run()
