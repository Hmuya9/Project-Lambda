"""Lightweight tests for Project Lambda semantic validation."""

from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from lambda_core.validate import ValidationError, validate_roadmap

ROOT = Path(__file__).resolve().parents[1]
# Prefer the newest generated roadmap_*.json; fall back to Step-1 fixture if present.
def _latest_roadmap_json() -> Path | None:
    outputs = ROOT / "outputs"
    if not outputs.is_dir():
        return None
    candidates = sorted(outputs.glob("roadmap_*.json"), key=lambda p: p.stat().st_mtime)
    return candidates[-1] if candidates else None


FLUIDSTACK_JD = ROOT / "examples" / "jobs" / "fluidstack_production_engineering.md"
AI_INFRA_JD = ROOT / "examples" / "jobs" / "ai_infra_systems.md"


def _minimal_good_roadmap() -> dict:
    """Smallest-ish valid roadmap structure for mutation tests."""
    inv_portability = {
        "title": "How does software move between machines and still work?",
        "track": "general",
        "expensive_problem": "Software fails when moved between machines.",
        "engineering_question": "Why do runtime, dependencies, and configuration break portability?",
        "why_matters_for_role": "Production systems must deploy reliably.",
        "phase_0_mental_model": (
            "Software depends on a stack of assumptions: the runtime version, installed "
            "dependencies, environment variables, filesystem paths, operating system "
            "behavior, and permissions. Because each layer can differ between machines, "
            "a program that works locally can fail elsewhere. Failure modes include missing "
            "libraries, wrong config defaults, and path assumptions that only held on the "
            "developer laptop. Understanding this causal chain is the portability mental model."
        ),
        "visual_system_model": (
            "Sketch: developer machine → Git clone → runtime + dependencies + env vars + "
            "filesystem + OS permissions → target machine. Mark failure layers at each hop."
        ),
        "subquestions": ["q1", "q2", "q3"],
        "concepts_and_vocabulary": ["runtime", "dependency", "env var"],
        "engineering_principles": ["make assumptions explicit", "document setup"],
        "technologies_involved": [],
        "observe_first": "Watch a setup fail on a clean machine.",
        "build_or_modify": (
            "Build project machine-report: check Python version, require APP_ENV, "
            "use one external dependency, write output/report.txt, log steps, "
            "fail clearly when config is missing, include README + failure log + "
            "assumptions table."
        ),
        "intentionally_break_debug": "Change Python version and missing dependency.",
        "improve": "Add clearer setup instructions.",
        "github_evidence": "Repo with machine-report script + README + setup notes.",
        "obsidian_engineering_page": "Software Portability",
        "two_minute_explanation_target": "Explain environment mismatch failures.",
        "exit_criteria": ["c1", "c2", "c3"],
        "builds_on_prior_artifact": "none",
        "artifact_this_investigation_produces": "src/machine_report.py in fleet-repair-lab",
        "module_or_folder_added": "src/machine_report.py",
        "delta_from_previous_investigation": "none — starting investigation",
        "capstone_delta": "n/a — not the capstone",
    }
    inv_docker = {
        **copy.deepcopy(inv_portability),
        "title": "Why does Docker exist?",
        "track": "general",
        "expensive_problem": "Environment mismatch survives README-only packaging.",
        "engineering_question": "What pain does container packaging solve?",
        "phase_0_mental_model": (
            "After experiencing portability failures, Docker appears as a response to "
            "environment mismatch: it packages runtime and dependency assumptions so the "
            "same image behaves more consistently across hosts. It does not remove all "
            "failure modes; networking, volumes, and permissions still matter. The mental "
            "model is: containerization reduces, but does not erase, environment drift."
        ),
        "visual_system_model": (
            "Host OS → Docker daemon → image layers → container filesystem → app process. "
            "Show env mismatch paths avoided vs still possible."
        ),
        "build_or_modify": "Add a Dockerfile for the same fleet-repair-lab repo.",
        "technologies_involved": [
            {
                "technology": "Docker",
                "engineering_pain_it_solves": (
                    "Software behaves differently across machines because runtime, "
                    "dependencies, filesystem layout, OS assumptions, and config differ."
                ),
            }
        ],
        "builds_on_prior_artifact": "src/machine_report.py",
        "artifact_this_investigation_produces": "Dockerfile for fleet-repair-lab",
        "module_or_folder_added": "Dockerfile",
        "delta_from_previous_investigation": "Containerizes the same repo so packaging is explicit.",
        "capstone_delta": "n/a — not the capstone",
    }
    inv_api = {
        **copy.deepcopy(inv_portability),
        "title": "Why do services expose APIs?",
        "track": "general",
        "build_or_modify": "Add an HTTP API module to the same cumulative repo.",
        "technologies_involved": [],
        "builds_on_prior_artifact": "src/machine_report.py",
        "artifact_this_investigation_produces": "src/api/",
        "module_or_folder_added": "src/api/",
        "delta_from_previous_investigation": "Adds an HTTP boundary to the same system.",
        "capstone_delta": "n/a — not the capstone",
    }
    inv_health = {
        **copy.deepcopy(inv_portability),
        "title": "Why do production systems need health checks?",
        "track": "general",
        "build_or_modify": "Add health check endpoints to the same cumulative repo.",
        "technologies_involved": [],
        "builds_on_prior_artifact": "src/api/",
        "artifact_this_investigation_produces": "src/health/",
        "module_or_folder_added": "src/health/",
        "delta_from_previous_investigation": "Adds health endpoints and failure states.",
        "capstone_delta": "n/a — not the capstone",
    }
    inv_capstone = {
        **copy.deepcopy(inv_portability),
        "title": "Capstone: GPU Repair Pipeline Simulation",
        "track": "role_specific",
        "expensive_problem": "Fleet repair without a pipeline loses throughput.",
        "engineering_question": "How do telemetry, state machines, and metrics compose?",
        "build_or_modify": "Add verification + postmortem evidence to the same repo.",
        "technologies_involved": [],
        "builds_on_prior_artifact": "src/health/",
        "artifact_this_investigation_produces": "docs/verification-log.md + postmortem",
        "module_or_folder_added": "docs/verification-log.md",
        "delta_from_previous_investigation": (
            "Adds verification discipline on top of the integrated repair workflow."
        ),
        "capstone_delta": (
            "Previous work integrated repair. Capstone adds failure injection, measured "
            "MTTD/MTTR, false-positive notes, escalation boundaries, verification log, "
            "and an incident postmortem."
        ),
    }

    paste = """### Investigation 1: How does software move between machines and still work?

#### Phase 0 Mental Model
Software depends on runtime, dependencies, environment variables, filesystem paths,
and operating system assumptions. Because those layers differ between machines, setup
fails in predictable ways. Map each failure back to an assumption.

#### Visual System Model
developer machine -> git -> runtime/deps/env/fs/os -> target machine

#### Exact small project: machine-report
Build machine-report that:
- checks Python version
- reads required env var APP_ENV
- uses one external dependency
- writes output/report.txt
- logs what it is doing
- fails clearly when required configuration is missing
- includes README setup, a failure log, and an assumptions table

#### Commands to run
python -m venv .venv
pip install -r requirements.txt
set APP_ENV=dev
python src/machine_report.py

#### Subquestions
- What breaks first when the runtime differs?
- How do missing dependencies present?
- Which config assumptions are silent?

#### Observe
Watch a fresh machine fail setup.

#### Build or Modify
Implement machine-report as specified above.

#### Intentionally Break / Debug
Unset APP_ENV; change Python version; remove the dependency.

#### Improve
Tighten setup instructions and assumptions table.

#### GitHub evidence
Repo with machine_report.py, README, failure log, assumptions table, output/report.txt.

#### Obsidian evidence
Engineering page: Software Portability — assumptions table and failure modes.

#### Exit criteria
- Can explain environment mismatch
- Has setup log artifact
- Can teach the failure modes in two minutes
"""

    # pad paste to >= 1000 chars if needed
    while len(paste) < 1000:
        paste += "\nAdditional notes on portability failure modes and layer assumptions."

    titles = [
        inv_portability["title"],
        inv_api["title"],
        inv_docker["title"],
        inv_health["title"],
        inv_capstone["title"],
    ]
    modules = [
        "src/machine_report.py",
        "src/api/",
        "Dockerfile",
        "src/health/",
        "docs/verification-log.md",
    ]
    caps = [
        "portability baseline",
        "API boundary",
        "container packaging",
        "health checks",
        "capstone verification",
    ]

    return {
        "role_family": {
            "primary_family": "gpu_fleet_production_engineering",
            "secondary_families": ["data_center_compute_infrastructure"],
            "why_this_family": (
                "JD owns GPU fleet repair pipelines, return-to-service, and "
                "BMC/Redfish hardware telemetry."
            ),
            "excluded_families": ["ai_infrastructure_model_serving"],
        },
        "role_interpretation": {
            "one_liner": "Fleet repair ops engineer",
            "real_mission": "Turn GPU failure into a measured repair pipeline.",
            "what_success_looks_like": (
                "Common-path repair automation with escalation for unsafe states "
                "and fail-closed behavior when recovery is ambiguous."
            ),
            "what_this_role_is_not": ["ticket closer", "YAML-only ops"],
            "role_signature_claims": [
                "GPU failure is not a ticket; it is a fleet throughput problem.",
                "Repair must become a pipeline, not a manual procedure.",
                "Health visibility must come from real signals, not vibes.",
                "Automation must know when to stop and escalate.",
            ],
        },
        "expensive_problem_map": [],
        "performance_requirements": [
            {
                "requirement": "Common-path repair automation with escalation gates",
                "source": "implied_by_jd",
                "why_it_matters": "Throughput without unsafe full automation.",
            }
        ],
        "surface_keywords_vs_deep_skills": [],
        "candidate_transfer_map": {
            "transferable_intuition": [],
            "missing_evidence": [
                {
                    "gap": "Linux fluency evidence",
                    "artifact_required": "GitHub repo with shell notes and README setup log",
                }
            ],
            "misleading_overclaims_to_avoid": [],
            "strongest_positioning_angle": "x",
        },
        "missing_mental_models": [
            {
                "mental_model": "Observability and alerting for production health",
                "why_required_before_role_work": "Need signal discipline before repair automation.",
                "what_goes_wrong_without_it": "Blind repair loops and noisy pages.",
                "first_investigation_that_builds_it": inv_health["title"],
            }
        ],
        "general_engineering_value_threshold": [
            {
                "capability": "Linux/server fluency",
                "artifact_evidence_required": (
                    "GitHub repo, README, shell commands, and troubleshooting notes — "
                    "not field experience alone."
                ),
            }
        ],
        "skill_dependency_graph": [],
        "roadmap_tracks": {
            "general_engineering_track": [
                inv_portability["title"],
                inv_api["title"],
                inv_docker["title"],
                inv_health["title"],
            ],
            "role_specific_track": [
                inv_capstone["title"],
            ],
        },

        "cumulative_system": {
            "system_name": "fleet-repair-lab",
            "system_purpose": "Grow one fleet repair simulation system.",
            "why_this_system_matches_the_role": "Mirrors GPU fleet repair operations.",
            "starting_scope": "portable machine-report script",
            "final_capstone_shape": (
                "Verified repair pipeline with explicit escalation boundaries, "
                "failure injection, and postmortem evidence."
            ),
            "suggested_repo_name": "fleet-repair-lab",
            "repo_growth_model": [
                {
                    "investigation_number": n,
                    "investigation_title": title,
                    "folder_or_module_added": mod,
                    "capability_added": cap,
                    "why_it_matters": "cumulative growth",
                    "evidence_created": "artifact",
                }
                for n, title, mod, cap in zip(
                    range(1, 6), titles, modules, caps, strict=True
                )
            ],
        },
        "investigation_roadmap": [
            inv_portability,
            inv_api,
            inv_docker,
            inv_health,
            inv_capstone,
        ],
        "proof_of_work_ladder": [
            {
                "level": n,
                "title": title,
                "same_system_name": "fleet-repair-lab",
                "module_or_folder_added": mod,
                "extends_previous": "prior level of fleet-repair-lab",
                "new_capability_added": cap,
                "what_new_proof_it_creates": proof,
                "why_this_is_not_a_separate_project": "Same repo, new module only.",
                "evidence": ["README update", "module code"],
                "connected_investigations": [title],
            }
            for n, title, mod, cap, proof in [
                (1, titles[0], modules[0], "report", "setup log"),
                (2, titles[1], modules[1], "http", "api tests"),
                (3, titles[2], modules[2], "image", "run log"),
                (4, titles[3], modules[3], "health", "health log"),
                (5, titles[4], modules[4], "verify", "postmortem"),
            ]
        ],
        "first_investigation_prompt": {
            "ready_to_paste_prompt": paste,
            "expensive_problem": "portability",
            "engineering_question": "how does software move",
            "phase_0_mental_model": inv_portability["phase_0_mental_model"],
            "observe_first": "observe",
            "build_or_modify": inv_portability["build_or_modify"],
            "intentionally_break_debug": "break",
            "improve": "improve",
        },
        "evidence_plan": {
            "obsidian_pages": ["a", "b", "c", "d", "e"],
            "github_repository": {
                "repo_name": "fleet-repair-lab",
                "repo_purpose": "one cumulative fleet repair system",
                "final_folder_structure": (
                    "fleet-repair-lab/\n"
                    "├── README.md\n"
                    "├── Dockerfile\n"
                    "├── docs/\n"
                    "│   └── verification-log.md\n"
                    "├── src/\n"
                    "│   ├── machine_report.py\n"
                    "│   ├── api/\n"
                    "│   └── health/\n"
                    "├── tests/\n"
                    "└── outputs/\n"
                ),
                "evidence_files": [
                    "README.md",
                    "docs/architecture.md",
                    "docs/failure-log.md",
                    "docs/verification-log.md",
                    "docs/incident-postmortem.md",
                    "outputs/metrics-sample.json",
                    "tests/",
                    "src/",
                ],
            },
            "diagrams": ["d1", "d2", "d3", "d4"],
            "benchmarks_or_logs": ["b1", "b2", "b3", "b4"],
            "readme_sections": ["r1", "r2", "r3", "r4"],
            "interview_artifacts": ["i1", "i2", "i3"],
        },
        "operational_metrics_contract": [
            {
                "metric": "MTTD (target: under 5 minutes)",
                "source": "proposed_project_target",
                "why_it_matters": "Fast detection protects fleet throughput.",
                "how_to_measure_in_the_project": "Timestamp detect vs inject.",
                "what_bad_result_means": "Blind spots in telemetry.",
            },
            {
                "metric": "MTTR (target: under 30 minutes)",
                "source": "proposed_project_target",
                "why_it_matters": "Return-to-service speed.",
                "how_to_measure_in_the_project": "Timestamp repair start to green check.",
                "what_bad_result_means": "Stuck repair queue.",
            },
            {
                "metric": "false positive rate",
                "source": "proposed_project_target",
                "why_it_matters": "Noise burns operators.",
                "how_to_measure_in_the_project": "Count bad alerts / total alerts.",
                "what_bad_result_means": "Alert fatigue.",
            },
            {
                "metric": "escalation rate",
                "source": "implied_by_jd",
                "why_it_matters": "Shows automation boundaries working.",
                "how_to_measure_in_the_project": "Escalated / total repairs.",
                "what_bad_result_means": "Automation too aggressive or too timid.",
            },
            {
                "metric": "return-to-service pass rate",
                "source": "proposed_project_target",
                "why_it_matters": "Prevents reintroducing bad hosts.",
                "how_to_measure_in_the_project": "Pass vs fail after repair.",
                "what_bad_result_means": "Weak verification gate.",
            },
        ],
        "automation_boundaries": {
            "safe_to_automate": [
                "collect logs",
                "isolate known-safe failure codes",
                "open repair tickets with context",
            ],
            "requires_human_escalation": [
                "ambiguous thermal signals",
                "firmware flash decisions",
                "unsafe recovery loops",
            ],
            "fail_closed_conditions": [
                "missing telemetry freshness",
                "conflicting health signals",
            ],
            "manual_approval_gates": [
                "return host to production",
                "apply destructive repair action",
            ],
        },
        "capstone_proof_contract": {
            "what_it_must_demonstrate": [
                "failure injection discipline",
                "measured MTTD/MTTR",
                "escalation boundaries",
                "verification before return-to-service",
            ],
            "required_failure_injections": [
                "missing dependency",
                "stale telemetry",
                "failed return-to-service check",
            ],
            "required_measurements": [
                "Target MTTD for injected faults",
                "Target MTTR / return-to-service time",
                "false positive notes",
            ],
            "required_docs": [
                "docs/verification-log.md",
                "docs/incident-postmortem.md",
                "README architecture tradeoffs",
                "architecture diagram",
            ],
            "hiring_manager_readout": (
                "After completing this capstone, the candidate should be able to say: "
                "this one fleet-repair lab starts with portability and grows into a "
                "repair pipeline. Target measurement: MTTD/MTTR on injected faults. "
                "Evidence to produce: escalation boundaries and a postmortem. "
                "The final readout should include verification before return-to-service."
            ),
        },
        "interview_readiness_map": [
            {
                "expectation": "portability",
                "evidence_needed": "GitHub repo with README and setup log",
            }
        ],
        "guardrail_checks": {},
    }


def test_docker_in_investigation_1_fails():
    data = _minimal_good_roadmap()
    data["investigation_roadmap"][0]["title"] = "Learn Docker for reproducibility"
    data["investigation_roadmap"][0]["technologies_involved"] = [
        {
            "technology": "Docker",
            "engineering_pain_it_solves": (
                "Software behaves differently across machines because runtime and "
                "dependencies differ between hosts."
            ),
        }
    ]
    with pytest.raises(ValidationError) as exc:
        validate_roadmap(data)
    assert "Docker" in str(exc.value) or "docker" in str(exc.value).lower()


def test_one_sentence_mental_model_fails():
    data = _minimal_good_roadmap()
    data["investigation_roadmap"][0]["phase_0_mental_model"] = (
        "Reproducibility is important for reliable systems."
    )
    with pytest.raises(ValidationError) as exc:
        validate_roadmap(data)
    assert "mental model" in str(exc.value).lower()


def test_background_as_evidence_fails():
    data = _minimal_good_roadmap()
    data["general_engineering_value_threshold"][0]["artifact_evidence_required"] = (
        "Proven by experience with Linux servers in field service roles."
    )
    with pytest.raises(ValidationError) as exc:
        validate_roadmap(data)
    assert "background experience" in str(exc.value).lower()


def test_good_minimal_roadmap_passes():
    validate_roadmap(_minimal_good_roadmap())


def test_growth_title_mismatch_fails():
    data = _minimal_good_roadmap()
    data["cumulative_system"]["repo_growth_model"][2]["investigation_title"] = (
        "Why do metrics and alerts exist?"
    )
    with pytest.raises(ValidationError) as exc:
        validate_roadmap(data)
    assert "title mismatch" in str(exc.value).lower()


def test_growth_module_mismatch_fails():
    data = _minimal_good_roadmap()
    data["cumulative_system"]["repo_growth_model"][1]["folder_or_module_added"] = (
        "src/observability/"
    )
    with pytest.raises(ValidationError) as exc:
        validate_roadmap(data)
    msg = str(exc.value).lower()
    assert "module mismatch" in msg or "does not appear" in msg


def test_docker_role_specific_fails():
    data = _minimal_good_roadmap()
    docker_title = data["investigation_roadmap"][2]["title"]
    data["investigation_roadmap"][2]["track"] = "role_specific"
    data["roadmap_tracks"]["general_engineering_track"] = [
        e
        for e in data["roadmap_tracks"]["general_engineering_track"]
        if "docker" not in e.lower()
    ]
    data["roadmap_tracks"]["role_specific_track"] = [
        docker_title,
        data["investigation_roadmap"][4]["title"],
    ]
    with pytest.raises(ValidationError) as exc:
        validate_roadmap(data, job_description="Own GPU fleet health and repair pipelines.")
    assert "docker" in str(exc.value).lower()


def test_stated_in_jd_fabricated_threshold_fails():
    data = _minimal_good_roadmap()
    data["operational_metrics_contract"][0]["source"] = "stated_in_jd"
    jd = "Own Redfish and BMC tooling. Build repair pipelines for GPU fleet health."
    with pytest.raises(ValidationError) as exc:
        validate_roadmap(data, job_description=jd)
    assert "stated_in_jd" in str(exc.value).lower() or "proposed_project_target" in str(
        exc.value
    ).lower()


def test_fake_capstone_achievement_language_fails():
    data = _minimal_good_roadmap()
    data["capstone_proof_contract"]["hiring_manager_readout"] = (
        "I built a fleet repair lab. I successfully validated the pipeline. "
        "MTTD was consistently under 5 minutes and MTTR was maintained below 30 minutes. "
        "I proved the system works."
    )
    with pytest.raises(ValidationError) as exc:
        validate_roadmap(data)
    assert "fake" in str(exc.value).lower() or "achievement" in str(exc.value).lower()


def test_vague_investigation_1_fails():
    data = _minimal_good_roadmap()
    vague = (
        "### Phase 0 Mental Model\nUnderstand portability.\n\n"
        "### observe\nLook around.\n\n### build\nCreate a simple application.\n\n"
        "### break\nBreak it.\n\n### improve\nImprove it.\n\n"
        "### GitHub\nPush code.\n\n### Obsidian\nTake notes.\n"
    )
    while len(vague) < 1000:
        vague += "\nMore filler about creating a simple application without specifics."
    data["first_investigation_prompt"]["ready_to_paste_prompt"] = vague
    data["first_investigation_prompt"]["build_or_modify"] = "Create a simple application."
    data["investigation_roadmap"][0]["build_or_modify"] = "Create a simple application."
    with pytest.raises(ValidationError) as exc:
        validate_roadmap(data)
    msg = str(exc.value).lower()
    assert "vague" in msg or "machine-report" in msg


def test_redfish_required_when_in_jd():
    data = _minimal_good_roadmap()
    # Keep exact track match but strip BMC/Redfish from all role content
    for inv in data["investigation_roadmap"]:
        for key in ("title", "engineering_question", "expensive_problem", "phase_0_mental_model",
                    "build_or_modify"):
            inv[key] = (
                str(inv.get(key) or "")
                .replace("BMC", "hardware")
                .replace("Redfish", "telemetry")
                .replace("IPMI", "bus")
            )
        inv["subquestions"] = ["q1", "q2", "q3"]
        inv["concepts_and_vocabulary"] = ["runtime", "dependency", "env var"]
    # Rebuild exact tracks after title edits
    generals = [i for i in data["investigation_roadmap"] if i["track"] == "general"]
    roles = [i for i in data["investigation_roadmap"] if i["track"] == "role_specific"]
    data["roadmap_tracks"]["general_engineering_track"] = [i["title"] for i in generals]
    data["roadmap_tracks"]["role_specific_track"] = [i["title"] for i in roles]
    for i, inv in enumerate(data["investigation_roadmap"]):
        data["proof_of_work_ladder"][i]["title"] = inv["title"]
        data["proof_of_work_ladder"][i]["connected_investigations"] = [inv["title"]]
        data["cumulative_system"]["repo_growth_model"][i]["investigation_title"] = inv["title"]
    jd = FLUIDSTACK_JD.read_text(encoding="utf-8") if FLUIDSTACK_JD.exists() else (
        "Own Redfish and BMC tooling. Firmware-level telemetry and IPMI."
    )
    with pytest.raises(ValidationError) as exc:
        validate_roadmap(data, job_description=jd)
    assert "redfish" in str(exc.value).lower() or "bmc" in str(exc.value).lower()


def test_track_titles_must_exactly_match_investigations():
    data = _minimal_good_roadmap()
    data["roadmap_tracks"]["role_specific_track"] = [
        "How do BMC/Redfish-style interfaces expose hardware state?"
    ]
    with pytest.raises(ValidationError) as exc:
        validate_roadmap(data)
    assert "exactly match" in str(exc.value).lower() or "missing from" in str(exc.value).lower()


def test_paragraph_track_item_fails():
    data = _minimal_good_roadmap()
    data["roadmap_tracks"]["general_engineering_track"][0] = (
        "How does software move between machines and still work? This investigation "
        "covers runtime assumptions, dependencies, configuration, and filesystem "
        "portability across developer and production hosts in depth."
    )
    with pytest.raises(ValidationError) as exc:
        validate_roadmap(data)
    assert "paragraph" in str(exc.value).lower()


def test_proof_ladder_connected_must_include_own_title():
    data = _minimal_good_roadmap()
    data["proof_of_work_ladder"][0]["connected_investigations"] = [
        data["investigation_roadmap"][1]["title"]
    ]
    with pytest.raises(ValidationError) as exc:
        validate_roadmap(data)
    assert "connected_investigations" in str(exc.value).lower()


def test_proof_ladder_title_must_match_investigation():
    data = _minimal_good_roadmap()
    data["proof_of_work_ladder"][1]["title"] = "Some other title entirely"
    with pytest.raises(ValidationError) as exc:
        validate_roadmap(data)
    assert "must exactly equal" in str(exc.value).lower()


def test_ai_infra_jd_rejects_bmc_redfish_leakage():
    data = _minimal_good_roadmap()
    data["role_family"] = {
        "primary_family": "ai_infrastructure_model_serving",
        "secondary_families": [],
        "why_this_family": (
            "JD owns model serving, inference latency, throughput, and observability "
            "for LLM workloads — not hardware fleet repair."
        ),
        "excluded_families": ["gpu_fleet_production_engineering"],
    }
    data["cumulative_system"]["system_name"] = "ai-inference-reliability-lab"
    data["cumulative_system"]["suggested_repo_name"] = "ai-inference-reliability-lab"
    data["cumulative_system"]["final_capstone_shape"] = (
        "Local inference service reliability lab with latency/throughput evidence."
    )
    for level in data["proof_of_work_ladder"]:
        level["same_system_name"] = "ai-inference-reliability-lab"
    # Inject BMC leakage into role-specific track/investigation
    data["investigation_roadmap"][4]["title"] = (
        "How do BMC/Redfish-style interfaces expose hardware state?"
    )
    data["investigation_roadmap"][4]["track"] = "role_specific"
    data["roadmap_tracks"]["role_specific_track"] = [
        data["investigation_roadmap"][4]["title"]
    ]
    data["proof_of_work_ladder"][4]["title"] = data["investigation_roadmap"][4]["title"]
    data["proof_of_work_ladder"][4]["connected_investigations"] = [
        data["investigation_roadmap"][4]["title"]
    ]
    data["cumulative_system"]["repo_growth_model"][4]["investigation_title"] = (
        data["investigation_roadmap"][4]["title"]
    )
    jd = AI_INFRA_JD.read_text(encoding="utf-8")
    with pytest.raises(ValidationError) as exc:
        validate_roadmap(data, job_description=jd)
    msg = str(exc.value).lower()
    assert "bmc" in msg or "redfish" in msg or "repair" in msg


def test_ai_infra_family_requires_serving_style_work():
    data = _minimal_good_roadmap()
    data["role_family"] = {
        "primary_family": "ai_infrastructure_model_serving",
        "secondary_families": [],
        "why_this_family": (
            "JD focuses on model serving paths, inference latency budgets, and "
            "token throughput observability."
        ),
        "excluded_families": ["gpu_fleet_production_engineering"],
    }
    data["cumulative_system"]["system_name"] = "fleet-repair-lab"
    data["cumulative_system"]["suggested_repo_name"] = "fleet-repair-lab"
    for level in data["proof_of_work_ladder"]:
        level["same_system_name"] = "fleet-repair-lab"
    jd = AI_INFRA_JD.read_text(encoding="utf-8")
    with pytest.raises(ValidationError) as exc:
        validate_roadmap(data, job_description=jd)
    msg = str(exc.value).lower()
    assert "inference" in msg or "serving" in msg or "fleet-repair" in msg


def test_unmeasurable_proposed_metric_fails():
    data = _minimal_good_roadmap()
    data["operational_metrics_contract"][2] = {
        "metric": "User satisfaction rating after six months",
        "source": "proposed_project_target",
        "why_it_matters": "Business likes happy users.",
        "how_to_measure_in_the_project": "Survey users for satisfaction.",
        "what_bad_result_means": "Unhappy users.",
    }
    with pytest.raises(ValidationError) as exc:
        validate_roadmap(data)
    assert "business" in str(exc.value).lower() or "measurable" in str(exc.value).lower()


def test_observability_mm_cannot_point_at_api_investigation():
    data = _minimal_good_roadmap()
    data["missing_mental_models"][0]["first_investigation_that_builds_it"] = (
        "Why do services expose APIs?"
    )
    with pytest.raises(ValidationError) as exc:
        validate_roadmap(data)
    assert "observability" in str(exc.value).lower() or "api" in str(exc.value).lower()


def test_align_maps_repair_slogan_to_exact_investigation_title():
    from lambda_core.align import align_roadmap_structure

    data = _minimal_good_roadmap()
    # Capstone title is repair-related in the fleet fixture
    repair_title = data["investigation_roadmap"][4]["title"]
    assert "repair" in repair_title.lower() or "pipeline" in repair_title.lower()
    data["missing_mental_models"].append(
        {
            "mental_model": "Repair must become a pipeline",
            "why_required_before_role_work": "Fleet throughput depends on repair automation.",
            "what_goes_wrong_without_it": "Manual heroics and stuck hosts.",
            "first_investigation_that_builds_it": (
                "Turn deployment/repair into a pipeline, not a procedure."
            ),
        }
    )
    align_roadmap_structure(data)
    pointer = data["missing_mental_models"][-1]["first_investigation_that_builds_it"]
    assert pointer == repair_title
    validate_roadmap(data)


def test_align_maps_observability_phrase_to_metrics_or_health_title():
    from lambda_core.align import align_roadmap_structure

    data = _minimal_good_roadmap()
    metrics_or_health = [
        t["title"]
        for t in data["investigation_roadmap"]
        if any(k in t["title"].lower() for k in ("health", "metric", "alert"))
    ]
    assert metrics_or_health
    data["missing_mental_models"].append(
        {
            "mental_model": "Signal discipline under load",
            "why_required_before_role_work": "Need measurable health before automation.",
            "what_goes_wrong_without_it": "Blind pages and noisy alerts.",
            "first_investigation_that_builds_it": "Observability and alerting",
        }
    )
    align_roadmap_structure(data)
    pointer = data["missing_mental_models"][-1]["first_investigation_that_builds_it"]
    assert pointer in metrics_or_health
    assert pointer in [i["title"] for i in data["investigation_roadmap"]]
    validate_roadmap(data)


def test_align_maps_portability_phrase_to_exact_portability_title():
    from lambda_core.align import align_roadmap_structure

    data = _minimal_good_roadmap()
    port_title = data["investigation_roadmap"][0]["title"]
    data["missing_mental_models"].append(
        {
            "mental_model": "Environment mismatch mental model",
            "why_required_before_role_work": "Deployments fail without portability understanding.",
            "what_goes_wrong_without_it": "Works on my machine failures.",
            "first_investigation_that_builds_it": "software portability",
        }
    )
    align_roadmap_structure(data)
    pointer = data["missing_mental_models"][-1]["first_investigation_that_builds_it"]
    assert pointer == port_title
    validate_roadmap(data)


def test_unmapped_mental_model_pointer_still_fails_validation():
    from lambda_core.align import align_roadmap_structure

    data = _minimal_good_roadmap()
    data["missing_mental_models"].append(
        {
            "mental_model": "Quantum annealing schedules",
            "why_required_before_role_work": "Unrelated concept.",
            "what_goes_wrong_without_it": "No mapping should exist.",
            "first_investigation_that_builds_it": (
                "How do quantum annealers schedule qubit calibrations?"
            ),
        }
    )
    align_roadmap_structure(data)
    pointer = data["missing_mental_models"][-1]["first_investigation_that_builds_it"]
    assert pointer not in [i["title"] for i in data["investigation_roadmap"]]
    with pytest.raises(ValidationError) as exc:
        validate_roadmap(data)
    assert "does not match any investigation title" in str(exc.value)


def test_validator_requires_exact_title_not_fuzzy_align():
    data = _minimal_good_roadmap()
    # Fuzzy-similar but not exact — must fail without running aligner
    data["missing_mental_models"][0]["first_investigation_that_builds_it"] = (
        "Why production systems need health checks somehow"
    )
    with pytest.raises(ValidationError) as exc:
        validate_roadmap(data)
    assert "does not match any investigation title" in str(exc.value)


def _latest_json_for_job(job_stem: str) -> Path | None:
    outputs = ROOT / "outputs"
    if not outputs.is_dir():
        return None
    # Prefer JSON whose markdown sibling mentions the job path
    candidates = sorted(outputs.glob("roadmap_*.json"), key=lambda p: p.stat().st_mtime, reverse=True)
    for path in candidates:
        md = path.with_suffix(".md")
        if md.exists() and job_stem in md.read_text(encoding="utf-8", errors="ignore"):
            return path
    return candidates[0] if candidates else None


@pytest.mark.skipif(not FLUIDSTACK_JD.exists(), reason="Fluidstack JD missing")
def test_fluidstack_jd_allows_fleet_repair_family_signals():
    """Unit-level: fleet fixture validates against Fluidstack JD signals."""
    data = _minimal_good_roadmap()
    # Add explicit BMC/Redfish role investigation so JD tooling requirement is met
    inv = copy.deepcopy(data["investigation_roadmap"][3])
    inv["title"] = "How do BMC/Redfish-style interfaces expose hardware state?"
    inv["track"] = "role_specific"
    inv["module_or_folder_added"] = "src/redfish_interface.py"
    inv["artifact_this_investigation_produces"] = "src/redfish_interface.py"
    inv["delta_from_previous_investigation"] = "Adds mocked BMC/Redfish telemetry."
    inv["capstone_delta"] = "n/a — not the capstone"
    # Insert before capstone
    data["investigation_roadmap"].insert(4, inv)
    # Capstone remains last
    titles = [i["title"] for i in data["investigation_roadmap"]]
    modules = [i["module_or_folder_added"] for i in data["investigation_roadmap"]]
    data["roadmap_tracks"]["general_engineering_track"] = [
        i["title"] for i in data["investigation_roadmap"] if i["track"] == "general"
    ]
    data["roadmap_tracks"]["role_specific_track"] = [
        i["title"] for i in data["investigation_roadmap"] if i["track"] == "role_specific"
    ]
    data["cumulative_system"]["repo_growth_model"] = [
        {
            "investigation_number": n,
            "investigation_title": title,
            "folder_or_module_added": mod,
            "capability_added": "cap",
            "why_it_matters": "growth",
            "evidence_created": "artifact",
        }
        for n, title, mod in zip(range(1, len(titles) + 1), titles, modules, strict=True)
    ]
    data["proof_of_work_ladder"] = [
        {
            "level": n,
            "title": title,
            "same_system_name": "fleet-repair-lab",
            "module_or_folder_added": mod,
            "extends_previous": "prior",
            "new_capability_added": "cap",
            "what_new_proof_it_creates": "proof",
            "why_this_is_not_a_separate_project": "Same repo.",
            "evidence": ["README"],
            "connected_investigations": [title],
        }
        for n, title, mod in zip(range(1, len(titles) + 1), titles, modules, strict=True)
    ]
    jd = FLUIDSTACK_JD.read_text(encoding="utf-8")
    validate_roadmap(data, job_description=jd)


def test_fluidstack_generated_roadmap_passes():
    path = _latest_json_for_job("fluidstack_production_engineering.md")
    if path is None or not path.exists():
        pytest.skip("Fluidstack generated roadmap JSON not present")
    from lambda_core.align import align_roadmap_structure

    data = json.loads(path.read_text(encoding="utf-8"))
    jd = FLUIDSTACK_JD.read_text(encoding="utf-8")
    align_roadmap_structure(data, job_description=jd)
    validate_roadmap(data, job_description=jd)
    family = (data.get("role_family") or {}).get("primary_family")
    if family:
        assert family == "gpu_fleet_production_engineering"


def test_ai_infra_generated_roadmap_passes_when_present():
    path = _latest_json_for_job("ai_infra_systems.md")
    if path is None or not path.exists():
        pytest.skip("AI infra generated roadmap JSON not present")
    from lambda_core.align import align_roadmap_structure

    data = json.loads(path.read_text(encoding="utf-8"))
    jd = AI_INFRA_JD.read_text(encoding="utf-8")
    align_roadmap_structure(data, job_description=jd)
    validate_roadmap(data, job_description=jd)
    family = (data.get("role_family") or {}).get("primary_family")
    assert family == "ai_infrastructure_model_serving"
    # Ignore schema/guardrail key names that mention Redfish as a forbidden early tool.
    scan = {k: v for k, v in data.items() if k != "guardrail_checks"}
    blob = json.dumps(scan).lower()
    assert "redfish" not in blob and "bmc" not in blob
    assert any(t in blob for t in ("inference", "latency", "throughput", "serving"))
