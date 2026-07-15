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
        "build_or_modify": "Create a tiny script with README setup steps.",
        "intentionally_break_debug": "Change Python version and missing dependency.",
        "improve": "Add clearer setup instructions.",
        "github_evidence": "Repo with script + README + setup notes.",
        "obsidian_engineering_page": "Software Portability",
        "two_minute_explanation_target": "Explain environment mismatch failures.",
        "exit_criteria": ["c1", "c2", "c3"],
        "builds_on_prior_artifact": "none",
        "artifact_this_investigation_produces": "portable script repo",
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
        "technologies_involved": [
            {
                "technology": "Docker",
                "engineering_pain_it_solves": (
                    "Software behaves differently across machines because runtime, "
                    "dependencies, filesystem layout, OS assumptions, and config differ."
                ),
            }
        ],
        "builds_on_prior_artifact": "portable script repo",
        "artifact_this_investigation_produces": "Dockerfile + run notes",
    }
    inv_api = {
        **copy.deepcopy(inv_portability),
        "title": "Why do services expose APIs?",
        "track": "general",
        "technologies_involved": [],
        "builds_on_prior_artifact": "portable script repo",
        "artifact_this_investigation_produces": "tiny HTTP service",
    }
    inv_health = {
        **copy.deepcopy(inv_portability),
        "title": "Why do production systems need health checks?",
        "track": "general",
        "technologies_involved": [],
        "builds_on_prior_artifact": "tiny HTTP service",
        "artifact_this_investigation_produces": "health endpoint",
    }
    inv_capstone = {
        **copy.deepcopy(inv_portability),
        "title": "Capstone: GPU Repair Pipeline Simulation",
        "track": "role_specific",
        "expensive_problem": "Fleet repair without a pipeline loses throughput.",
        "engineering_question": "How do telemetry, state machines, and metrics compose?",
        "technologies_involved": [],
        "builds_on_prior_artifact": "health endpoint",
        "artifact_this_investigation_produces": "repair pipeline sim",
    }

    paste = """### Investigation 1: How does software move between machines and still work?

#### Phase 0 Mental Model
Software depends on runtime, dependencies, environment variables, filesystem paths,
and operating system assumptions. Because those layers differ between machines, setup
fails in predictable ways. Map each failure back to an assumption.

#### Visual System Model
developer machine -> git -> runtime/deps/env/fs/os -> target machine

#### Subquestions
- What breaks first when the runtime differs?
- How do missing dependencies present?
- Which config assumptions are silent?

#### Observe
Watch a fresh machine fail setup.

#### Build or Modify
Create a tiny script with README setup.

#### Intentionally Break / Debug
Remove a dependency and change an env var.

#### Improve
Tighten setup instructions.

#### GitHub evidence
Repo with script, README, setup log.

#### Obsidian evidence
Engineering page: Software Portability.

#### Exit criteria
- Can explain environment mismatch
- Has setup log artifact
- Can teach the failure modes in two minutes
"""

    # pad paste to >= 1000 chars if needed
    while len(paste) < 1000:
        paste += "\nAdditional notes on portability failure modes and layer assumptions."

    return {
        "role_interpretation": {},
        "expensive_problem_map": [],
        "performance_requirements": [],
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
                "portability",
                "python automation",
                "apis",
                "docker",
            ],
            "role_specific_track": [
                "repair state machine",
                "telemetry",
                "gpu repair pipeline",
            ],
        },
        "investigation_roadmap": [
            inv_portability,
            inv_api,
            inv_docker,
            inv_health,
            inv_capstone,
        ],
        "proof_of_work_ladder": [],
        "first_investigation_prompt": {
            "ready_to_paste_prompt": paste,
            "expensive_problem": "portability",
            "engineering_question": "how does software move",
            "phase_0_mental_model": inv_portability["phase_0_mental_model"],
            "observe_first": "observe",
            "build_or_modify": "build",
            "intentionally_break_debug": "break",
            "improve": "improve",
        },
        "evidence_plan": {},
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


@pytest.mark.skipif(
    not FLUIDSTACK_ROADMAP.exists(),
    reason="Fluidstack generated roadmap JSON not present",
)
def test_fluidstack_generated_roadmap_passes():
    data = json.loads(FLUIDSTACK_ROADMAP.read_text(encoding="utf-8"))
    validate_roadmap(data)
