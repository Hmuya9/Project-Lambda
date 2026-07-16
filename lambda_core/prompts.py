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
                        "fail-closed behavior, explicit repair-pipeline boundaries."
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
                        "Sharp engineering truths of THIS job — not generic summaries. "
                        "Fluidstack-like examples: 'GPU failure is not a ticket; it is a "
                        "fleet throughput problem.'; 'Repair must become a pipeline, not "
                        "a manual procedure.'; 'Health visibility must come from real "
                        "signals, not vibes.'; 'Hardware qualification must define "
                        "production-ready before the fleet goes live.'; 'Automation "
                        "must know when to stop and escalate.'"
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
                        "General-value investigations ONLY. MUST include Docker-style "
                        "work here for software/systems/infrastructure roles "
                        "(not in role_specific). May include: software portability; "
                        "Python automation; config/env; logging/errors; APIs; Why "
                        "Docker exists; health checks; basic metrics. "
                        "FORBIDDEN here: hardware telemetry, Redfish/BMC/IPMI, GPU "
                        "repair/qualification/fleet repair workflows. "
                        "Each entry must correspond to a general-track investigation."
                    ),
                },
                "role_specific_track": {
                    "type": "array",
                    "items": {"type": "string"},
                    "minItems": 3,
                    "maxItems": 10,
                    "description": (
                        "JD-specific investigations ONLY. Fluidstack-like: repair "
                        "state machines; hardware telemetry; Redfish/BMC/IPMI "
                        "concepts (name them explicitly — do not collapse into "
                        "generic 'hardware telemetry'); GPU qualification; fleet "
                        "ops; repair pipeline simulation; incident/postmortem "
                        "verification. Docker is NOT role-specific unless the JD "
                        "treats container infrastructure as a primary duty. "
                        "Each entry must correspond to a role_specific investigation."
                    ),
                },
            },
        },
        "cumulative_system": {
            "type": "object",
            "additionalProperties": False,
            "description": (
                "ONE growing engineering artifact — not many mini-projects. "
                "For Fluidstack-like roles use a role-shaped name like "
                "fleet-repair-lab / gpu-fleet-ops-lab / compute-fleet-health-lab. "
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
                            "Should reflect the matching investigation title/topic."
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
                "Ops credibility metrics for production/GPU infrastructure roles. "
                "Prefer MTTD, MTTR/time to return to service, false positive/negative "
                "rate, repair queue depth, escalation rate, return-to-service pass rate, "
                "telemetry freshness, alert noise rate. "
                "Numeric thresholds invented for the project (e.g. MTTD under 5 min, "
                "MTTR under 30 min) MUST use source=proposed_project_target — they are "
                "NOT stated JD facts unless the exact number appears in the JD."
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

ROADMAP TRACKS
general_engineering_track ONLY:
  portability, Python automation, config/logs, APIs, Why Docker, health checks,
  basic metrics.
role_specific_track ONLY:
  repair state machines, hardware telemetry, Redfish/BMC/IPMI (name explicitly),
  GPU qualification, fleet operations, repair pipeline simulation,
  incident/postmortem verification for fleet failures, CAPSTONE last.
FORBIDDEN: putting hardware telemetry / Redfish / GPU repair / qualification in
the general track.
FORBIDDEN: putting Docker on the role_specific track for typical software/
systems/infrastructure roles.
Every investigation labeled `general` must appear in general_engineering_track.
Every investigation labeled `role_specific` must appear in role_specific_track.

PRESERVE ROLE-SPECIFIC TOOLING (critical)
If the JD mentions Redfish, BMC, IPMI, firmware-level telemetry, or hardware
lifecycle management, the roadmap MUST include an investigation or subquestion
that explicitly names the relevant concept — e.g.
  "How do BMC/Redfish-style interfaces expose hardware state?"
It may be mocked. It does not need real hardware.
Do NOT collapse Redfish/BMC/IPMI into only generic "hardware telemetry."

ROADMAP CONSISTENCY (critical)
These sections MUST agree with each other:
  cumulative_system.repo_growth_model
  investigation_roadmap
  proof_of_work_ladder
  evidence_plan.github_repository.final_folder_structure
  roadmap_tracks
Rules:
- every investigation has a matching repo growth item (same number, title, module)
- every investigation has a matching proof ladder level (same number/module)
- no folder in repo growth unless it appears in the roadmap/ladder
- no roadmap item without a repo growth module
Reject inventing mismatched topics for the same investigation number.

CUMULATIVE SINGLE-SYSTEM RULE (critical)
Do NOT create many mini-repos (Software Portability Repo, Docker Repo, etc.).
Create ONE cumulative system such as:
  fleet-repair-lab / gpu-fleet-ops-lab / compute-fleet-health-lab
Populate cumulative_system with stable system_name + suggested_repo_name and a
repo_growth_model (folder/module + investigation_title each investigation).
proof_of_work_ladder.same_system_name MUST match cumulative_system.system_name
on EVERY level.
Each ladder level adds module_or_folder_added + new_capability_added +
what_new_proof_it_creates + why_this_is_not_a_separate_project.
evidence_plan.github_repository describes ONE repo tree (README, docs/, src/,
tests/, outputs/) — never a list of many repos.
Capstone is the mature version of the SAME repo.

DOCKER MODULE CONSISTENCY
If an investigation is "Why does Docker exist?", cumulative_system.repo_growth_model
AND proof_of_work_ladder MUST include a Docker-related artifact in the SAME repo,
e.g. Dockerfile, docker-compose.yml, docs/docker-portability-notes.md, or
docs/containerization-tradeoffs.md. Never a separate Docker project.

METRIC SOURCE HONESTY (critical)
performance_requirements.source and operational_metrics_contract.source must be
exactly one of:
  stated_in_jd | implied_by_jd | proposed_project_target
Numeric thresholds that do NOT appear in the JD (e.g. MTTD under 5 minutes,
MTTR under 30 minutes for Fluidstack) MUST be proposed_project_target.
Never label model-invented measurements as stated_in_jd / "stated in JD".
Trust is the product. Do not fabricate precision.

OPERATIONAL CREDIBILITY (critical)
Fill role_interpretation.role_signature_claims with sharp role truths (not job
summaries). Example style: "GPU failure is not a ticket; it is a fleet throughput
problem."
Fill operational_metrics_contract with measurable ops metrics (MTTD, MTTR /
return-to-service, FP/FN rates, queue depth, escalation rate, alert noise, etc.)
AND honest source labels.
Fill automation_boundaries: safe_to_automate, requires_human_escalation,
fail_closed_conditions, manual_approval_gates.
Fill capstone_proof_contract with failure injections, MTTD/MTTR measurements,
verification/postmortem docs, and a hiring_manager_readout.
FORBIDDEN absolute automation language anywhere:
  "fully automated", "no humans needed", "complete automation", "automated everything"
REQUIRED framing instead:
  common-path automation, escalation for unsafe/ambiguous states, human review
  gates, fail-closed behavior, repair pipeline with explicit boundaries.

NO FAKE ACCOMPLISHMENT LANGUAGE (critical)
Project Lambda generates a roadmap, not fake achievements.
capstone_proof_contract and hiring_manager_readout MUST NOT claim the user
already achieved results.
FORBIDDEN unless clearly framed as a future target/template:
  "I successfully validated", "MTTD was consistently under",
  "MTTR was maintained below", "I built", "I proved"
REQUIRED framing:
  "After completing this capstone, the candidate should be able to say…"
  "Target measurement…"
  "Evidence to produce…"
  "The final readout should include…"

FLUIDSTACK-LIKE PROGRESSION (adapt titles; keep order spirit)
1. How does software move between machines and still work? (NO Docker)
   → concrete machine-report project [general]
2. Python automation with config, logs, clear failure modes [general]
3. Why do services expose APIs? [general]
4. Why does Docker exist? [general] + Dockerfile (or equivalent) in same repo
5. Why do production systems need health checks? [general]
6. Why do metrics and alerts exist? [general]
7. Why does repair become a state machine? [role_specific]
8. How do BMC/Redfish-style interfaces expose hardware state?
   (or equivalent explicit BMC/Redfish/IPMI investigation) [role_specific]
9. How would a GPU repair pipeline simulation work? [role_specific]
10. Capstone verification + incident/postmortem evidence on SAME repo
    [role_specific] — future-facing proof contract only

OUTPUT
Match the JSON schema exactly.
Fill guardrail_checks honestly.
Be concrete, problem-first, cumulative, consistent across sections, and
hiring-manager credible without fabricating completed results.
"""


def build_user_prompt(job_description: str, engineer_profile: str) -> str:
    return f"""Generate a Project Lambda Role-to-Roadmap for this engineer.

Hard requirements for THIS run:
1. Investigation 1 = software portability / environment mismatch via a concrete
   machine-report project (Python version check, APP_ENV, one dependency,
   output/report.txt, logging, clear config failure, README, failure log,
   assumptions table). NO Docker. NO vague "create a simple application."
2. Docker only later as "Why does Docker exist?" after portability pain. Docker
   is GENERAL track (not role_specific) unless the JD treats container
   infrastructure as a primary role-specific duty. If Docker investigation
   exists, add Dockerfile (or docker-compose / docker docs) to the SAME
   cumulative repo growth model and proof ladder.
3. EVERY investigation (including Capstone): Phase 0 mental model (>=300 chars)
   that literally uses at least two of these exact words: because, depends,
   layer, failure, assumption, runtime, dependency, environment, signal, state.
   visual_system_model >=80 chars with boxes/arrows/layers.
4. role_signature_claims: >=4 sharp engineering truths (not generic summaries).
5. NEVER say fully automated / no humans needed / complete automation /
   automated everything. Use common-path automation + escalation + fail-closed.
6. Fill operational_metrics_contract (include MTTD and MTTR or return-to-service)
   with source exactly one of: stated_in_jd | implied_by_jd |
   proposed_project_target. Invented numeric thresholds (e.g. MTTD <5 min,
   MTTR <30 min) MUST be proposed_project_target — never stated_in_jd.
   Same honesty for performance_requirements.source.
7. Fill automation_boundaries (safe / escalate / fail-closed / approval gates).
8. Fill capstone_proof_contract with failure injections, MTTD/MTTR measurements,
   verification + postmortem docs, hiring_manager_readout. Readout MUST be
   future-facing ("After completing…", "Target…", "Evidence to produce…") —
   NEVER fake past-tense success ("I built", "I proved", "MTTD was under…").
9. ONE cumulative system; stable same_system_name; one github_repository with a
   multi-line final_folder_structure tree (>=80 chars showing README/docs/src/
   Dockerfile/tests/outputs).
10. ROADMAP CONSISTENCY: repo_growth_model, investigation_roadmap,
    proof_of_work_ladder, final_folder_structure, and roadmap_tracks MUST agree.
    Same investigation numbers, titles, and modules. Growth count = ladder
    count = investigation count. Every growth folder appears in roadmap/ladder.
    module_or_folder_added must be a SPECIFIC path identical across roadmap,
    growth, and ladder (e.g. src/machine_report.py) — NEVER vague 'src/' alone.
11. Capstone LAST with real proof beyond prior integration. The FINAL
    investigation title should include Capstone/verification/postmortem language.
    A mid/late 'GPU repair pipeline simulation' investigation may exist BEFORE
    the final Capstone, but only the LAST item gets a real capstone_delta.
    Final capstone_delta MUST literally mention: failure injection, MTTD, MTTR
    (or return-to-service), and postmortem/verification. Non-final use
    'n/a — not the capstone'.
12. first_investigation_prompt paste-ready with Phase 0 / mental model / observe /
    build / break / improve / GitHub / Obsidian / commands / exit criteria;
    names machine-report; no Docker.
13. If the JD mentions Redfish, BMC, IPMI, or firmware-level telemetry, include
    an explicit role_specific investigation or subquestion naming that concept
    (do not collapse to only "hardware telemetry").
14. Track discipline: general investigations appear in general_engineering_track;
    role_specific ones appear in role_specific_track.
15. Fill guardrail_checks honestly.

=== JOB DESCRIPTION ===
{job_description.strip()}

=== ENGINEER PROFILE / BACKGROUND ===
{engineer_profile.strip()}

Produce the structured Project Lambda JSON now.
"""
