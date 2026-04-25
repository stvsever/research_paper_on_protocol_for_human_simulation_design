"""Command-line interface for the research paper template."""

from __future__ import annotations

import argparse

from paper_template.pipeline.run_all import run_all


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="paper-template",
        description="Reusable staged scaffold for research paper projects",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("run-all", help="Print the staged workflow scaffold")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    if args.command == "run-all":
        run_all()
        return 0
    return 1
