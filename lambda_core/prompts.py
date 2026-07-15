"""Prompt templates and output schema for Project Lambda Role-to-Roadmap generation.

Iterate product behavior here — keep CLI/UI wrappers stable.
"""

from __future__ import annotations

CONTRACT_JSON_SCHEMA: dict = {
    "type": "object",
    "additionalProperties": False,
    "required": [
        "role_interpretation",
        "expensive_problem_map",
        "performance_requirements",
        "surface_keywords_vs_deep_skills",
        "candidate_transfer_map",
        "missing_mental_models",
        "general_engineering_value_threshold",
        "skill_dependency_graph",
        "roadmap_tracks",
        "investigation_roadmap",
        "proof_of_work_ladder",
        "first_investigation_prompt",
        "evidence_plan",
        "interview_readiness_map",
        "guardrail_checks",
    ],
    "properties": {
        "role_interpretation": {
            "type": "object",
            "additionalProperties": False,
            "required": [
                "one_liner",
                "real_mission",
                "what_success_looks_like",
                "what_this_role_is_not",
            ],
            "properties": {
                "one_liner": {"type": "string"},
                "real_mission": {"type": "string"},
                "what_success_looks_like": {
                    "type": "string",
                    "description": (
                        "Never say 'fully automated'. Prefer highly automated common "
                        "paths with explicit human escalation for ambiguous, unsafe, "
                        "or failed recovery states."
                    ),
                },
                "what_this_role_is_not": {
                    "type": "array",
                    "items": {"type": "string"},
                    "minItems": 2,
                    "maxItems": 6,
                },
            },
        },
        "expensive_problem_map": {
            "type": "array",
            "minItems": 3,
            "maxItems": 8,
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": [
                    "problem",
                    "why_company_pays_for_it",
                    "constraints",
                    "failure_modes",
                    "jd_evidence",
                ],
                "properties": {
                    "problem": {"type": "string"},
                    "why_company_pays_for_it": {"type": "string"},
                    "constraints": {"type": "array", "items": {"type": "string"}},
                    "failure_modes": {"type": "array", "items": {"type": "string"}},
                    "jd_evidence": {"type": "string"},
                },
            },
        },
        "performance_requirements": {
            "type": "array",
            "minItems": 3,
            "maxItems": 10,
            "description": "What 'good' looks like for the role — performance/ops bars.",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": [
                    "requirement",
                    "source",
                    "why_it_matters",
                ],
                "properties": {
                    "requirement": {"type": "string"},
                    "source": {
                        "type": "string",
                        "description": (
                            "'stated in JD' | 'likely implied' | "
                            "'proposed project bar (not an employer requirement)'."
                        ),
                    },
                    "why_it_matters": {"type": "string"},
                },
            },
        },
        "surface_keywords_vs_deep_skills": {
            "type": "array",
            "minItems": 4,
            "maxItems": 12,
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": [
                    "surface_keyword",
                    "deep_skill_or_principle",
                    "engineering_pain_behind_it",
                    "danger_of_learning_it_in_isolation",
                ],
                "properties": {
                    "surface_keyword": {"type": "string"},
                    "deep_skill_or_principle": {"type": "string"},
                    "engineering_pain_behind_it": {
                        "type": "string",
                        "description": (
                            "The expensive pain that made this keyword matter — "
                            "not a tool definition."
                        ),
                    },
                    "danger_of_learning_it_in_isolation": {"type": "string"},
                },
            },
        },
        "candidate_transfer_map": {
            "type": "object",
            "additionalProperties": False,
            "description": (
                "Separate transferable intuition from missing software evidence. "
                "Never treat background experience as proof of software capability."
            ),
            "required": [
                "transferable_intuition",
                "missing_evidence",
                "misleading_overclaims_to_avoid",
                "strongest_positioning_angle",
            ],
            "properties": {
                "transferable_intuition": {
                    "type": "array",
                    "minItems": 2,
                    "maxItems": 8,
                    "items": {
                        "type": "object",
                        "additionalProperties": False,
                        "required": [
                            "intuition",
                            "profile_anchor",
                            "role_relevance",
                            "why_this_is_not_yet_software_evidence",
                        ],
                        "properties": {
                            "intuition": {"type": "string"},
                            "profile_anchor": {"type": "string"},
                            "role_relevance": {"type": "string"},
                            "why_this_is_not_yet_software_evidence": {
                                "type": "string",
                                "description": (
                                    "Explicitly state that intuition is not an artifact."
                                ),
                            },
                        },
                    },
                },
                "missing_evidence": {
                    "type": "array",
                    "minItems": 2,
                    "maxItems": 8,
                    "items": {
                        "type": "object",
                        "additionalProperties": False,
                        "required": [
                            "gap",
                            "why_it_blocks_credibility",
                            "artifact_required",
                            "first_mental_model_to_build",
                        ],
                        "properties": {
                            "gap": {"type": "string"},
                            "why_it_blocks_credibility": {"type": "string"},
                            "artifact_required": {
                                "type": "string",
                                "description": (
                                    "Concrete artifact: repo, setup log, README, "
                                    "shell notes, diagram, benchmark — not resume text."
                                ),
                            },
                            "first_mental_model_to_build": {"type": "string"},
                        },
                    },
                },
                "misleading_overclaims_to_avoid": {
                    "type": "array",
                    "items": {"type": "string"},
                    "minItems": 2,
                },
                "strongest_positioning_angle": {"type": "string"},
            },
        },
        "missing_mental_models": {
            "type": "array",
            "minItems": 4,
            "maxItems": 10,
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": [
                    "mental_model",
                    "why_required_before_role_work",
                    "what_goes_wrong_without_it",
                    "first_investigation_that_builds_it",
                ],
                "properties": {
                    "mental_model": {"type": "string"},
                    "why_required_before_role_work": {"type": "string"},
                    "what_goes_wrong_without_it": {"type": "string"},
                    "first_investigation_that_builds_it": {"type": "string"},
                },
            },
        },
        "general_engineering_value_threshold": {
            "type": "array",
            "minItems": 6,
            "maxItems": 14,
            "description": (
                "Baseline capabilities for general credibility. Evidence fields MUST "
                "name artifacts to build — never claim background experience as proof."
            ),
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": [
                    "capability",
                    "capability_scope",
                    "why_it_matters_generally",
                    "connected_role_problem",
                    "artifact_evidence_required",
                    "transferable_intuition_note",
                ],
                "properties": {
                    "capability": {"type": "string"},
                    "capability_scope": {
                        "type": "string",
                        "description": "'general_engineering' or 'role_specific'.",
                    },
                    "why_it_matters_generally": {"type": "string"},
                    "connected_role_problem": {"type": "string"},
                    "artifact_evidence_required": {
                        "type": "string",
                        "description": (
                            "Repo/README/log/demo/diagram required. NEVER 'proven by "
                            "field/industrial experience'."
                        ),
                    },
                    "transferable_intuition_note": {
                        "type": "string",
                        "description": (
                            "What background intuition helps, and why it is still "
                            "insufficient without an artifact."
                        ),
                    },
                },
            },
        },
        "skill_dependency_graph": {
            "type": "array",
            "minItems": 8,
            "maxItems": 16,
            "description": (
                "Problem/pain ordered — not tool shopping. Portability pain BEFORE "
                "Docker. Docker is a mid-graph consequence of local env mismatch, "
                "not Investigation 1. Example: software portability mental model → "
                "Python automation → config/env → logging/errors → HTTP/API → "
                "Why Docker exists → health checks → metrics → state machine → "
                "mocked telemetry → repair pipeline."
            ),
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": [
                    "skill_or_model",
                    "depends_on",
                    "unlocks",
                    "why_it_comes_before_later_work",
                ],
                "properties": {
                    "skill_or_model": {"type": "string"},
                    "depends_on": {"type": "array", "items": {"type": "string"}},
                    "unlocks": {"type": "array", "items": {"type": "string"}},
                    "why_it_comes_before_later_work": {
                        "type": "string",
                        "description": "Must cite engineering pain / dependency, not 'learn X'.",
                    },
                },
            },
        },
        "roadmap_tracks": {
            "type": "object",
            "additionalProperties": False,
            "required": ["general_engineering_track", "role_specific_track"],
            "properties": {
                "general_engineering_track": {
                    "type": "array",
                    "items": {"type": "string"},
                    "minItems": 4,
                    "maxItems": 12,
                    "description": (
                        "Titles/ids of general-value investigations. Fluidstack-like: "
                        "software portability; Python automation; config/env; "
                        "logging/errors; APIs; Why Docker exists; health checks; metrics."
                    ),
                },
                "role_specific_track": {
                    "type": "array",
                    "items": {"type": "string"},
                    "minItems": 3,
                    "maxItems": 10,
                    "description": (
                        "Titles/ids of JD-specific investigations. Fluidstack-like: "
                        "repair state machines; hardware telemetry; Redfish/BMC; "
                        "GPU qualification; GPU repair pipeline simulation."
                    ),
                },
            },
        },
        "investigation_roadmap": {
            "type": "array",
            "minItems": 8,
            "maxItems": 12,
            "description": (
                "Problem-first learning ladder. Investigation 1 for most "
                "software/systems roles MUST be software portability / environment "
                "mismatch WITHOUT Docker. Docker only later as 'Why does Docker "
                "exist?'. Final role capstone last."
            ),
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": [
                    "title",
                    "track",
                    "expensive_problem",
                    "engineering_question",
                    "why_matters_for_role",
                    "phase_0_mental_model",
                    "visual_system_model",
                    "subquestions",
                    "concepts_and_vocabulary",
                    "engineering_principles",
                    "technologies_involved",
                    "observe_first",
                    "build_or_modify",
                    "intentionally_break_debug",
                    "improve",
                    "github_evidence",
                    "obsidian_engineering_page",
                    "two_minute_explanation_target",
                    "exit_criteria",
                    "builds_on_prior_artifact",
                    "artifact_this_investigation_produces",
                ],
                "properties": {
                    "title": {"type": "string"},
                    "track": {
                        "type": "string",
                        "description": "Exactly 'general' or 'role_specific'.",
                    },
                    "expensive_problem": {"type": "string"},
                    "engineering_question": {"type": "string"},
                    "why_matters_for_role": {"type": "string"},
                    "phase_0_mental_model": {
                        "type": "string",
                        "description": (
                            "MULTI-PARAGRAPH / LAYERED (>=300 chars). Explain system "
                            "layers or causal chain the learner must picture. Must use "
                            "causal/layer language (at least two of: because, depends, "
                            "layer, failure, assumption, runtime, dependency, "
                            "environment, signal, state). Forbidden: one-sentence slogans."
                        ),
                    },
                    "visual_system_model": {
                        "type": "string",
                        "description": (
                            "Describe a diagram the learner should sketch "
                            "(boxes, arrows, failure points)."
                        ),
                    },
                    "subquestions": {
                        "type": "array",
                        "items": {"type": "string"},
                        "minItems": 3,
                        "maxItems": 8,
                    },
                    "concepts_and_vocabulary": {
                        "type": "array",
                        "items": {"type": "string"},
                        "minItems": 3,
                        "maxItems": 12,
                    },
                    "engineering_principles": {
                        "type": "array",
                        "items": {"type": "string"},
                        "minItems": 2,
                        "maxItems": 8,
                    },
                    "technologies_involved": {
                        "type": "array",
                        "description": (
                            "Objects only. Empty allowed for early investigations. "
                            "Never list a technology without engineering_pain_it_solves. "
                            "Investigation 1 must NOT include Docker."
                        ),
                        "items": {
                            "type": "object",
                            "additionalProperties": False,
                            "required": ["technology", "engineering_pain_it_solves"],
                            "properties": {
                                "technology": {"type": "string"},
                                "engineering_pain_it_solves": {"type": "string"},
                            },
                        },
                    },
                    "observe_first": {"type": "string"},
                    "build_or_modify": {"type": "string"},
                    "intentionally_break_debug": {"type": "string"},
                    "improve": {"type": "string"},
                    "github_evidence": {"type": "string"},
                    "obsidian_engineering_page": {"type": "string"},
                    "two_minute_explanation_target": {"type": "string"},
                    "exit_criteria": {
                        "type": "array",
                        "items": {"type": "string"},
                        "minItems": 3,
                        "maxItems": 8,
                    },
                    "builds_on_prior_artifact": {"type": "string"},
                    "artifact_this_investigation_produces": {"type": "string"},
                },
            },
        },
        "proof_of_work_ladder": {
            "type": "array",
            "minItems": 5,
            "maxItems": 10,
            "description": (
                "ONE progressive system that grows. Capstone (e.g. GPU repair "
                "pipeline simulation) is LAST only."
            ),
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": [
                    "level",
                    "title",
                    "proves",
                    "scope",
                    "extends_previous_level",
                    "same_system_name",
                    "evidence",
                    "why_not_before_prerequisites",
                    "connected_investigations",
                ],
                "properties": {
                    "level": {"type": "integer"},
                    "title": {"type": "string"},
                    "proves": {"type": "string"},
                    "scope": {"type": "string"},
                    "extends_previous_level": {"type": "string"},
                    "same_system_name": {"type": "string"},
                    "evidence": {
                        "type": "array",
                        "items": {"type": "string"},
                        "minItems": 1,
                    },
                    "why_not_before_prerequisites": {"type": "string"},
                    "connected_investigations": {
                        "type": "array",
                        "items": {"type": "string"},
                        "minItems": 1,
                    },
                },
            },
        },
        "first_investigation_prompt": {
            "type": "object",
            "additionalProperties": False,
            "description": (
                "Paste-ready Investigation 1. For software/systems roles: software "
                "portability. FORBIDDEN: Docker, K8s, Prometheus, Grafana, Redfish "
                "in this prompt."
            ),
            "required": [
                "ready_to_paste_prompt",
                "expensive_problem",
                "engineering_question",
                "phase_0_mental_model",
                "visual_system_model",
                "subquestions",
                "concepts_and_vocabulary",
                "observe_first",
                "build_or_modify",
                "intentionally_break_debug",
                "improve",
                "github_evidence",
                "obsidian_engineering_page",
                "two_minute_explanation_target",
                "exit_criteria",
            ],
            "properties": {
                "ready_to_paste_prompt": {
                    "type": "string",
                    "description": (
                        "Complete multi-section prompt including Phase 0 BEFORE build. "
                        "Must not recommend Docker tutorials for Investigation 1."
                    ),
                },
                "expensive_problem": {"type": "string"},
                "engineering_question": {"type": "string"},
                "phase_0_mental_model": {
                    "type": "string",
                    "description": "Layered multi-paragraph mental model — not one sentence.",
                },
                "visual_system_model": {"type": "string"},
                "subquestions": {
                    "type": "array",
                    "items": {"type": "string"},
                    "minItems": 3,
                },
                "concepts_and_vocabulary": {
                    "type": "array",
                    "items": {"type": "string"},
                    "minItems": 3,
                },
                "observe_first": {"type": "string"},
                "build_or_modify": {"type": "string"},
                "intentionally_break_debug": {"type": "string"},
                "improve": {"type": "string"},
                "github_evidence": {"type": "string"},
                "obsidian_engineering_page": {"type": "string"},
                "two_minute_explanation_target": {"type": "string"},
                "exit_criteria": {
                    "type": "array",
                    "items": {"type": "string"},
                    "minItems": 3,
                },
            },
        },
        "evidence_plan": {
            "type": "object",
            "additionalProperties": False,
            "required": [
                "obsidian_pages",
                "github_repos_or_folders",
                "diagrams",
                "benchmarks_or_logs",
                "readme_sections",
                "interview_artifacts",
            ],
            "properties": {
                "obsidian_pages": {
                    "type": "array",
                    "items": {"type": "string"},
                    "minItems": 5,
                },
                "github_repos_or_folders": {
                    "type": "array",
                    "items": {"type": "string"},
                    "minItems": 2,
                },
                "diagrams": {
                    "type": "array",
                    "items": {"type": "string"},
                    "minItems": 4,
                },
                "benchmarks_or_logs": {
                    "type": "array",
                    "items": {"type": "string"},
                    "minItems": 4,
                },
                "readme_sections": {
                    "type": "array",
                    "items": {"type": "string"},
                    "minItems": 4,
                },
                "interview_artifacts": {
                    "type": "array",
                    "items": {"type": "string"},
                    "minItems": 3,
                },
            },
        },
        "interview_readiness_map": {
            "type": "array",
            "minItems": 5,
            "maxItems": 10,
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": [
                    "expectation",
                    "current_readiness",
                    "evidence_needed",
                    "likely_interview_challenge",
                    "how_to_answer_after_roadmap",
                ],
                "properties": {
                    "expectation": {"type": "string"},
                    "current_readiness": {"type": "string"},
                    "evidence_needed": {
                        "type": "string",
                        "description": "Artifact-based evidence, not resume claims.",
                    },
                    "likely_interview_challenge": {"type": "string"},
                    "how_to_answer_after_roadmap": {"type": "string"},
                },
            },
        },
        "guardrail_checks": {
            "type": "object",
            "additionalProperties": False,
            "description": (
                "Model self-check. Prefer true only when honestly satisfied. "
                "Code validation comes in a later step."
            ),
            "required": [
                "investigation_1_avoids_docker_k8s_prometheus_redfish",
                "investigation_1_is_software_portability",
                "docker_appears_only_after_portability_pain",
                "mental_models_are_layered_not_one_liners",
                "background_not_treated_as_software_evidence",
                "capstone_is_last",
                "technologies_tied_to_engineering_pain",
                "notes",
            ],
            "properties": {
                "investigation_1_avoids_docker_k8s_prometheus_redfish": {
                    "type": "boolean",
                },
                "investigation_1_is_software_portability": {"type": "boolean"},
                "docker_appears_only_after_portability_pain": {"type": "boolean"},
                "mental_models_are_layered_not_one_liners": {"type": "boolean"},
                "background_not_treated_as_software_evidence": {"type": "boolean"},
                "capstone_is_last": {"type": "boolean"},
                "technologies_tied_to_engineering_pain": {"type": "boolean"},
                "notes": {"type": "array", "items": {"type": "string"}},
            },
        },
    },
}


SYSTEM_PROMPT = """You are Project Lambda — a problem-first engineering growth engine.

YOU ARE NOT:
- a course generator
- a project generator
- a keyword-to-curriculum generator
- a resume coach
- a study-plan writer that says "learn Docker / learn Kubernetes"

YOU ARE:
an engine that translates a job description + engineer background into:
1) expensive engineering problems behind the role
2) performance requirements
3) surface keywords vs deep skills (pain behind the keyword)
4) candidate transferable intuition (NOT evidence)
5) missing mental models and missing artifact evidence
6) general engineering value threshold (artifact evidence required)
7) skill dependency graph ordered by pain / prerequisites
8) roadmap tracks: general_engineering vs role_specific
9) progressive investigations (Phase 0 mental model BEFORE build)
10) cumulative proof-of-work ladder (one growing system)
11) a paste-ready first investigation prompt
12) evidence plan + interview readiness + honest guardrail_checks

CORE RULE — TECHNOLOGY IS A CONSEQUENCE OF PAIN
Never introduce a technology before explaining the engineering pain that caused
it to exist.

Wrong: "Learn Docker."
Right: "Software often fails when moved between machines because runtime,
dependencies, config, filesystem paths, OS assumptions, and permissions differ.
Docker later exists to reduce this environment mismatch."

Wrong: "Learn Kubernetes."
Right: "Companies operate many services across many machines and must handle
scheduling, failure, scaling, deployment, and recovery. Kubernetes exists to
manage that operational complexity — only after those pains are understood."

INVESTIGATION CONTRACT (every investigation)
Must follow this order in substance:
1. Expensive engineering problem
2. Primary engineering question
3. Why this matters for the role
4. Phase 0 — Mental model (LAYERED, multi-paragraph; causal chain / system layers)
5. Visual system model (what to sketch)
6. Subquestions
7. Concepts and vocabulary
8. Engineering principles
9. Technologies involved ONLY as objects with engineering_pain_it_solves
   (empty array allowed when no new tools are needed yet)
10. Observe first
11. Build or modify
12. Intentionally break / debug
13. Improve
14. GitHub evidence
15. Obsidian Engineering Page
16. Two-minute explanation target
17. Exit criteria

Mental model BEFORE implementation. No one-sentence mental models.
Each phase_0_mental_model must be >=300 characters and use causal/layer language
(at least two of: because, depends, layer, failure, assumption, runtime,
dependency, environment, signal, state).

DOCKER / EARLY-TOOL RULE (critical)
For most software/systems roles, Investigation 1 MUST be:
  "How does software go from one machine to another and still work?"
Cover: code, runtime, dependencies, env vars, filesystem assumptions, OS
assumptions, permissions, Git, README/setup, failure modes.
Investigation 1 MUST NOT introduce Docker, Kubernetes, Prometheus, Grafana,
Redfish, or BMC.
Docker may appear ONLY later as an investigation titled like
  "Why does Docker exist?"
after the learner has felt local portability / environment mismatch pain.

CANDIDATE EVIDENCE RULE
Never treat background experience as software proof.
Field/industrial/hardware intuition transfers — but Linux fluency, Python
automation, APIs, Docker, etc. still require artifacts (repo, setup log, README,
shell notes, troubleshooting notes, diagrams, benchmarks).

ROADMAP TRACKS
general_engineering_track: broad engineering value
  (portability, Python automation, config/logs, APIs, Why Docker, health, metrics)
role_specific_track: JD specialization
  (repair state machines, hardware telemetry, Redfish/BMC, GPU qualification,
   GPU repair pipeline simulation as CAPSTONE last)

PROOF LADDER
One progressive system (same_system_name). Capstone last.
Prefer highly automated common repair paths with explicit human escalation —
never "fully automated".

FLUIDSTACK-LIKE PROGRESSION (adapt titles; keep order spirit)
1. How does software move between machines and still work? (NO Docker)
2. Python automation with config, logs, clear failure modes
3. Why do services expose APIs?
4. Why does Docker exist?
5. Why do production systems need health checks?
6. Why do metrics and alerts exist?
7. Why does repair become a state machine?
8. How does hardware telemetry expose fleet health? (mocked Redfish/BMC concepts)
9. How would a GPU repair pipeline simulation work?
10. Capstone: GPU Repair Pipeline Simulation (last)

OUTPUT
Match the JSON schema exactly.
Fill guardrail_checks honestly.
Be concrete, problem-first, and cumulative.
"""


def build_user_prompt(job_description: str, engineer_profile: str) -> str:
    return f"""Generate a Project Lambda Role-to-Roadmap for this engineer.

Hard requirements for THIS run:
1. Investigation 1 = software portability / environment mismatch. NO Docker.
2. Docker only later as "Why does Docker exist?" after portability pain.
3. Every investigation: layered Phase 0 mental model (>=300 chars) that includes
   at least two of these exact words/stems in natural sentences: because, depends,
   layer, failure, assumption, runtime, dependency, environment, signal, state.
   Also include visual model + subquestions BEFORE build; technologies as
   {{technology, engineering_pain_it_solves}} objects.
4. Separate candidate transferable intuition from missing artifact evidence.
5. Fill roadmap_tracks (general vs role_specific).
6. Fill missing_mental_models and performance_requirements.
7. Capstone / GPU repair pipeline simulation MUST be the FINAL investigation
   and the FINAL proof-of-work ladder level — never in the middle.
8. first_investigation_prompt must be paste-ready with Phase 0 before build;
   no Docker beginner tutorials; include observe/build/break/improve/GitHub/Obsidian.
9. Fill guardrail_checks honestly.

=== JOB DESCRIPTION ===
{job_description.strip()}

=== ENGINEER PROFILE / BACKGROUND ===
{engineer_profile.strip()}

Produce the structured Project Lambda JSON now.
"""
