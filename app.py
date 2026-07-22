#!/usr/bin/env python3
"""Project Lambda — CLI.

    python app.py generate -j job.md -p profile.md [--intent targeted] [-o outdir]
    python app.py render plan.json [-o outdir]
"""

from __future__ import annotations

import argparse
import datetime
import json
import sys
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent
DEFAULT_OUTPUTS = ROOT / "outputs"


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="project-lambda",
        description=(
            "Structure study around the expensive problems the market pays for. "
            "Profile + market intent in, evidence-driven plan out."
        ),
    )
    sub = p.add_subparsers(dest="command", required=True)

    gen = sub.add_parser("generate", help="Run the full pipeline (needs ANTHROPIC_API_KEY).")
    gen.add_argument("--job", "-j", required=True, help="Job description or market-composite file (.md/.txt).")
    gen.add_argument("--profile", "-p", required=True, help="Engineer profile file (.md/.txt).")
    gen.add_argument(
        "--intent",
        choices=("targeted", "directional", "exploratory"),
        default="targeted",
        help="Market intent (default: targeted).",
    )
    gen.add_argument("--weeks", type=int, default=8, help="Sprint count (default: 8).")
    gen.add_argument(
        "--project",
        type=int,
        default=None,
        help="Index (0-based) of the pitched project to build around; default: recommended.",
    )
    gen.add_argument("--out", "-o", help="Output directory (default: outputs/<role>_<date>/).")
    gen.add_argument("--no-backlog-update", action="store_true", help="Do not append new problems to data/backlog.md.")

    ren = sub.add_parser("render", help="Render an existing plan.json (offline, no API key).")
    ren.add_argument("plan", help="Path to plan.json.")
    ren.add_argument("--out", "-o", help="Output directory (default: alongside the plan).")
    return p


def _out_dir(base_hint: str | None, role_title: str) -> Path:
    if base_hint:
        return Path(base_hint)
    stamp = datetime.date.today().isoformat()
    slug = "".join(c if c.isalnum() else "_" for c in role_title.lower())[:40] or "plan"
    return DEFAULT_OUTPUTS / f"{slug}_{stamp}"


def cmd_generate(args: argparse.Namespace) -> int:
    from lambda_core.llm import validate_config
    from lambda_core.pipeline import run_pipeline
    from lambda_core.render import render_all

    try:
        validate_config()
    except RuntimeError as exc:
        print(f"Config error: {exc}", file=sys.stderr)
        return 2

    try:
        source = Path(args.job).read_text(encoding="utf-8")
        profile = Path(args.profile).read_text(encoding="utf-8")
    except OSError as exc:
        print(f"Input error: {exc}", file=sys.stderr)
        return 2

    plan = run_pipeline(
        source,
        profile,
        intent=args.intent,
        weeks=args.weeks,
        update_backlog=not args.no_backlog_update,
        project_index=args.project,
    )

    out = _out_dir(args.out, plan["meta"].get("role_title", "plan"))
    out.mkdir(parents=True, exist_ok=True)
    plan_path = out / "plan.json"
    plan_path.write_text(json.dumps(plan, indent=2, ensure_ascii=False), encoding="utf-8")
    summary = render_all(plan, out)
    print(f"✓ {plan_path}")
    print(f"✓ dashboard.html + vault/ — {summary['sprints']} sprints, {summary['pages']} engineering pages")
    print(f"Output: {summary['out']}")
    return 0


def cmd_render(args: argparse.Namespace) -> int:
    from lambda_core.render import render_all
    from lambda_core.validate import ValidationError, validate_plan

    plan_path = Path(args.plan)
    plan = json.loads(plan_path.read_text(encoding="utf-8"))
    try:
        validate_plan(plan)
    except ValidationError as err:
        print(f"plan.json failed validation:\n{err}", file=sys.stderr)
        return 1
    out = Path(args.out) if args.out else plan_path.parent / f"{plan_path.stem}_rendered"
    summary = render_all(plan, out)
    print(f"✓ dashboard.html + vault/ — {summary['sprints']} sprints, {summary['pages']} engineering pages")
    print(f"Output: {summary['out']}")
    return 0


def main(argv: list[str] | None = None) -> int:
    load_dotenv(ROOT / ".env")
    args = build_parser().parse_args(argv)
    if args.command == "generate":
        return cmd_generate(args)
    return cmd_render(args)


if __name__ == "__main__":
    raise SystemExit(main())
