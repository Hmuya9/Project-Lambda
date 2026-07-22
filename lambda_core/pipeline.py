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
    pitch_prompt,
    plan_prompt,
)
from lambda_core.validate import ValidationError, validate_plan

GAP_WEIGHT = {"full": 3, "partial": 2, "none": 1}
INTENTS = ("targeted", "directional", "exploratory")
_PID = re.compile(r"^P\d+$")

EVIDENCE_TYPES = {
    "repo", "benchmark", "postmortem", "diagram", "demo",
    "failure-mode-table", "verification-log", "readme", "writeup",
}
# Keyword → canonical type, checked in order. The model may phrase evidence
# types freely ("verification log", "incident report", "FMEA table") — we
# normalize in code instead of bouncing schema errors off the model.
_EVIDENCE_SYNONYMS = (
    ("bench", "benchmark"),
    ("postmortem", "postmortem"),
    ("incident", "postmortem"),
    ("fmea", "failure-mode-table"),
    ("failure", "failure-mode-table"),
    ("table", "failure-mode-table"),
    ("verif", "verification-log"),
    ("log", "verification-log"),
    ("diagram", "diagram"),
    ("sketch", "diagram"),
    ("architecture", "diagram"),
    ("demo", "demo"),
    ("video", "demo"),
    ("readme", "readme"),
    ("repo", "repo"),
    ("code", "repo"),
    ("project", "repo"),
)


def _normalize_evidence_type(value: Any) -> str:
    slug = re.sub(r"[^a-z]+", "-", str(value or "").lower()).strip("-")
    if slug in EVIDENCE_TYPES:
        return slug
    for key, canon in _EVIDENCE_SYNONYMS:
        if key in slug:
            return canon
    return "writeup"


def normalize_sprints(sprints: list[Any]) -> list[dict[str, Any]]:
    """Guarantee sprint structure the schema demands; never trust model types.

    After this, sprint-level schema failures can only be about SUBSTANCE
    (e.g. a thin done_when) — which the repair pass can meaningfully fix.
    """
    out: list[dict[str, Any]] = []
    for i, s in enumerate(sprints, 1):
        if not isinstance(s, dict):
            continue
        s["week"] = _int(s.get("week"), i, 1, 52)
        primary = s.get("primary") if isinstance(s.get("primary"), dict) else {}
        primary["id"] = str(primary.get("id", "")) or "P0"
        primary["question"] = str(primary.get("question", ""))
        s["primary"] = primary
        ev = s.get("evidence") if isinstance(s.get("evidence"), dict) else {}
        ev["artifact"] = str(ev.get("artifact", ""))
        ev["type"] = _normalize_evidence_type(ev.get("type"))
        ev["done_when"] = str(ev.get("done_when", ""))
        s["evidence"] = ev
        for key in ("secondary", "stretch", "interview"):
            value = s.get(key)
            s[key] = [str(x) for x in value] if isinstance(value, list) else []
        if "watch" in s:
            watch = s.get("watch")
            s["watch"] = [w for w in watch if isinstance(w, dict) and w.get("query")] if isinstance(watch, list) else []
            for w in s["watch"]:
                w["title"] = str(w.get("title", "video"))
                w["query"] = str(w.get("query", ""))
                if w.get("source") not in ("youtube", "mit-ocw"):
                    w["source"] = "youtube"
        out.append(s)
    return out


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


def _problem_key(text: Any) -> str:
    """Loose text key for detecting the same problem under light rewording."""
    return re.sub(r"[^a-z0-9 ]+", "", str(text).lower()).strip()


def assign_ids(
    mappings: list[dict[str, Any]],
    start_counter: int,
    existing: list[Any] | None = None,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], dict[str, str]]:
    """Resolve mapping-stage output into final backlog IDs.

    Returns (mapped, new_entries, id_by_problem) where id_by_problem keys the
    ORIGINAL decoded problem wording to its final ID (never the literal "NEW").
    Non-dict entries are skipped; a malformed/blank backlog_id is treated as NEW.

    Dedup guarantees:
    - a NEW problem whose text already matches an existing backlog entry gets
      the EXISTING id (the model failed to match; we match for it),
    - two NEW mappings with the same problem text share ONE new id,
    - no duplicate (id, problem) pair in the mapped output.
    """
    existing_by_key = {
        _problem_key(p.problem): p.id for p in (existing or []) if hasattr(p, "id")
    }
    assigned_new: dict[str, str] = {}
    seen_ids: set[str] = set()
    mapped: list[dict[str, Any]] = []
    new_entries: list[dict[str, Any]] = []
    id_by_problem: dict[str, str] = {}
    counter = start_counter
    for m in mappings:
        if not isinstance(m, dict):
            continue
        problem_text = str(m.get("backlog_problem") or m.get("problem", ""))
        key = _problem_key(problem_text)
        backlog_id = str(m.get("backlog_id", "")).strip()
        if not _PID.match(backlog_id):
            if key in existing_by_key:
                backlog_id = existing_by_key[key]  # model said NEW; text says match
            elif key in assigned_new:
                backlog_id = assigned_new[key]  # same NEW problem twice → one id
            else:
                backlog_id = f"P{counter}"
                counter += 1
                assigned_new[key] = backlog_id
                new_entries.append(
                    {
                        "id": backlog_id,
                        "problem": problem_text,
                        "domain": str(m.get("domain") or "Added from targeted runs"),
                    }
                )
        id_by_problem[str(m.get("problem", ""))] = backlog_id
        if backlog_id not in seen_ids:
            seen_ids.add(backlog_id)
            mapped.append({"id": backlog_id, "problem": problem_text})
    return mapped, new_entries, id_by_problem


def normalize_gap_map(
    gap_map: list[dict[str, Any]], mapped: list[dict[str, Any]]
) -> list[dict[str, Any]]:
    """Guarantee every gap-map entry satisfies the plan schema.

    Fills missing id/problem from the mapped list by position, defaults every
    schema-required field, drops non-dict entries, and drops DUPLICATE ids —
    each problem appears exactly once. After this, gap_map can never be the
    source of a final-validation failure.
    """
    out: list[dict[str, Any]] = []
    seen: set[str] = set()
    for i, g in enumerate(gap_map):
        if not isinstance(g, dict):
            continue
        fallback = mapped[i] if i < len(mapped) else {}
        pid = str(g.get("id", "")).strip()
        if not _PID.match(pid):
            pid = str(fallback.get("id", "P0")) or "P0"
        if pid in seen:
            continue
        seen.add(pid)
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


def run_discovery(
    source_text: str,
    profile: str,
    *,
    intent: str = "targeted",
    update_backlog: bool = True,
) -> dict[str, Any]:
    """Phase 1: decode → map → intersect → rank → project pitches.

    Returns a discovery dict the UI can show for the PROJECT PICK moment,
    then pass to run_plan() with the chosen project.
    """
    if intent not in INTENTS:
        raise ValueError(f"intent must be one of {INTENTS}, got {intent!r}")
    if not source_text.strip():
        raise ValueError("No job description / market composite provided (intake gate).")
    if not profile.strip():
        raise ValueError(
            "No engineer profile provided (intake gate). Nothing is tailored without a profile."
        )

    problems = backlog_mod.load_backlog()

    _log("[1/5] Decoding what the market pays for...")
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

    _log("[2/5] Mapping onto the domain backlog...")
    mapping = _stage(
        map_prompt(decoded_problems, backlog_mod.as_prompt_block(problems)),
        ("mappings",),
        "map",
    )

    # Assign real IDs to NEW problems; optionally grow the backlog (never mutate).
    mapped, new_entries, id_by_problem = assign_ids(
        mapping.get("mappings", []), backlog_mod.next_id(problems), problems
    )
    if not mapped:
        raise RuntimeError(
            "The map stage returned no usable mappings after a retry. "
            "Run again, or switch models via .env."
        )
    if update_backlog and new_entries:
        appended = backlog_mod.append_entries(new_entries)
        _log(f"      backlog grew: {', '.join(appended) or '(duplicates skipped)'}")

    _log("[3/5] Intersecting with the profile...")
    intersect = _stage(intersect_prompt(mapped, profile), ("gap_map",), "intersect")
    gap_map = rank(normalize_gap_map(intersect.get("gap_map", []), mapped))
    if not gap_map:
        raise RuntimeError(
            "The intersect stage returned an empty gap map after a retry. "
            "Run again, or switch models via .env."
        )

    _log("[4/5] Pitching projects that sit you close to the expensive problems...")
    pitch = _stage(
        pitch_prompt(gap_map, profile, decode), ("project_options",), "pitch"
    )
    project_options = [
        p for p in pitch.get("project_options", []) if isinstance(p, dict)
    ]
    recommended = _int(pitch.get("recommended", 0), 0, 0, max(0, len(project_options) - 1))

    # Attach decoded problem metadata with final IDs (wording match, then order).
    expensive_problems = []
    for i, p in enumerate(decoded_problems):
        pid = id_by_problem.get(str(p.get("problem", "")), "")
        if not pid and i < len(mapped):
            pid = mapped[i]["id"]
        expensive_problems.append({**p, "id": pid or "P0"})

    return {
        "intent": intent,
        "decode": decode,
        "expensive_problems": expensive_problems,
        "mapped": mapped,
        "new_entries": new_entries,
        "gap_map": gap_map,
        "project_options": project_options,
        "recommended": recommended,
    }


def run_plan(
    discovery: dict[str, Any],
    profile: str,
    *,
    project: dict[str, Any] | None = None,
    weeks: int = 8,
) -> dict[str, Any]:
    """Phase 2: build the sprint plan around the chosen project; validate."""
    weeks = _int(weeks, 8, 4, 12)
    decode = discovery["decode"]
    gap_map = discovery["gap_map"]
    intent = discovery.get("intent", "targeted")
    if project is None and discovery.get("project_options"):
        project = discovery["project_options"][discovery.get("recommended", 0)]

    _log("[5/5] Planning sprints + positioning around your project...")
    plan_part = _stage(
        plan_prompt(gap_map, profile, decode, weeks, project=project),
        ("positioning", "sprints"),
        "plan",
        max_tokens=16384,
    )

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
            "human_hook": decode.get("human_hook") or {},
            "expensive_problems": discovery["expensive_problems"],
            "hard_requirements": decode.get("hard_requirements") or [],
            "wishlist": decode.get("wishlist") or [],
            "seniority_signal": str(decode.get("seniority_signal", "")),
        },
        "project": project or {},
        "project_options": discovery.get("project_options", []),
        "gap_map": gap_map,
        "positioning": plan_part["positioning"],
        "sprints": normalize_sprints(plan_part["sprints"]),
        "new_backlog_entries": discovery.get("new_entries", []),
    }

    try:
        validate_plan(plan)
    except ValidationError as err:
        # One focused repair pass. Because gap_map/meta/role_decode are
        # normalized in code, remaining failures can only involve the plan
        # stage's output (positioning/sprints) — the one part re-generated here.
        _log(f"      plan failed validation, repairing:\n{err}")
        plan_part = _stage(
            plan_prompt(gap_map, profile, decode, weeks, project=project)
            + "\n\nYour previous output failed these checks — fix them exactly:\n"
            + str(err),
            ("positioning", "sprints"),
            "plan-repair",
            max_tokens=16384,
        )
        plan["positioning"] = plan_part["positioning"]
        plan["sprints"] = normalize_sprints(plan_part["sprints"])
        validate_plan(plan)

    return plan


def run_pipeline(
    source_text: str,
    profile: str,
    *,
    intent: str = "targeted",
    weeks: int = 8,
    update_backlog: bool = True,
    project_index: int | None = None,
) -> dict[str, Any]:
    """Full pipeline in one call: discovery, then the plan.

    project_index picks a pitched project; None takes the recommended one.
    """
    discovery = run_discovery(
        source_text, profile, intent=intent, update_backlog=update_backlog
    )
    options = discovery.get("project_options", [])
    project = None
    if options:
        idx = discovery.get("recommended", 0)
        if project_index is not None:
            idx = _int(project_index, idx, 0, len(options) - 1)
        project = options[idx]
    return run_plan(discovery, profile, project=project, weeks=weeks)
