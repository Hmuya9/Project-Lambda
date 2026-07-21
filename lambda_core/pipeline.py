"""The Lambda pipeline: intake → decode → map → intersect → rank → plan.

Staged reasoning with a small contract per stage. Ranking is code, not LLM:
priority = importance × gap severity, ordered by backlog dependency (lower IDs
are foundations by construction of the backlog).
"""

from __future__ import annotations

import datetime
import sys
from typing import Any

from lambda_core import backlog as backlog_mod
from lambda_core.llm import complete_json
from lambda_core.prompts import (
    SYSTEM,
    decode_prompt,
    intersect_prompt,
    map_prompt,
    plan_prompt,
)
from lambda_core.validate import ValidationError, validate_plan

GAP_WEIGHT = {"full": 3, "partial": 2, "none": 1}
INTENTS = ("targeted", "directional", "exploratory")


def _log(msg: str) -> None:
    print(msg, file=sys.stderr)


def rank(gap_map: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Deterministic ranking: score desc, then backlog ID asc (foundations first)."""

    def pid_num(item: dict[str, Any]) -> int:
        try:
            return int(str(item.get("id", "P999"))[1:])
        except ValueError:
            return 999

    def score(item: dict[str, Any]) -> int:
        importance = int(item.get("importance", 3))
        return importance * GAP_WEIGHT.get(item.get("gap", "partial"), 2)

    ordered = sorted(gap_map, key=lambda g: (-score(g), pid_num(g)))
    for i, item in enumerate(ordered, 1):
        item["priority"] = i
    return ordered


def run_pipeline(
    source_text: str,
    profile: str,
    *,
    intent: str = "targeted",
    weeks: int = 8,
    update_backlog: bool = True,
) -> dict[str, Any]:
    """Run the full pipeline and return a validated plan dict."""
    if intent not in INTENTS:
        raise ValueError(f"intent must be one of {INTENTS}, got {intent!r}")
    if not source_text.strip():
        raise ValueError("No job description / market composite provided (intake gate).")
    if not profile.strip():
        raise ValueError("No engineer profile provided (intake gate). Nothing is tailored without a profile.")

    problems = backlog_mod.load_backlog()

    _log("[1/4] Decoding what the market pays for...")
    decode = complete_json(SYSTEM, decode_prompt(source_text, intent))

    _log("[2/4] Mapping onto the domain backlog...")
    mapping = complete_json(
        SYSTEM,
        map_prompt(decode["expensive_problems"], backlog_mod.as_prompt_block(problems)),
    )

    # Assign real IDs to NEW problems; optionally grow the backlog (never mutate).
    new_entries: list[dict[str, Any]] = []
    counter = backlog_mod.next_id(problems)
    mapped: list[dict[str, Any]] = []
    for m in mapping.get("mappings", []):
        backlog_id = str(m.get("backlog_id", "")).strip()
        if backlog_id.upper() == "NEW":
            backlog_id = f"P{counter}"
            counter += 1
            new_entries.append(
                {
                    "id": backlog_id,
                    "problem": m.get("backlog_problem") or m.get("problem", ""),
                    "domain": m.get("domain") or "Added from targeted runs",
                }
            )
        mapped.append(
            {"id": backlog_id, "problem": m.get("backlog_problem") or m.get("problem", "")}
        )
    if update_backlog and new_entries:
        appended = backlog_mod.append_entries(new_entries)
        _log(f"      backlog grew: {', '.join(appended) or '(duplicates skipped)'}")

    _log("[3/4] Intersecting with the profile...")
    intersect = complete_json(SYSTEM, intersect_prompt(mapped, profile))
    gap_map = rank(intersect["gap_map"])

    _log("[4/4] Planning sprints + positioning...")
    plan_part = complete_json(
        SYSTEM, plan_prompt(gap_map, profile, decode, weeks), max_tokens=16384
    )

    # Attach decoded problem metadata with final IDs.
    id_by_problem = {m["problem"]: m["id"] for m in mapping.get("mappings", [])}
    expensive_problems = []
    for p in decode.get("expensive_problems", []):
        pid = id_by_problem.get(p.get("problem", ""), "")
        if pid.upper() == "NEW":  # defensive; should have been assigned above
            pid = ""
        expensive_problems.append({"id": pid or "P0", **p})

    plan: dict[str, Any] = {
        "meta": {
            "mode": intent,
            "role_title": decode.get("role_title", ""),
            "company": decode.get("company", ""),
            "archetype": decode.get("archetype", ""),
            "generated": datetime.date.today().isoformat(),
            "jd_source": "" if intent == "targeted" else f"{intent} composite",
        },
        "role_decode": {
            "summary": decode.get("summary", ""),
            "expensive_problems": expensive_problems,
            "hard_requirements": decode.get("hard_requirements", []),
            "wishlist": decode.get("wishlist", []),
            "seniority_signal": decode.get("seniority_signal", ""),
        },
        "gap_map": gap_map,
        "positioning": plan_part["positioning"],
        "sprints": plan_part["sprints"],
        "new_backlog_entries": new_entries,
    }

    try:
        validate_plan(plan)
    except ValidationError as err:
        # One focused repair pass on the failing stage only (sprints/positioning).
        _log(f"      plan failed validation, repairing:\n{err}")
        plan_part = complete_json(
            SYSTEM,
            plan_prompt(gap_map, profile, decode, weeks)
            + "\n\nYour previous output failed these checks — fix them exactly:\n"
            + str(err),
            max_tokens=16384,
        )
        plan["positioning"] = plan_part["positioning"]
        plan["sprints"] = plan_part["sprints"]
        validate_plan(plan)

    return plan
