"""Prompt templates and output schema for Project Lambda Role-to-Roadmap generation.

Iterate product behavior here — keep CLI/UI wrappers stable.
"""

from __future__ import annotations

CONTRACT_JSON_SCHEMA: dict = {
    "type": "object",
    "additionalProperties": False,
    "required": [
        "role_family",
        "role_interpretation",
        "expensive_problem_map",
        "performance_requirements",
        "surface_keywords_vs_deep_skills",
        "candidate_transfer_map",
        "missing_mental_models",
        "general_engineering_value_threshold",
        "skill_dependency_graph",
        "roadmap_tracks",
        "cumulative_system",
        "investigation_roadmap",
        "proof_of_work_ladder",
        "first_investigation_prompt",
        "evidence_plan",
        "operational_metrics_contract",
        "automation_boundaries",
        "capstone_proof_contract",
        "interview_readiness_map",
        "guardrail_checks",
    ],
    "properties": {
        "role_family": {
            "type": "object",
            "additionalProperties": False,
            "description": (
                "Classify the role FIRST. Role-specific investigations, cumulative "
                "system name, metrics, and capstone MUST follow this family. "
                "Do NOT default to GPU fleet repair / BMC / Redfish unless the JD "
                "explicitly supports that family."
            ),
            "required": [
                "primary_family",
                "secondary_families",
                "why_this_family",
                "excluded_families",
            ],
            "properties": {
                "primary_family": {
                    "type": "string",
                    "description": (
                        "Exactly one of: ai_infrastructure_model_serving | "
                        "gpu_fleet_production_engineering | "
                        "backend_platform_engineering | robotics_systems | "
                        "embedded_ai | cloud_infrastructure | "
                        "controls_automation_software | "
                        "data_center_compute_infrastructure | "
                        "general_systems_software"
                    ),
                },
                "secondary_families": {
                    "type": "array",
                    "items": {"type": "string"},
                },
                "why_this_family": {
                    "type": "string",
                    "description": "Cite JD evidence for the chosen family.",
                },
                "excluded_families": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": (
                        "Families that would be a misread of this JD "
                        "(e.g. exclude gpu_fleet_production_engineering for a "
                        "model-serving AI infra role)."
                    ),
                },
            },
        },
        "role_interpretation": {
            "type": "object",
            "additionalProperties": False,
            "required": [
                "one_liner",
                "real_mission",
                "what_success_looks_like",
                "what_this_role_is_not",
                "role_signature_claims",
            ],
            "properties": {
                "one_liner": {"type": "string"},
                "real_mission": {"type": "string"},
                "what_success_looks_like": {
                    "type": "string",
                    "description": (
                        "FORBIDDEN: 'fully automated', 'no humans needed', "
                        "'complete automation', 'automated everything'. "
                        "REQUIRED framing: common-path automation with escalation "
                        "for unsafe/ambiguous states, human review gates, "
                        "fail-closed behavior, and explicit operational boundaries "
                        "appropriate to the role family."
                    ),
                },
                "what_this_role_is_not": {
                    "type": "array",
                    "items": {"type": "string"},
                    "minItems": 2,
                    "maxItems": 6,
                },
                "role_signature_claims": {
                    "type": "array",
                    "minItems": 4,
                    "maxItems": 8,
                    "description": (
                        "Sharp engineering truths of THIS job and role family — not "
                        "generic summaries and not copied from a different family. "
                        "Fleet/repair examples only when JD supports fleet repair. "
                        "Model-serving examples: 'Inference latency is a product "
                        "feature, not a nice-to-have.'; 'Batching improves throughput "
                        "but can hurt tail latency.'; 'GPU utilization without SLO "
                        "discipline is a false win.'; 'Observability must expose queue "
                        "depth, token throughput, and cold starts — not vibes.'"
                    ),
                    "items": {"type": "string"},
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
                            "Exactly one of: 'stated_in_jd' | 'implied_by_jd' | "
                            "'proposed_project_target'. "
                            "Numeric thresholds (e.g. MTTD under 5 minutes) that are NOT "
                            "literally in the JD MUST be proposed_project_target — never "
                            "stated_in_jd. Trust is the product; do not fabricate precision."
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
                        "SHORT TITLES ONLY — exact copies of investigation_roadmap "
                        "titles where track='general'. No paragraphs. No extras. "
                        "Every general investigation title must appear exactly once."
                    ),
                },
                "role_specific_track": {
                    "type": "array",
                    "items": {"type": "string"},
                    "minItems": 3,
                    "maxItems": 10,
                    "description": (
                        "SHORT TITLES ONLY — exact copies of investigation_roadmap "
                        "titles where track='role_specific'. No paragraphs. No "
                        "extras. Role-specific titles MUST match the chosen "
                        "role_family (model serving vs fleet repair). Docker is NOT "
                        "role-specific unless the JD treats container infrastructure "
                        "as a primary duty. BMC/Redfish/GPU repair titles ONLY when "
                        "the JD explicitly supports them."
                    ),
                },
            },
        },
        "cumulative_system": {
            "type": "object",
            "additionalProperties": False,
            "description": (
                "ONE growing engineering artifact — not many mini-projects. "
                "Name MUST match role_family: "
                "ai_infrastructure_model_serving → ai-inference-reliability-lab / "
                "model-serving-ops-lab / inference-platform-lab; "
                "gpu_fleet_production_engineering → fleet-repair-lab / "
                "gpu-fleet-ops-lab / compute-fleet-health-lab. "
                "FORBIDDEN: defaulting every AI job to fleet-repair. "
                "FORBIDDEN names: Software Portability, Python Automation, "
                "Docker Project, API Project."
            ),
            "required": [
                "system_name",
                "system_purpose",
                "why_this_system_matches_the_role",
                "starting_scope",
                "final_capstone_shape",
                "suggested_repo_name",
                "repo_growth_model",
            ],
            "properties": {
                "system_name": {"type": "string"},
                "system_purpose": {"type": "string"},
                "why_this_system_matches_the_role": {"type": "string"},
                "starting_scope": {"type": "string"},
                "final_capstone_shape": {"type": "string"},
                "suggested_repo_name": {
                    "type": "string",
                    "description": "Same identity as system_name (kebab-case repo).",
                },
                "repo_growth_model": {
                    "type": "array",
                    "minItems": 5,
                    "maxItems": 12,
                    "description": (
                        "MUST have exactly one entry per investigation, same count "
                        "as investigation_roadmap. investigation_number, "
                        "investigation_title, and folder_or_module_added MUST match "
                        "the corresponding investigation's index, title, and "
                        "module_or_folder_added. Do NOT invent a different topic "
                        "for the same investigation number (e.g. growth saying "
                        "Inv 3 is observability while roadmap says Inv 3 is APIs)."
                    ),
                    "items": {
                        "type": "object",
                        "additionalProperties": False,
                        "required": [
                            "investigation_number",
                            "investigation_title",
                            "folder_or_module_added",
                            "capability_added",
                            "why_it_matters",
                            "evidence_created",
                        ],
                        "properties": {
                            "investigation_number": {"type": "integer"},
                            "investigation_title": {
                                "type": "string",
                                "description": (
                                    "Must match investigation_roadmap[N-1].title."
                                ),
                            },
                            "folder_or_module_added": {
                                "type": "string",
                                "description": (
                                    "Must match that investigation's "
                                    "module_or_folder_added "
                                    "(e.g. src/machine_report.py or src/api/)."
                                ),
                            },
                            "capability_added": {"type": "string"},
                            "why_it_matters": {"type": "string"},
                            "evidence_created": {"type": "string"},
                        },
                    },
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
                    "module_or_folder_added",
                    "delta_from_previous_investigation",
                    "capstone_delta",
                ],
                "properties": {
                    "title": {"type": "string"},
                    "track": {
                        "type": "string",
                        "description": (
                            "Exactly 'general' or 'role_specific'. "
                            "Hardware telemetry / Redfish / BMC / GPU repair / "
                            "qualification / fleet repair MUST be role_specific."
                        ),
                    },
                    "expensive_problem": {"type": "string"},
                    "engineering_question": {"type": "string"},
                    "why_matters_for_role": {"type": "string"},
                    "phase_0_mental_model": {
                        "type": "string",
                        "description": (
                            "MULTI-PARAGRAPH / LAYERED (>=300 chars). Explain system "
                            "layers or causal chain the learner must picture. MUST "
                            "literally include at least two of these words in the text: "
                            "because, depends, layer, failure, assumption, runtime, "
                            "dependency, environment, signal, state. Example opener: "
                            "'This depends on a stack of assumptions at each layer; "
                            "failure happens because the environment or runtime differs.' "
                            "Forbidden: one-sentence slogans. Applies to EVERY "
                            "investigation including Capstone."
                        ),
                    },
                    "visual_system_model": {
                        "type": "string",
                        "description": (
                            "Describe a diagram the learner should sketch "
                            "(boxes, arrows, failure points). >=80 characters."
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
                    "artifact_this_investigation_produces": {
                        "type": "string",
                        "description": (
                            "Must be a module/folder/file INSIDE the one cumulative "
                            "repo — not a new separate repository."
                        ),
                    },
                    "module_or_folder_added": {
                        "type": "string",
                        "description": (
                            "SPECIFIC path added to the cumulative repo this "
                            "investigation — must exactly match "
                            "repo_growth_model.folder_or_module_added and the "
                            "matching proof_of_work_ladder.module_or_folder_added. "
                            "Examples: src/machine_report.py, src/api/, Dockerfile, "
                            "docs/verification-log.md. FORBIDDEN: vague paths like "
                            "src/ or docs/ alone."
                        ),
                    },
                    "delta_from_previous_investigation": {
                        "type": "string",
                        "description": (
                            "For Investigation 1: 'none — starting investigation'. "
                            "Otherwise: what NEW proof/capability this adds vs previous."
                        ),
                    },
                    "capstone_delta": {
                        "type": "string",
                        "description": (
                            "For final investigation ONLY: must literally include "
                            "'failure injection' and 'MTTD' and 'MTTR' (or "
                            "'return-to-service') and 'postmortem' or 'verification'. "
                            "Explain NEW proof beyond prior integration. "
                            "For non-final: 'n/a — not the capstone'."
                        ),
                    },
                },
            },
        },
        "proof_of_work_ladder": {
            "type": "array",
            "minItems": 5,
            "maxItems": 12,
            "description": (
                "ONE progressive system that grows. Count MUST equal "
                "investigation_roadmap length. level N maps to investigation N; "
                "module_or_folder_added MUST match that investigation. "
                "same_system_name MUST match cumulative_system.system_name on EVERY "
                "level. Capstone is LAST. NOT separate projects."
            ),
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": [
                    "level",
                    "title",
                    "same_system_name",
                    "module_or_folder_added",
                    "extends_previous",
                    "new_capability_added",
                    "what_new_proof_it_creates",
                    "why_this_is_not_a_separate_project",
                    "evidence",
                    "connected_investigations",
                ],
                "properties": {
                    "level": {"type": "integer"},
                    "title": {
                        "type": "string",
                        "description": (
                            "MUST exactly equal investigation_roadmap[level-1].title."
                        ),
                    },
                    "same_system_name": {
                        "type": "string",
                        "description": "Identical across all levels; role-shaped name.",
                    },
                    "module_or_folder_added": {
                        "type": "string",
                        "description": (
                            "Must match investigation_roadmap[level-1]."
                            "module_or_folder_added."
                        ),
                    },
                    "extends_previous": {"type": "string"},
                    "new_capability_added": {"type": "string"},
                    "what_new_proof_it_creates": {"type": "string"},
                    "why_this_is_not_a_separate_project": {"type": "string"},
                    "evidence": {
                        "type": "array",
                        "items": {"type": "string"},
                        "minItems": 1,
                    },
                    "connected_investigations": {
                        "type": "array",
                        "items": {"type": "string"},
                        "minItems": 1,
                        "description": (
                            "MUST include this level's own investigation title "
                            "(investigation_roadmap[level-1].title). Do not point "
                            "only at the next investigation."
                        ),
                    },
                },
            },
        },
        "first_investigation_prompt": {
            "type": "object",
            "additionalProperties": False,
            "description": (
                "Paste-ready Investigation 1. For software/systems roles: a concrete "
                "portability project named machine-report (NOT a vague 'create a "
                "simple application'). FORBIDDEN: Docker, K8s, Prometheus, Grafana, "
                "Redfish in this prompt."
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
                        "Complete multi-section prompt. MUST literally include "
                        "section headings containing: 'Phase 0', 'mental model', "
                        "'observe', 'build', 'break', 'improve', 'GitHub', "
                        "'Obsidian', plus commands to run, what to break, what to "
                        "write in Obsidian, GitHub evidence, and exit criteria. "
                        "MUST name the concrete project 'machine-report' (or "
                        "machine_report) that: checks Python version; reads one "
                        "required env var (e.g. APP_ENV); uses one external "
                        "dependency; writes output/report.txt; logs what it is "
                        "doing; fails clearly when required config is missing; "
                        "includes README setup; includes a failure log; includes "
                        "an assumptions table. Forbidden: vague language like "
                        "'create a simple application' without the concrete "
                        "machine-report spec. Must not recommend Docker."
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
                "build_or_modify": {
                    "type": "string",
                    "description": (
                        "Must specify the concrete machine-report project "
                        "(Python version check, APP_ENV, one dependency, "
                        "output/report.txt, logging, clear config failure)."
                    ),
                },
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
            "description": (
                "ONE primary GitHub repository with folders/modules — never many "
                "disconnected repos."
            ),
            "required": [
                "obsidian_pages",
                "github_repository",
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
                "github_repository": {
                    "type": "object",
                    "additionalProperties": False,
                    "required": [
                        "repo_name",
                        "repo_purpose",
                        "final_folder_structure",
                        "evidence_files",
                    ],
                    "properties": {
                        "repo_name": {
                            "type": "string",
                            "description": "Must match cumulative_system.suggested_repo_name.",
                        },
                        "repo_purpose": {"type": "string"},
                        "final_folder_structure": {
                            "type": "string",
                            "description": (
                                "Multi-line text tree of the ONE repo (>=80 chars), e.g. "
                                "fleet-repair-lab/\\n├── README.md\\n├── docs/\\n├── src/\\n"
                                "├── Dockerfile\\n├── tests/\\n└── outputs/. "
                                "Not a list of multiple repos."
                            ),
                        },
                        "evidence_files": {
                            "type": "array",
                            "items": {"type": "string"},
                            "minItems": 6,
                            "description": (
                                "Include README.md, docs/architecture.md, "
                                "docs/failure-log.md, docs/verification-log.md, "
                                "docs/incident-postmortem.md, outputs/, tests/, src/ paths."
                            ),
                        },
                    },
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
                    "description": (
                        "Prefer ops-credible: failure injection log, MTTD/MTTR, "
                        "alert trigger log, return-to-service verification."
                    ),
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
        "operational_metrics_contract": {
            "type": "array",
            "minItems": 5,
            "maxItems": 12,
            "description": (
                "Ops metrics measurable INSIDE the cumulative project. "
                "Match role_family: model serving → request count, error rate, "
                "P50/P95/P99 latency, throughput req/s, queue depth, batch size, "
                "simulated GPU utilization, CPU/memory, cold start, MTTD/MTTR for "
                "simulated service incidents, alert noise. "
                "Fleet repair → MTTD, MTTR/return-to-service, FP/FN, telemetry "
                "freshness, repair queue depth, escalation rate, RTS pass rate. "
                "FORBIDDEN as proposed project metrics unless JD+project support a "
                "proxy: user/customer satisfaction, revenue impact, broad business "
                "KPIs, six-month org targets. "
                "Invented numeric thresholds MUST use proposed_project_target."
            ),
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": [
                    "metric",
                    "source",
                    "why_it_matters",
                    "how_to_measure_in_the_project",
                    "what_bad_result_means",
                ],
                "properties": {
                    "metric": {"type": "string"},
                    "source": {
                        "type": "string",
                        "description": (
                            "Exactly one of: 'stated_in_jd' | 'implied_by_jd' | "
                            "'proposed_project_target'. Reject inventing 'stated in JD' "
                            "labels for model-invented measurements."
                        ),
                    },
                    "why_it_matters": {"type": "string"},
                    "how_to_measure_in_the_project": {"type": "string"},
                    "what_bad_result_means": {"type": "string"},
                },
            },
        },
        "automation_boundaries": {
            "type": "object",
            "additionalProperties": False,
            "description": (
                "Explicit judgment about what the cumulative system may automate vs "
                "must escalate. Required for production/ops roles."
            ),
            "required": [
                "safe_to_automate",
                "requires_human_escalation",
                "fail_closed_conditions",
                "manual_approval_gates",
            ],
            "properties": {
                "safe_to_automate": {
                    "type": "array",
                    "items": {"type": "string"},
                    "minItems": 3,
                },
                "requires_human_escalation": {
                    "type": "array",
                    "items": {"type": "string"},
                    "minItems": 3,
                },
                "fail_closed_conditions": {
                    "type": "array",
                    "items": {"type": "string"},
                    "minItems": 2,
                },
                "manual_approval_gates": {
                    "type": "array",
                    "items": {"type": "string"},
                    "minItems": 2,
                },
            },
        },
        "capstone_proof_contract": {
            "type": "object",
            "additionalProperties": False,
            "description": (
                "Capstone must prove readiness — not 'integrate everything'. "
                "Must cover failure injection, verification logs, MTTD/MTTR, "
                "escalation cases, FP/FN notes, postmortem, README, architecture "
                "diagram, two-minute hiring-manager explanation. "
                "CRITICAL: Project Lambda generates a ROADMAP, not fake achievements. "
                "hiring_manager_readout and measurement language MUST be "
                "future-facing / template language — never claim the user already "
                "achieved results."
            ),
            "required": [
                "what_it_must_demonstrate",
                "required_failure_injections",
                "required_measurements",
                "required_docs",
                "hiring_manager_readout",
            ],
            "properties": {
                "what_it_must_demonstrate": {
                    "type": "array",
                    "items": {"type": "string"},
                    "minItems": 4,
                },
                "required_failure_injections": {
                    "type": "array",
                    "items": {"type": "string"},
                    "minItems": 3,
                },
                "required_measurements": {
                    "type": "array",
                    "items": {"type": "string"},
                    "minItems": 3,
                    "description": (
                        "Must include MTTD and MTTR (or time-to-return-to-service). "
                        "Frame as targets/evidence to produce — not past achievements."
                    ),
                },
                "required_docs": {
                    "type": "array",
                    "items": {"type": "string"},
                    "minItems": 4,
                    "description": (
                        "Include verification log, incident postmortem, README tradeoff "
                        "section, architecture diagram note."
                    ),
                },
                "hiring_manager_readout": {
                    "type": "string",
                    "description": (
                        "Future-facing two-minute template. REQUIRED framing like: "
                        "'After completing this capstone, the candidate should be able "
                        "to say…', 'Target measurement…', 'Evidence to produce…', "
                        "'The final readout should include…'. "
                        "FORBIDDEN past-tense fake success: 'I successfully validated', "
                        "'MTTD was consistently under', 'MTTR was maintained below', "
                        "'I built', 'I proved' — unless clearly marked as a future "
                        "script the candidate will use after finishing the work."
                    ),
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
                "one_cumulative_system_not_many_repos",
                "avoids_blind_full_automation_language",
                "has_operational_metrics_and_automation_boundaries",
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
                "one_cumulative_system_not_many_repos": {"type": "boolean"},
                "avoids_blind_full_automation_language": {"type": "boolean"},
                "has_operational_metrics_and_automation_boundaries": {
                    "type": "boolean",
                },
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
- a fabricator of fake completed achievements or fake JD precision

YOU ARE:
an engine that translates a job description + engineer background into:
0) role_family classification (FIRST — routes everything else)
1) expensive engineering problems behind the role
2) performance requirements (with honest source labels)
3) surface keywords vs deep skills (pain behind the keyword)
4) candidate transferable intuition (NOT evidence)
5) missing mental models and missing artifact evidence
6) general engineering value threshold (artifact evidence required)
7) skill dependency graph ordered by pain / prerequisites
8) roadmap tracks: general_engineering vs role_specific
9) progressive investigations (Phase 0 mental model BEFORE build)
10) cumulative proof-of-work ladder (one growing system)
11) a paste-ready first investigation prompt (concrete machine-report)
12) evidence plan + interview readiness + honest guardrail_checks

CRITICAL ANTI-OVERFIT RULE
Do NOT default every AI / GPU job to Fluidstack-style fleet repair,
BMC/Redfish, hardware RMA, or GPU repair pipeline simulation.
Classify role_family from the JD, then generate role-specific work for THAT family.

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
dependency, environment, signal, state). EVERY investigation including mid
and capstone must satisfy this — no exceptions for later investigations.
Each visual_system_model must be >=80 characters and describe boxes/arrows/
layers/failure points to sketch.

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
Docker belongs on the GENERAL engineering track for software/systems/
infrastructure roles — NOT role_specific — unless the JD specifically treats
container infrastructure as a primary role-specific duty.

INVESTIGATION 1 — CONCRETE machine-report PROJECT (critical)
Do NOT say vague things like "create a simple application."
Default concrete project for software/systems roles:

  Project: machine-report

It must:
- check Python version
- read one required environment variable (e.g. APP_ENV)
- use one external dependency
- write output/report.txt
- log what it is doing
- fail clearly when required configuration is missing
- include README setup instructions
- include a failure log
- include an assumptions table

first_investigation_prompt.ready_to_paste_prompt MUST include:
Phase 0 mental model, visual model, exact small project, commands to run,
what to break, what to write in Obsidian, GitHub evidence, exit criteria.

CANDIDATE EVIDENCE RULE
Never treat background experience as software proof.
Field/industrial/hardware intuition transfers — but Linux fluency, Python
automation, APIs, Docker, etc. still require artifacts (repo, setup log, README,
shell notes, troubleshooting notes, diagrams, benchmarks).

ROLE FAMILY CLASSIFICATION (do this first)
Fill role_family.primary_family with exactly one allowed value:
  ai_infrastructure_model_serving
  gpu_fleet_production_engineering
  backend_platform_engineering
  robotics_systems
  embedded_ai
  cloud_infrastructure
  controls_automation_software
  data_center_compute_infrastructure
  general_systems_software

Routing evidence:
- Mentions model serving / inference / vLLM / Triton / latency budgets /
  token throughput / $/token / cold starts → ai_infrastructure_model_serving
- Mentions repair pipeline / RMA / return to service / BMC / Redfish / IPMI /
  firmware telemetry / bare metal lifecycle / hardware qualification /
  physical fleet repair → gpu_fleet_production_engineering
Do NOT pick gpu_fleet_production_engineering merely because GPUs appear.

ROLE-FAMILY ROLE-SPECIFIC ROUTING
If primary_family = ai_infrastructure_model_serving, role-specific work should
usually include several of:
  How does an AI model become a service?
  Why do inference systems care about latency and throughput?
  Why do batching and queues improve throughput but hurt latency?
  How do we measure P50/P95/P99 latency?
  How do model-serving systems fail under load?
  How do we observe an inference service?
  How do CPU/GPU resource constraints affect inference?
  How do we load test and diagnose bottlenecks?
  Capstone: Local Inference Service Reliability Lab
Cumulative system names like:
  ai-inference-reliability-lab / model-serving-ops-lab / inference-platform-lab
FORBIDDEN unless JD explicitly supports fleet/hardware repair:
  GPU repair pipeline simulation, BMC/Redfish/IPMI, hardware fleet repair,
  repair state machines, RMA automation.

If primary_family = gpu_fleet_production_engineering, role-specific work may
include:
  repair state machines; BMC/Redfish/IPMI (named explicitly); hardware
  telemetry; GPU qualification; repair pipeline simulation; fleet health;
  incident/postmortem verification.
Cumulative system names like:
  fleet-repair-lab / gpu-fleet-ops-lab / compute-fleet-health-lab

PRESERVE ROLE-SPECIFIC TOOLING ONLY WHEN JD SUPPORTS IT
If AND ONLY IF the JD mentions Redfish, BMC, IPMI, firmware-level telemetry,
hardware lifecycle, RMA, repair pipeline, or physical fleet operations, include
an investigation/subquestion that explicitly names the concept.
If the JD does NOT mention those, do NOT invent BMC/Redfish/GPU repair tracks.

ROADMAP TRACKS (exact title matching)
roadmap_tracks.*. entries MUST be SHORT TITLES ONLY (no paragraphs).
Each general_engineering_track title MUST exactly equal one investigation
title with track=general.
Each role_specific_track title MUST exactly equal one investigation title
with track=role_specific.
Every investigation title appears in exactly one track. No extras.
FORBIDDEN: putting Docker on role_specific for typical software/systems roles.

ROADMAP CONSISTENCY (critical)
These sections MUST agree:
  cumulative_system.repo_growth_model
  investigation_roadmap
  proof_of_work_ladder
  evidence_plan.github_repository.final_folder_structure
  roadmap_tracks
Rules:
- every investigation has matching repo growth item (number, title, module)
- every investigation has matching proof ladder level
- proof_of_work_ladder[i].title == investigation_roadmap[i].title
- proof_of_work_ladder[i].connected_investigations includes that same title
- no folder in repo growth unless it appears in roadmap/ladder

CUMULATIVE SINGLE-SYSTEM RULE (critical)
ONE cumulative system named for the role_family (see above).
NOT many mini-repos. Capstone is the mature version of the SAME repo.
proof_of_work_ladder.same_system_name MUST match cumulative_system.system_name.

DOCKER MODULE CONSISTENCY
If an investigation is "Why does Docker exist?", add Dockerfile /
docker-compose / docker docs to the SAME repo growth model and proof ladder.

METRIC SOURCE + MEASURABILITY (critical)
source must be stated_in_jd | implied_by_jd | proposed_project_target.
Invented numeric thresholds → proposed_project_target.
Proposed metrics MUST be measurable by the cumulative project artifacts.
Prefer family-appropriate metrics (latency/throughput for serving; MTTD/MTTR/
return-to-service for fleet repair).
FORBIDDEN proposed metrics: user/customer satisfaction, revenue impact, broad
business KPIs, six-month org targets — unless JD states them AND the project
has an explicit simulation/proxy.

MISSING MENTAL MODEL MAPPING
missing_mental_models[].first_investigation_that_builds_it MUST name an
investigation title that actually builds that model.
Observability/metrics/alerting models must NOT point at the API investigation;
point at health checks / metrics & alerts / inference observability instead.

OPERATIONAL CREDIBILITY
Fill role_signature_claims with sharp truths for THIS family.
Fill automation_boundaries and capstone_proof_contract.
FORBIDDEN absolute automation language:
  "fully automated", "no humans needed", "complete automation", "automated everything"
Use common-path automation + escalation + fail-closed + human review gates.

NO FAKE ACCOMPLISHMENT LANGUAGE
Capstone readout is future-facing / template language only.

GENERAL FOUNDATION (most software/systems roles)
1. How does software move between machines and still work? (machine-report, NO Docker) [general]
2. Python automation with config, logs, clear failure modes [general]
3. Why do services expose APIs? [general]
4. Why does Docker exist? [general] + Dockerfile in same repo
5. Why do production systems need health checks? [general]
6. Why do metrics and alerts exist? [general]
Then ROLE-SPECIFIC investigations for the chosen family (NOT always fleet repair).

AI INFRA / MODEL SERVING ROLE-SPECIFIC EXAMPLE (when family matches)
7. How does an AI model become a service?
8. Why do inference systems care about latency and throughput?
9. Why do batching and queues improve throughput but hurt latency?
10. Capstone: Local Inference Service Reliability Lab
    (API works, load test, P50/P95/P99, throughput, error rate, metrics,
     failure injection, postmortem, latency/throughput tradeoff README)

GPU FLEET PRODUCTION ENGINEERING EXAMPLE (only when JD supports it)
7. Why does repair become a state machine?
8. How do BMC/Redfish-style interfaces expose hardware state?
9. How would a GPU repair pipeline simulation work?
10. Capstone: GPU Fleet Repair / Health Simulation

OUTPUT
Match the JSON schema exactly.
Fill guardrail_checks honestly.
Be concrete, problem-first, family-correct, cumulative, and credible.
"""


def build_user_prompt(job_description: str, engineer_profile: str) -> str:
    return f"""Generate a Project Lambda Role-to-Roadmap for this engineer.

Hard requirements for THIS run:
0. FIRST fill role_family. Classify from the JD. Do NOT default to
   gpu_fleet_production_engineering just because GPUs appear. Model serving /
   inference / latency / throughput JDs → ai_infrastructure_model_serving.
   Repair/RMA/BMC/Redfish/fleet hardware JDs → gpu_fleet_production_engineering.
1. Investigation 1 = software portability via concrete machine-report
   (Python version, APP_ENV, one dependency, output/report.txt, logging,
   clear config failure, README, failure log, assumptions table). NO Docker.
2. Docker later as "Why does Docker exist?" on GENERAL track (+ Dockerfile in
   same repo) unless JD makes containers a primary role-specific duty.
3. Role-specific investigations MUST match role_family. For
   ai_infrastructure_model_serving: model serving / inference latency /
   throughput / batching / queues / observability / load testing — NOT
   BMC/Redfish/GPU repair unless JD explicitly mentions those.
4. Cumulative system name MUST match family (inference/model-serving lab vs
   fleet-repair lab). Capstone shape MUST match family.
5. EVERY investigation: Phase 0 mental model (>=300 chars) with >=2 of:
   because, depends, layer, failure, assumption, runtime, dependency,
   environment, signal, state. visual_system_model >=80 chars.
6. role_signature_claims: >=4 sharp truths for THIS family.
7. NEVER say fully automated / no humans needed / complete automation /
   automated everything.
8. operational_metrics_contract: honest source labels; proposed metrics must be
   project-measurable (latency/throughput/error rate/queue depth/MTTD/MTTR…).
   No user-satisfaction/revenue/six-month business KPIs as proposed metrics.
9. automation_boundaries + future-facing capstone_proof_contract.
10. ROADMAP CONSISTENCY: growth/ladder/investigations same count, titles, modules.
    roadmap_tracks titles are SHORT and EXACT copies of investigation titles
    (general↔general, role_specific↔role_specific). No extras, no paragraphs.
11. proof_of_work_ladder[i].title == investigation_roadmap[i].title AND
    connected_investigations includes that same title.
12. missing_mental_models[].first_investigation_that_builds_it must point at an
    investigation that actually builds it (observability ≠ API investigation).
13. If JD mentions Redfish/BMC/IPMI/firmware telemetry/repair/RMA/fleet hardware,
    include explicit coverage. If not, do NOT invent it.
14. Capstone LAST with family-correct proof. Final capstone_delta mentions
    failure injection + measurements + postmortem/verification.
15. Fill guardrail_checks honestly.

=== JOB DESCRIPTION ===
{job_description.strip()}

=== ENGINEER PROFILE / BACKGROUND ===
{engineer_profile.strip()}

Produce the structured Project Lambda JSON now.
"""
