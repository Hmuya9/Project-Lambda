"""The Lambda pipeline: intake → decode → map → intersect → rank → plan.

Staged reasoning with a small contract per stage. Ranking is code, not LLM:
priority = importance × gap severity, ordered by backlog dependency (lower IDs
are foundations by construction of the backlog).

Robustness principle: every stage's output is checked for its required keys
(with one corrective retry), and everything the final schema demands of
gap_map is normalized in code — so schema-level failures can only come from
the plan stage, which is the one stage the repair pass re-runs.
"""

from __future__ import annotations

import datetime
import re
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
_PID = re.compile(r"^P\d+$")


def _log(msg: str) -> None:
    print(msg, file=sys.stderr)


def _int(value: Any, default: int, lo: int, hi: int) -> int:
    """Coerce model output to an int within [lo, hi]; never raise."""
    try:
        n = int(float(str(value).strip()))
    except (ValueError, TypeError):
        return default
    return max(lo, min(hi, n))


def _stage(
    prompt: str, required: tuple[str, ...], stage: str, *, max_tokens: int = 8192
) -> dict[str, Any]:
    """One stage call. Verifies required keys; one corrective retry; clear error."""
    data = complete_json(SYSTEM, prompt, max_tokens=max_tokens)
    missing = [k for k in required if not isinstance(data, dict) or k not in data]
    if missing:
        data = complete_json(
            SYSTEM,
            prompt
            + "\n\nYour previous JSON was missing required key(s): "
            + ", ".join(missing)
            + ". Return the complete JSON object again with EVERY required key present.",
            max_tokens=max_tokens,
        )
        missing = [k for k in required if not isinstance(data, dict) or k not in data]
        if missing:
            raise RuntimeError(
                f"The {stage} stage returned JSON missing {missing} after a retry. "
                "Run again, or switch models via .env."
            )
    return data


def rank(gap_map: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Deterministic ranking: score desc, then backlog ID asc (foundations first).

    Also normalizes importance (int 1–5) and gap (enum) in place — model output
    is never trusted to be well-typed.
    """

    def pid_num(item: dict[str, Any]) -> int:
        try:
            return int(str(item.get("id", "P999"))[1:])
        except ValueError:
            return 999

    for item in gap_map:
        item["importance"] = _int(item.get("importance"), 3, 1, 5)
        gap = str(item.get("gap", "")).strip().lower()
        item["gap"] = gap if gap in GAP_WEIGHT else "partial"

    def score(item: dict[str, Any]) -> int:
        return item["importance"] * GAP_WEIGHT[item["gap"]]

    ordered = sorted(gap_map, key=lambda g: (-score(g), pid_num(g)))
    for i, item in enumerate(ordered, 1):
        item["priority"] = i
    return ordered


def assign_ids(
    mappings: list[dict[str, Any]], start_counter: int
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], dict[str, str]]:
    """Resolve mapping-stage output into final backlog IDs.

    Returns (mapped, new_entries, id_by_problem) where id_by_problem keys the
    ORIGINAL decoded problem wording to its final ID (never the literal "NEW").
    Non-dict entries are skipped; a malformed/blank backlog_id is treated as NEW.
    """
    mapped: list[dict[str, Any]] = []
    new_entries: list[dict[str, Any]] = []
    id_by_problem: dict[str, str] = {}
    counter = start_counter
    for m in mappings:
        if not isinstance(m, dict):
            continue
        backlog_id = str(m.get("backlog_id", "")).strip()
        if not _PID.match(backlog_id):
            backlog_id = f"P{counter}"
            counter += 1
            new_entries.append(
                {
                    "id": backlog_id,
                    "problem": str(m.get("backlog_problem") or m.get("problem", "")),
                    "domain": str(m.get("domain") or "Added from targeted runs"),
                }
            )
        id_by_problem[str(m.get("problem", ""))] = backlog_id
        mapped.append(
            {
                "id": backlog_id,
                "problem": str(m.get("backlog_problem") or m.get("problem", "")),
            }
        )
    return mapped, new_entries, id_by_problem


def normalize_gap_map(
    gap_map: list[dict[str, Any]], mapped: list[dict[str, Any]]
) -> list[dict[str, Any]]:
    """Guarantee every gap-map entry satisfies the plan schema.

    Fills missing id/problem from the mapped list by position, defaults every
    schema-required field, and drops non-dict entries. After this, gap_map can
    never be the source of a final-validation failure.
    """
    out: list[dict[str, Any]] = []
    for i, g in enumerate(gap_map):
        if not isinstance(g, dict):
            continue
        fallback = mapped[i] if i < len(mapped) else {}
        pid = str(g.get("id", "")).strip()
        if not _PID.match(pid):
            pid = str(fallback.get("id", "P0")) or "P0"
        out.append(
            {
                "id": pid,
                "problem": str(g.get("problem") or fallback.get("problem", "")),
                "importance": g.get("importance", 3),
                "transfer": str(g.get("transfer", "")),
                "gap": g.get("gap", "partial"),
                "credibility_risk": str(g.get("credibility_risk", "")),
                "priority": 0,  # set by rank()
            }
        )
    return out


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
        raise ValueError(
            "No engineer profile provided (intake gate). Nothing is tailored without a profile."
        )
    weeks = _int(weeks, 8, 4, 12)

    problems = backlog_mod.load_backlog()

    _log("[1/4] Decoding what the market pays for...")
    decode = _stage(
        decode_prompt(source_text, intent), ("summary", "expensive_problems"), "decode"
    )
    decoded_problems = [
        p for p in decode.get("expensive_problems", []) if isinstance(p, dict)
    ]
    if not decoded_problems:
        raise RuntimeError(
            "The decode stage produced no expensive problems — the input may not "
            "be a job description or market composite. Check what was pasted."
        )

    _log("[2/4] Mapping onto the domain backlog...")
    mapping = _stage(
        map_prompt(decoded_problems, backlog_mod.as_prompt_block(problems)),
        ("mappings",),
        "map",
    )

    # Assign real IDs to NEW problems; optionally grow the backlog (never mutate).
    mapped, new_entries, id_by_problem = assign_ids(
        mapping.get("mappings", []), backlog_mod.next_id(problems)
    )
    if not mapped:
        raise RuntimeError(
            "The map stage returned no usable mappings after a retry. "
            "Run again, or switch models via .env."
        )
    if update_backlog and new_entries:
        appended = backlog_mod.append_entries(new_entries)
        _log(f"      backlog grew: {', '.join(appended) or '(duplicates skipped)'}")

    _log("[3/4] Intersecting with the profile...")
    intersect = _stage(intersect_prompt(mapped, profile), ("gap_map",), "intersect")
    gap_map = rank(normalize_gap_map(intersect.get("gap_map", []), mapped))
    if not gap_map:
        raise RuntimeError(
            "The intersect stage returned an empty gap map after a retry. "
            "Run again, or switch models via .env."
        )

    _log("[4/4] Planning sprints + positioning...")
    plan_part = _stage(
        plan_prompt(gap_map, profile, decode, weeks),
        ("positioning", "sprints"),
        "plan",
        max_tokens=16384,
    )

    # Attach decoded problem metadata with final IDs (wording match, then order).
    expensive_problems = []
    for i, p in enumerate(decoded_problems):
        pid = id_by_problem.get(str(p.get("problem", "")), "")
        if not pid and i < len(mapped):
            pid = mapped[i]["id"]
        expensive_problems.append({**p, "id": pid or "P0"})

    plan: dict[str, Any] = {
        "meta": {
            "mode": intent,
            "role_title": str(decode.get("role_title", "")) or "Untitled role",
            "company": str(decode.get("company", "")),
            "archetype": str(decode.get("archetype", "")),
            "generated": datetime.date.today().isoformat(),
            "jd_source": str(decode.get("jd_source", ""))
            if intent == "targeted"
            else f"{intent} composite",
        },
        "role_decode": {
            "summary": str(decode.get("summary", "")),
            "expensive_problems": expensive_problems,
            "hard_requirements": decode.get("hard_requirements") or [],
            "wishlist": decode.get("wishlist") or [],
            "seniority_signal": str(decode.get("seniority_signal", "")),
        },
        "gap_map": gap_map,
        "positioning": plan_part["positioning"],
        "sprints": plan_part["sprints"],
        "new_backlog_entries": new_entries,
    }

    try:
        validate_plan(plan)
    except ValidationError as err:
        # One focused repair pass. Because gap_map/meta/role_decode are
        # normalized in code, remaining failures can only involve the plan
        # stage's output (positioning/sprints) — the one part re-generated here.
        _log(f"      plan failed validation, repairing:\n{err}")
        plan_part = _stage(
            plan_prompt(gap_map, profile, decode, weeks)
            + "\n\nYour previous output failed these checks — fix them exactly:\n"
            + str(err),
            ("positioning", "sprints"),
            "plan-repair",
            max_tokens=16384,
        )
        plan["positioning"] = plan_part["positioning"]
        plan["sprints"] = plan_part["sprints"]
        validate_plan(plan)

    return plan
