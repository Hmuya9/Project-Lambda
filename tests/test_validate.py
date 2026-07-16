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


FLUIDSTACK_ROADMAP = _latest_roadmap_json() or (
    ROOT / "outputs" / "roadmap_20260715_175853.json"
)
FLUIDSTACK_JD = ROOT / "examples" / "jobs" / "fluidstack_production_engineering.md"


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
        "missing_mental_models": [],
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
                "software portability / machine-report",
                "APIs",
                "Why Docker exists",
                "health checks",
            ],
            "role_specific_track": [
                "GPU repair pipeline simulation capstone",
                "repair state machine",
                "BMC/Redfish telemetry",
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
    data["investigation_roadmap"][2]["track"] = "role_specific"
    data["roadmap_tracks"]["role_specific_track"].append("Why Docker exists")
    # remove from general track matching
    data["roadmap_tracks"]["general_engineering_track"] = [
        e
        for e in data["roadmap_tracks"]["general_engineering_track"]
        if "docker" not in e.lower()
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
    # Ensure no BMC/Redfish/IPMI in role-specific content
    data["roadmap_tracks"]["role_specific_track"] = [
        "GPU repair pipeline simulation capstone",
        "repair state machine",
        "hardware telemetry",
    ]
    jd = FLUIDSTACK_JD.read_text(encoding="utf-8") if FLUIDSTACK_JD.exists() else (
        "Own Redfish and BMC tooling. Firmware-level telemetry and IPMI."
    )
    with pytest.raises(ValidationError) as exc:
        validate_roadmap(data, job_description=jd)
    assert "redfish" in str(exc.value).lower() or "bmc" in str(exc.value).lower()


@pytest.mark.skipif(
    not FLUIDSTACK_ROADMAP.exists(),
    reason="Fluidstack generated roadmap JSON not present",
)
def test_fluidstack_generated_roadmap_passes():
    data = json.loads(FLUIDSTACK_ROADMAP.read_text(encoding="utf-8"))
    jd = FLUIDSTACK_JD.read_text(encoding="utf-8") if FLUIDSTACK_JD.exists() else None
    validate_roadmap(data, job_description=jd)
