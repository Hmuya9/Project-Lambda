#!/usr/bin/env python3
"""Project Lambda — Role-to-Roadmap Engine (CLI)."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from dotenv import load_dotenv

from lambda_core.generator import generate_contract, validate_config
from lambda_core.inputs import resolve_input
from lambda_core.outputs import default_output_path, render_markdown, write_markdown

ROOT = Path(__file__).resolve().parent
DEFAULT_OUTPUTS = ROOT / "outputs"


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="project-lambda",
        description=(
            "Translate a technical job description + engineer background "
            "into a Role-to-Roadmap: expensive problems, mental models, "
            "skill dependencies, investigation roadmap, proof-of-work ladder, "
            "evidence plan, and interview readiness."
        ),
    )
    p.add_argument(
        "--job",
        "-j",
        help="Path to job description file (.md or .txt).",
    )
    p.add_argument(
        "--profile",
        "-p",
        help="Path to engineer profile / background file (.md or .txt).",
    )
    p.add_argument(
        "--interactive",
        "-i",
        action="store_true",
        help="Paste missing job/profile text interactively (end with a line: END).",
    )
    p.add_argument(
        "--out",
        "-o",
        help="Output Markdown path (default: outputs/roadmap_<timestamp>.md).",
    )
    p.add_argument(
        "--json",
        action="store_true",
        help="Also write a .json sidecar next to the Markdown file.",
    )
    p.add_argument(
        "--stdout",
        action="store_true",
        help="Print Markdown to stdout in addition to writing the file.",
    )
    return p


def main(argv: list[str] | None = None) -> int:
    load_dotenv(ROOT / ".env")
    args = build_parser().parse_args(argv)

    try:
        validate_config()
    except RuntimeError as exc:
        print(f"Config error: {exc}", file=sys.stderr)
        return 2

    try:
        job = resolve_input(
            file_path=args.job,
            interactive_label="job description",
            allow_interactive=args.interactive or (not args.job and not args.profile),
        )
        profile = resolve_input(
            file_path=args.profile,
            interactive_label="engineer profile / background",
            allow_interactive=args.interactive or (not args.job and not args.profile),
        )
    except (FileNotFoundError, ValueError) as exc:
        print(f"Input error: {exc}", file=sys.stderr)
        return 2

    job_source = args.job or "interactive"
    profile_source = args.profile or "interactive"

    print("Generating Role-to-Roadmap...", file=sys.stderr)
    try:
        contract = generate_contract(job, profile)
    except Exception as exc:
        print(f"Generation failed: {exc}", file=sys.stderr)
        return 1

    markdown = render_markdown(
        contract,
        job_source=job_source,
        profile_source=profile_source,
    )

    out_path = Path(args.out) if args.out else default_output_path(DEFAULT_OUTPUTS)
    write_markdown(markdown, out_path)

    if args.json:
        json_path = out_path.with_suffix(".json")
        json_path.write_text(json.dumps(contract, indent=2), encoding="utf-8")
        print(f"Wrote JSON: {json_path}", file=sys.stderr)

    print(f"Wrote Markdown: {out_path}", file=sys.stderr)
    if args.stdout:
        print(markdown)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
