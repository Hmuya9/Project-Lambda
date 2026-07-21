"""Slim plan validation: structure via JSON Schema + a few cheap substance checks.

Deliberately small. Substance is the reasoning pipeline's job; this layer only
catches contract violations and the most obvious quality failures. If this file
grows past ~100 lines, something upstream is broken — fix the pipeline, not this.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
SCHEMA_PATH = ROOT / "data" / "plan_schema.json"


class ValidationError(Exception):
    pass


def validate_plan(plan: dict[str, Any]) -> None:
    """Raise ValidationError with all problems found, or return None."""
    import json

    import jsonschema

    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    validator = jsonschema.Draft202012Validator(schema)
    errors = [
        f"{'/'.join(str(p) for p in e.absolute_path) or '<root>'}: {e.message}"
        for e in validator.iter_errors(plan)
    ]

    # Substance floor — cheap, robust, non-negotiable checks only.
    for i, sprint in enumerate(plan.get("sprints", []), 1):
        ev = sprint.get("evidence", {})
        artifact = str(ev.get("artifact", "")).strip()
        done_when = str(ev.get("done_when", "")).strip()
        if len(done_when) < 20:
            errors.append(
                f"sprint {i}: 'done_when' is missing or too thin to satisfy "
                f"a skeptical reviewer: {done_when!r}"
            )
        if artifact.lower().startswith(("learn ", "study ", "read ", "watch ")):
            errors.append(
                f"sprint {i}: artifact is consumption, not evidence: {artifact!r}"
            )
    if not plan.get("positioning", {}).get("do_not_claim"):
        errors.append("positioning: 'do_not_claim' must not be empty — honesty is enforced")

    if errors:
        raise ValidationError("\n".join(errors))
