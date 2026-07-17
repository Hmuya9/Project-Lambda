"""Deterministic structural alignment for Role-to-Roadmap payloads.

Uses investigation_roadmap as the source of truth so tracks, growth model,
and proof ladder cannot drift out of sync after generation.
Applies minimal JD-anchored patches (e.g. explicit BMC/Redfish when required).
"""

from __future__ import annotations

import re
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


def _exact_title(pointer: str, titles: list[str]) -> str | None:
    """Return the exact title string if pointer already matches (case-sensitive or ci)."""
    p = pointer.strip()
    if not p:
        return None
    for t in titles:
        if p == t:
            return t
    for t in titles:
        if p.lower() == t.lower():
            return t
    return None


def _first_title_matching(titles: list[str], *keyword_groups: tuple[str, ...]) -> str | None:
    """Return first investigation title whose lowercased text contains any keyword."""
    for group in keyword_groups:
        for t in titles:
            tl = t.lower()
            if any(k in tl for k in group):
                return t
    return None


def _map_missing_mental_model_pointer(
    pointer: str,
    mental_model: str,
    titles: list[str],
) -> str | None:
    """Map a concept/slogan pointer to the most relevant exact investigation title.

    Returns None when no deterministic mapping exists (validator will reject).
    """
    exact = _exact_title(pointer, titles)
    if exact is not None:
        return exact

    blob = _lower(pointer + " " + mental_model)
    if not blob or not titles:
        return None

    # Ordered from more specific → more general. First match wins.
    rules: list[tuple[tuple[str, ...], tuple[str, ...]]] = [
        # (keywords in pointer/model, keywords required in investigation title)
        (
            ("bmc", "redfish", "ipmi", "firmware", "hardware state", "hardware telemetry"),
            ("bmc", "redfish", "ipmi", "telemetry", "hardware state", "hardware"),
        ),
        (
            (
                "repair",
                "pipeline",
                "return to service",
                "return-to-service",
                "rma",
                "triage",
                "procedure",
                "state machine",
            ),
            # Do NOT use bare "pipeline" — it false-matches "metrics pipeline".
            ("repair", "rma", "state machine", "return to service", "return-to-service", "triage", "workflow"),
        ),
        (
            (
                "inference",
                "model serving",
                "model become a service",
                "batching",
                "p50",
                "p95",
                "p99",
                "token throughput",
                "cold start",
            ),
            (
                "inference",
                "serving",
                "batching",
                "p50",
                "p95",
                "p99",
                "latency",
                "throughput",
                "model become",
                "ai model",
            ),
        ),
        (
            ("robot", "sensor", "actuator", "control loop", "simulation", "kinematics"),
            ("robot", "sensor", "actuator", "control", "simulation"),
        ),
        (
            ("docker", "container", "containerization"),
            ("docker", "container"),
        ),
        (
            ("metric", "alert", "observability", "monitoring", "observ"),
            ("metric", "alert", "observ", "monitor"),
        ),
        (
            ("health", "liveness", "readiness"),
            ("health", "liveness", "readiness"),
        ),
        (
            ("api", "service communication", "expose api", "expose apis", "http"),
            ("api", "apis"),
        ),
        (
            ("config", "automation", "logging", "failure mode", "python automation"),
            ("automation", "config", "log", "python"),
        ),
        (
            (
                "portability",
                "environment",
                "dependency",
                "dependencies",
                "between machines",
                "another machine",
                "machine-report",
                "machine report",
            ),
            ("portability", "machine", "environment", "between machines", "another machine"),
        ),
        (
            ("capstone", "verification", "incident", "postmortem"),
            ("capstone", "verification", "incident", "postmortem"),
        ),
    ]

    for pointer_keys, title_keys in rules:
        if any(k in blob for k in pointer_keys):
            hit = _first_title_matching(titles, title_keys)
            # Observability phrases may only have a health-check investigation.
            if (
                hit is None
                and any(k in pointer_keys for k in ("observability", "metric", "alert", "observ"))
            ):
                hit = _first_title_matching(titles, ("health", "liveness", "readiness"))
            if hit:
                return hit

    # Last resort: token overlap with investigation titles (min 2 meaningful tokens).
    stop = {
        "how", "why", "does", "do", "the", "and", "for", "with", "into", "not",
        "a", "an", "to", "of", "in", "on", "is", "are", "be", "that", "this",
    }
    tokens = [
        w
        for w in re.findall(r"[a-z0-9]+", blob)
        if len(w) > 3 and w not in stop
    ]
    best: str | None = None
    best_score = 0
    for t in titles:
        tl = t.lower()
        score = sum(1 for tok in tokens if tok in tl)
        if score > best_score:
            best_score = score
            best = t
    if best is not None and best_score >= 2:
        return best
    return None


def _align_missing_mental_model_pointers(
    data: dict[str, Any],
    titles: list[str],
) -> None:
    """Rewrite first_investigation_that_builds_it to exact investigation titles."""
    for mm in data.get("missing_mental_models") or []:
        if not isinstance(mm, dict):
            continue
        pointer = str(mm.get("first_investigation_that_builds_it") or "").strip()
        model = str(mm.get("mental_model") or "").strip()
        mapped = _map_missing_mental_model_pointer(pointer, model, titles)
        if mapped is not None:
            mm["first_investigation_that_builds_it"] = mapped


_ROLE_SPECIFIC_TITLE_TERMS = (
    "redfish",
    "bmc",
    "ipmi",
    "gpu repair",
    "fleet repair",
    "repair pipeline",
    "hardware telemetry",
    "gpu qualification",
    "repair workflow",
    "repair process",
)


def _force_role_specific_tracks(investigations: list[Any]) -> None:
    """Flip mislabeled general investigations that are clearly role-specific."""
    for inv in investigations:
        if not isinstance(inv, dict):
            continue
        title_l = _lower(str(inv.get("title") or ""))
        if any(t in title_l for t in _ROLE_SPECIFIC_TITLE_TERMS):
            inv["track"] = "role_specific"


def _ensure_first_prompt_sections(data: dict[str, Any]) -> None:
    """Ensure paste-ready prompt contains required section keywords."""
    first = data.get("first_investigation_prompt")
    if not isinstance(first, dict):
        return
    ready = str(first.get("ready_to_paste_prompt") or "")
    ready_l = ready.lower()
    patches: list[str] = []
    required = (
        ("phase 0", "#### Phase 0\n"),
        ("mental model", "#### Mental model\n"),
        ("observe", "#### Observe\n"),
        ("build", "#### Build\n"),
        ("break", "#### Break\n"),
        ("improve", "#### Improve\n"),
        ("github", "#### GitHub evidence\n"),
        ("obsidian", "#### Obsidian\n"),
    )
    for key, heading in required:
        if key not in ready_l:
            patches.append(heading)
    if patches:
        mm = str(first.get("phase_0_mental_model") or "")
        first["ready_to_paste_prompt"] = (
            ready.rstrip()
            + "\n\n"
            + "\n".join(patches)
            + ("\n" + mm if mm and "mental model" in " ".join(patches).lower() else "")
            + "\n"
        )


def _scrub_absolute_automation(data: dict[str, Any]) -> None:
    """Replace absolute automation slogans with boundary-aware framing."""
    replacements = (
        ("fully automated", "common-path automation with escalation"),
        ("fully-automated", "common-path automation with escalation"),
        ("no humans needed", "human escalation for unsafe/ambiguous states"),
        ("complete automation", "bounded automation with fail-closed gates"),
        ("automated everything", "automate the common path with explicit boundaries"),
        ("automate everything", "automate the common path with explicit boundaries"),
    )
    role = data.get("role_interpretation")
    if isinstance(role, dict):
        for key in ("what_success_looks_like", "real_mission", "one_liner"):
            text = str(role.get(key) or "")
            low = text.lower()
            if any(
                a in low
                for a in (
                    "fully automated",
                    "no humans needed",
                    "complete automation",
                    "automated everything",
                )
            ):
                for old, new in replacements:
                    text = re.sub(re.escape(old), new, text, flags=re.I)
                if "escalat" not in text.lower() and "fail-closed" not in text.lower():
                    text = (
                        text.rstrip(".")
                        + ", with escalation and fail-closed gates for unsafe states."
                    )
                role[key] = text


def _ensure_ops_mttd_mttr(data: dict[str, Any]) -> None:
    """Ensure operational metrics and capstone measurements include MTTD/MTTR."""
    metrics = data.get("operational_metrics_contract")
    if not isinstance(metrics, list):
        metrics = []
        data["operational_metrics_contract"] = metrics
    # Drop clearly non-measurable proposed metrics
    cleaned: list[Any] = []
    for m in metrics:
        if not isinstance(m, dict):
            continue
        low = _lower(str(m.get("metric") or "") + " " + str(m.get("how_to_measure_in_the_project") or ""))
        if any(
            bad in low
            for bad in (
                "documentation completeness",
                "user satisfaction",
                "customer satisfaction",
                "revenue",
            )
        ):
            continue
        cleaned.append(m)
    metrics = cleaned
    data["operational_metrics_contract"] = metrics

    blob = _lower(
        " ".join(
            str(m.get("metric") or "") + " " + str(m.get("how_to_measure_in_the_project") or "")
            for m in metrics
            if isinstance(m, dict)
        )
    )
    has_mttd = "mttd" in blob or "mean time to detect" in blob
    has_mttr = (
        "mttr" in blob
        or "mean time to repair" in blob
        or "return to service" in blob
        or "return-to-service" in blob
        or "time to return" in blob
    )
    if not has_mttd:
        metrics.append(
            {
                "metric": "MTTD for simulated service/fleet incidents",
                "source": "proposed_project_target",
                "why_it_matters": "Fast detection protects availability and throughput.",
                "how_to_measure_in_the_project": (
                    "Timestamp fault injection vs first alert/detection in lab logs."
                ),
                "what_bad_result_means": "Blind spots in observability.",
            }
        )
    if not has_mttr:
        metrics.append(
            {
                "metric": "MTTR / return-to-service time for simulated incidents",
                "source": "proposed_project_target",
                "why_it_matters": "Recovery speed is the operational credibility bar.",
                "how_to_measure_in_the_project": (
                    "Timestamp detection vs verified healthy/return-to-service in lab logs."
                ),
                "what_bad_result_means": "Slow or unverified recovery.",
            }
        )

    proof = data.get("capstone_proof_contract")
    if isinstance(proof, dict):
        req = proof.get("required_measurements")
        if not isinstance(req, list):
            req = []
            proof["required_measurements"] = req
        meas_blob = _lower(" ".join(str(x) for x in req))
        if "mttd" not in meas_blob and "mean time to detect" not in meas_blob:
            req.append("Target MTTD for injected faults")
        if (
            "mttr" not in meas_blob
            and "mean time to repair" not in meas_blob
            and "return to service" not in meas_blob
            and "return-to-service" not in meas_blob
        ):
            req.append("Target MTTR / return-to-service time")


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

    _force_role_specific_tracks(investigations)

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
    _align_missing_mental_model_pointers(data, titles)

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
    _ensure_first_prompt_sections(data)
    _scrub_absolute_automation(data)
    _ensure_ops_mttd_mttr(data)
    return data
