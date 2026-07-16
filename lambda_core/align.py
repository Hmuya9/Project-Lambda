"""Deterministic structural alignment for Role-to-Roadmap payloads.

Uses investigation_roadmap as the source of truth so tracks, growth model,
and proof ladder cannot drift out of sync after generation.
Applies minimal JD-anchored patches (e.g. explicit BMC/Redfish when required).
"""

from __future__ import annotations

from typing import Any

_CAUSAL_WORDS = (
    "because",
    "depends",
    "layer",
    "failure",
    "assumption",
    "runtime",
    "dependency",
    "environment",
    "signal",
    "state",
)
_CAUSAL_PATCH = (
    " This depends on layered runtime and environment assumptions; "
    "failure happens because a signal or state at one layer is wrong."
)
_VISUAL_MARKERS = (
    "->",
    "→",
    "layer",
    "flow",
    "pipeline",
    "state",
    "diagram",
    "sketch",
    "arrow",
    "boxes",
)
_VISUAL_PATCH = (
    " Sketch boxes and arrows: input -> processing layer -> output; "
    "mark failure states."
)

_HARDWARE_JD_SIGNALS = (
    "redfish",
    "bmc",
    "ipmi",
    "firmware-level",
    "firmware level",
    "firmware telemetry",
    "bare metal",
    "hardware lifecycle",
)


def _lower(text: str | None) -> str:
    return (text or "").lower()


def _jd_needs_hardware_tooling(jd: str) -> bool:
    return any(s in _lower(jd) for s in _HARDWARE_JD_SIGNALS)


def _roadmap_names_hardware_tooling(investigations: list[Any]) -> bool:
    blob = _lower(
        " ".join(
            str(inv.get(k) or "")
            for inv in investigations
            if isinstance(inv, dict)
            for k in (
                "title",
                "engineering_question",
                "subquestions",
                "concepts_and_vocabulary",
                "build_or_modify",
            )
        )
    )
    return any(t in blob for t in ("redfish", "bmc", "ipmi"))


def _bmc_redfish_investigation() -> dict[str, Any]:
    return {
        "title": "How do BMC/Redfish-style interfaces expose hardware state?",
        "track": "role_specific",
        "expensive_problem": (
            "Without firmware-level telemetry, fleet health tooling guesses instead of measuring."
        ),
        "engineering_question": (
            "How do BMC/Redfish-style interfaces expose hardware state for repair and health automation?"
        ),
        "why_matters_for_role": (
            "Repair automation and fleet health depend on a reliable low-level access layer."
        ),
        "phase_0_mental_model": (
            "BMC/Redfish interfaces expose hardware state because firmware and board "
            "controllers sit below the OS. Health tooling depends on this layer for "
            "sensors, logs, and power/reset actions. Failure happens when telemetry is "
            "stale or incomplete — the runtime view looks healthy while the hardware "
            "signal says otherwise. Assumptions about IPMI/Redfish reachability and "
            "auth become part of the environment contract for fleet automation."
        ),
        "visual_system_model": (
            "GPU/host sensors -> BMC/Redfish interface -> telemetry collector -> "
            "health view / repair state machine. Mark auth, freshness, and missing-signal "
            "failure points with arrows."
        ),
        "subquestions": [
            "What state does Redfish expose that OS metrics miss?",
            "How do we mock BMC/Redfish without real hardware?",
            "What fails when telemetry freshness drops?",
        ],
        "concepts_and_vocabulary": [
            "BMC",
            "Redfish",
            "IPMI",
            "firmware telemetry",
            "sensor freshness",
        ],
        "engineering_principles": [
            "Prefer real signals over vibes",
            "Fail closed when telemetry is stale",
        ],
        "technologies_involved": [
            {
                "technology": "Mocked Redfish/BMC API",
                "engineering_pain_it_solves": (
                    "Hardware health cannot be inferred from application metrics alone "
                    "because firmware-level failures live below the OS runtime."
                ),
            }
        ],
        "observe_first": "Inspect a mocked Redfish inventory/sensors payload and map fields to health decisions.",
        "build_or_modify": (
            "Add src/redfish_interface.py that reads mocked BMC/Redfish state and "
            "emits normalized hardware health signals."
        ),
        "intentionally_break_debug": "Inject stale sensors, auth failure, and missing Redfish endpoints.",
        "improve": "Add freshness checks and explicit escalation when BMC signals conflict.",
        "github_evidence": "src/redfish_interface.py + mocked fixtures + failure notes",
        "obsidian_engineering_page": "BMC/Redfish hardware state mental model",
        "two_minute_explanation_target": (
            "Explain why fleet repair needs BMC/Redfish-style interfaces, even when mocked."
        ),
        "exit_criteria": [
            "Can explain BMC/Redfish role in hardware state",
            "Has mocked interface artifact",
            "Can show a stale-telemetry failure mode",
        ],
        "builds_on_prior_artifact": "prior cumulative modules",
        "artifact_this_investigation_produces": "src/redfish_interface.py",
        "module_or_folder_added": "src/redfish_interface.py",
        "delta_from_previous_investigation": (
            "Adds explicit BMC/Redfish-style hardware state access to the same repo."
        ),
        "capstone_delta": "n/a — not the capstone",
    }


def align_roadmap_structure(
    data: dict[str, Any],
    job_description: str | None = None,
) -> dict[str, Any]:
    """Align tracks / growth / ladder to investigation_roadmap in-place."""
    investigations = data.get("investigation_roadmap")
    if not isinstance(investigations, list) or not investigations:
        return data

    jd = job_description or ""
    if _jd_needs_hardware_tooling(jd) and not _roadmap_names_hardware_tooling(investigations):
        # Insert explicit BMC/Redfish investigation before final capstone.
        insert_at = len(investigations)
        for i, inv in enumerate(investigations):
            if isinstance(inv, dict) and "capstone" in str(inv.get("title") or "").lower():
                insert_at = i
                break
        investigations = (
            list(investigations[:insert_at])
            + [_bmc_redfish_investigation()]
            + list(investigations[insert_at:])
        )
        data["investigation_roadmap"] = investigations

    # Keep at most one Capstone-titled investigation and force it last.
    non_caps: list[Any] = []
    caps: list[Any] = []
    for inv in investigations:
        if not isinstance(inv, dict):
            continue
        if "capstone" in str(inv.get("title") or "").lower():
            caps.append(inv)
        else:
            non_caps.append(inv)
    if caps:
        investigations = non_caps + [caps[-1]]
        data["investigation_roadmap"] = investigations

    for inv in investigations:
        if not isinstance(inv, dict):
            continue
        mm = str(inv.get("phase_0_mental_model") or "")
        hits = sum(1 for w in _CAUSAL_WORDS if w in mm.lower())
        if hits < 2:
            inv["phase_0_mental_model"] = (mm.rstrip() + _CAUSAL_PATCH).strip()
        visual = str(inv.get("visual_system_model") or "")
        if len(visual.strip()) >= 40 and not any(s in visual.lower() for s in _VISUAL_MARKERS):
            inv["visual_system_model"] = (visual.rstrip() + _VISUAL_PATCH).strip()

    titles = [
        str(inv.get("title") or "").strip()
        for inv in investigations
        if isinstance(inv, dict)
    ]
    for mm in data.get("missing_mental_models") or []:
        if not isinstance(mm, dict):
            continue
        pointer = str(mm.get("first_investigation_that_builds_it") or "").strip()
        if pointer and any(pointer.lower() == t.lower() for t in titles):
            continue
        model_l = str(mm.get("mental_model") or "").lower()
        if any(k in model_l for k in ("observ", "metric", "alert", "health", "monitor")):
            for t in titles:
                tl = t.lower()
                if any(k in tl for k in ("health", "metric", "alert", "observ")):
                    mm["first_investigation_that_builds_it"] = t
                    break
        elif pointer:
            for t in titles:
                if pointer.lower() in t.lower() or t.lower() in pointer.lower():
                    mm["first_investigation_that_builds_it"] = t
                    break

    # Patch obviously non-measurable proposed metric wording toward project proxies.
    for item in data.get("operational_metrics_contract") or []:
        if not isinstance(item, dict):
            continue
        metric = str(item.get("metric") or "")
        how = str(item.get("how_to_measure_in_the_project") or "")
        low = (metric + " " + how).lower()
        if "incident resolution" in low and "mttr" not in low:
            item["metric"] = "MTTR / incident resolution time (simulated)"
            item["how_to_measure_in_the_project"] = (
                how
                + " Measure inject→detect→resolve timestamps in the cumulative lab logs."
            )

    generals = [
        str(inv.get("title") or "").strip()
        for inv in investigations
        if isinstance(inv, dict) and str(inv.get("track", "")).lower() == "general"
    ]
    roles = [
        str(inv.get("title") or "").strip()
        for inv in investigations
        if isinstance(inv, dict) and str(inv.get("track", "")).lower() == "role_specific"
    ]
    tracks = data.get("roadmap_tracks")
    if not isinstance(tracks, dict):
        tracks = {}
        data["roadmap_tracks"] = tracks
    tracks["general_engineering_track"] = [t for t in generals if t]
    tracks["role_specific_track"] = [t for t in roles if t]

    cumulative = data.get("cumulative_system")
    if not isinstance(cumulative, dict):
        cumulative = {}
        data["cumulative_system"] = cumulative
    system_name = str(cumulative.get("system_name") or "").strip() or "cumulative-lab"

    growth: list[dict[str, Any]] = []
    for i, inv in enumerate(investigations):
        if not isinstance(inv, dict):
            continue
        title = str(inv.get("title") or "").strip() or f"Investigation {i + 1}"
        module = str(inv.get("module_or_folder_added") or "").strip() or f"src/inv_{i + 1}/"
        growth.append(
            {
                "investigation_number": i + 1,
                "investigation_title": title,
                "folder_or_module_added": module,
                "capability_added": str(
                    inv.get("artifact_this_investigation_produces") or title
                ),
                "why_it_matters": str(inv.get("why_matters_for_role") or "Cumulative growth."),
                "evidence_created": str(inv.get("github_evidence") or "artifact"),
            }
        )
    cumulative["repo_growth_model"] = growth

    ladder: list[dict[str, Any]] = []
    for i, inv in enumerate(investigations):
        if not isinstance(inv, dict):
            continue
        title = str(inv.get("title") or "").strip() or f"Investigation {i + 1}"
        module = str(inv.get("module_or_folder_added") or "").strip() or f"src/inv_{i + 1}/"
        ladder.append(
            {
                "level": i + 1,
                "title": title,
                "same_system_name": system_name,
                "module_or_folder_added": module,
                "extends_previous": (
                    "none — starting level"
                    if i == 0
                    else f"Extends prior level of {system_name}."
                ),
                "new_capability_added": str(
                    inv.get("artifact_this_investigation_produces") or title
                ),
                "what_new_proof_it_creates": str(
                    inv.get("delta_from_previous_investigation")
                    or inv.get("github_evidence")
                    or "New evidence in the same repo."
                ),
                "why_this_is_not_a_separate_project": (
                    f"Same cumulative system ({system_name}); only a new module/folder."
                ),
                "evidence": [
                    str(inv.get("github_evidence") or "repo evidence"),
                    module,
                ],
                "connected_investigations": [title],
            }
        )
    data["proof_of_work_ladder"] = ladder
    return data
