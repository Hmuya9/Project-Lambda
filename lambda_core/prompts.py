"""Prompt templates and output schema for Role-to-Roadmap generation.

Improve the product by iterating here — keep the CLI and I/O layers stable.
"""

from __future__ import annotations

CONTRACT_JSON_SCHEMA: dict = {
    "type": "object",
    "additionalProperties": False,
    "required": [
        "role_interpretation",
        "expensive_problem_map",
        "surface_keywords_vs_deep_skills",
        "candidate_background_translation",
        "general_value_threshold",
        "skill_dependency_graph",
        "investigation_roadmap",
        "proof_of_work_ladder",
        "first_investigation_prompt",
        "evidence_plan",
        "interview_readiness_map",
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
                "one_liner": {
                    "type": "string",
                    "description": "Sharp, job-specific one-liner — not a generic infra slogan.",
                },
                "real_mission": {
                    "type": "string",
                    "description": "What expensive outcomes this hire exists to own.",
                },
                "what_success_looks_like": {
                    "type": "string",
                    "description": (
                        "Grounded in the JD. Do not invent employer metrics; "
                        "if proposing bars, label as proposed. "
                        "Never say 'fully automated' — prefer highly automated "
                        "common paths with explicit human escalation for ambiguous, "
                        "unsafe, or failed recovery states."
                    ),
                },
                "what_this_role_is_not": {
                    "type": "array",
                    "items": {"type": "string"},
                    "minItems": 2,
                    "maxItems": 6,
                    "description": "Common wrong framings of this JD to reject.",
                },
            },
        },
        "expensive_problem_map": {
            "type": "array",
            "minItems": 3,
            "maxItems": 8,
            "description": (
                "Expensive engineering problems behind the role — before any project spec."
            ),
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
                    "jd_evidence": {
                        "type": "string",
                        "description": (
                            "Quote/paraphrase from JD, or 'Likely implied because …'."
                        ),
                    },
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
                    "why_it_matters",
                    "danger_of_learning_it_in_isolation",
                ],
                "properties": {
                    "surface_keyword": {"type": "string"},
                    "deep_skill_or_principle": {"type": "string"},
                    "why_it_matters": {"type": "string"},
                    "danger_of_learning_it_in_isolation": {"type": "string"},
                },
            },
        },
        "candidate_background_translation": {
            "type": "object",
            "additionalProperties": False,
            "required": [
                "transferable_strengths",
                "real_gaps",
                "misleading_overclaims_to_avoid",
                "strongest_positioning_angle",
            ],
            "properties": {
                "transferable_strengths": {
                    "type": "array",
                    "minItems": 2,
                    "maxItems": 8,
                    "items": {
                        "type": "object",
                        "additionalProperties": False,
                        "required": ["strength", "profile_anchor", "role_relevance"],
                        "properties": {
                            "strength": {"type": "string"},
                            "profile_anchor": {
                                "type": "string",
                                "description": "Grounded in the profile only — never invent.",
                            },
                            "role_relevance": {"type": "string"},
                        },
                    },
                },
                "real_gaps": {
                    "type": "array",
                    "minItems": 2,
                    "maxItems": 8,
                    "items": {
                        "type": "object",
                        "additionalProperties": False,
                        "required": ["gap", "why_it_blocks_credibility", "first_thing_to_learn_instead"],
                        "properties": {
                            "gap": {"type": "string"},
                            "why_it_blocks_credibility": {"type": "string"},
                            "first_thing_to_learn_instead": {
                                "type": "string",
                                "description": (
                                    "Prerequisite mental model / principle — not a course list."
                                ),
                            },
                        },
                    },
                },
                "misleading_overclaims_to_avoid": {
                    "type": "array",
                    "items": {"type": "string"},
                },
                "strongest_positioning_angle": {"type": "string"},
            },
        },
        "general_value_threshold": {
            "type": "array",
            "minItems": 6,
            "maxItems": 14,
            "description": (
                "MUST include BOTH general engineering value capabilities AND "
                "role-specific capabilities. For adjacent-background / "
                "production-engineering (Fluidstack-like) roles, general items "
                "MUST cover: Linux/server fluency, Python automation, reproducible "
                "environments, config/env vars, logging/errors, basic HTTP/API, "
                "health checks, simple metrics, state machines, incident/debug "
                "notes, and hardware telemetry concepts — before advanced role toys."
            ),
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": [
                    "capability",
                    "capability_scope",
                    "why_it_matters_generally",
                    "connected_role_problem",
                    "evidence_that_proves_it",
                ],
                "properties": {
                    "capability": {"type": "string"},
                    "capability_scope": {
                        "type": "string",
                        "description": (
                            "Exactly one of: 'general_engineering' or 'role_specific'. "
                            "Include a majority of general_engineering items first."
                        ),
                    },
                    "why_it_matters_generally": {"type": "string"},
                    "connected_role_problem": {"type": "string"},
                    "evidence_that_proves_it": {"type": "string"},
                },
            },
        },
        "skill_dependency_graph": {
            "type": "array",
            "minItems": 7,
            "maxItems": 14,
            "description": (
                "LOW-LEVEL, realistic dependency order. Example chain for fleet/repair "
                "roles: Python script → config/env vars → logging/errors → HTTP API → "
                "Docker/reproducible env → health checks → metrics → state machine → "
                "mocked telemetry → final repair pipeline. FORBIDDEN: jumping from "
                "hardware failure modes straight to Kubernetes, or Redfish before "
                "HTTP/health/metrics foundations."
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
                    "depends_on": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Prior nodes in this graph only.",
                    },
                    "unlocks": {"type": "array", "items": {"type": "string"}},
                    "why_it_comes_before_later_work": {"type": "string"},
                },
            },
        },
        "investigation_roadmap": {
            "type": "array",
            "minItems": 5,
            "maxItems": 8,
            "description": (
                "FOUNDATION-FIRST learning ladder starting from the candidate's "
                "CURRENT capability level (adjacent software/systems value), NOT from "
                "the final role domain. Must be CUMULATIVE: each investigation produces "
                "an artifact used by the next. Before Redfish/BMC, Kubernetes, "
                "Prometheus/Grafana, or GPU fleet simulation, include prerequisites: "
                "reproducible execution; Python automation with config+logs; HTTP/API "
                "if needed; health checks + failure states; workflow/state machines; "
                "metrics and alerts; THEN mocked hardware telemetry; THEN final repair "
                "pipeline simulation as the LAST investigation."
            ),
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": [
                    "title",
                    "expensive_problem",
                    "engineering_question",
                    "mental_model_to_build",
                    "principles",
                    "technologies_introduced",
                    "observe_existing_system",
                    "build_or_modify",
                    "break_debug_improve",
                    "evidence_output",
                    "artifact_this_investigation_produces",
                    "builds_on_prior_artifact",
                    "why_this_comes_now",
                ],
                "properties": {
                    "title": {"type": "string"},
                    "expensive_problem": {"type": "string"},
                    "engineering_question": {
                        "type": "string",
                        "description": "Prefer 'Why …?' form when possible.",
                    },
                    "mental_model_to_build": {"type": "string"},
                    "principles": {
                        "type": "array",
                        "items": {"type": "string"},
                        "minItems": 1,
                    },
                    "technologies_introduced": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": (
                            "Only technologies required NOW — never introduce K8s/"
                            "Redfish/Prometheus in early investigations."
                        ),
                    },
                    "observe_existing_system": {"type": "string"},
                    "build_or_modify": {"type": "string"},
                    "break_debug_improve": {"type": "string"},
                    "evidence_output": {"type": "string"},
                    "artifact_this_investigation_produces": {
                        "type": "string",
                        "description": (
                            "Concrete artifact (repo folder, script, endpoint, diagram, "
                            "log) that later investigations will extend."
                        ),
                    },
                    "builds_on_prior_artifact": {
                        "type": "string",
                        "description": (
                            "For investigation 1: 'none — starting artifact'. "
                            "Otherwise name the prior artifact being extended."
                        ),
                    },
                    "why_this_comes_now": {
                        "type": "string",
                        "description": (
                            "Tie to candidate current level + why this unlocks the next "
                            "step — not 'because the JD mentions it'."
                        ),
                    },
                },
            },
        },
        "proof_of_work_ladder": {
            "type": "array",
            "minItems": 5,
            "maxItems": 8,
            "description": (
                "ONE progressive system that grows over time — NOT disconnected "
                "mini-projects. Each level EXTENDS the previous level of the same "
                "repo/system. Example: L1 reproducible Python service → L2 "
                "config/logging/errors → L3 health endpoint + failure states → "
                "L4 repair state machine → L5 metrics/alerting → L6 mocked "
                "Redfish/BMC telemetry → L7 final GPU repair pipeline simulation. "
                "Final GPU repair pipeline is LAST only."
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
                    "level": {
                        "type": "integer",
                        "description": "1 = base system; higher = extensions; final = role sim.",
                    },
                    "title": {"type": "string"},
                    "proves": {"type": "string"},
                    "scope": {"type": "string"},
                    "extends_previous_level": {
                        "type": "string",
                        "description": (
                            "Level 1: 'none — creates the system'. "
                            "Else: what concrete capability is added onto the prior level."
                        ),
                    },
                    "same_system_name": {
                        "type": "string",
                        "description": (
                            "Stable name of the growing system/repo (same across all levels)."
                        ),
                    },
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
                "Complete paste-ready Investigation 1 prompt. "
                "EMPTY dependency_layers, subquestions, or "
                "visual_resources_or_search_prompts is a schema FAILURE."
            ),
            "required": [
                "ready_to_paste_prompt",
                "expensive_problem",
                "engineering_question",
                "phase_0_mental_model",
                "dependency_layers",
                "subquestions",
                "visual_resources_or_search_prompts",
                "observe_build_improve_evidence_plan",
                "reflection_question",
            ],
            "properties": {
                "ready_to_paste_prompt": {
                    "type": "string",
                    "description": (
                        "Full multi-paragraph prompt including expensive problem, "
                        "engineering question, phase 0 mental model, dependency layers, "
                        "subquestions, visual resources/search prompts, observe/build/"
                        "improve/evidence plan, and reflection question."
                    ),
                },
                "expensive_problem": {"type": "string"},
                "engineering_question": {"type": "string"},
                "phase_0_mental_model": {"type": "string"},
                "dependency_layers": {
                    "type": "array",
                    "items": {"type": "string"},
                    "minItems": 3,
                    "maxItems": 8,
                },
                "subquestions": {
                    "type": "array",
                    "items": {"type": "string"},
                    "minItems": 3,
                    "maxItems": 10,
                },
                "visual_resources_or_search_prompts": {
                    "type": "array",
                    "items": {"type": "string"},
                    "minItems": 3,
                    "maxItems": 8,
                    "description": (
                        "Concrete YouTube/search/diagram prompts — never empty."
                    ),
                },
                "observe_build_improve_evidence_plan": {"type": "string"},
                "reflection_question": {"type": "string"},
            },
        },
        "evidence_plan": {
            "type": "object",
            "additionalProperties": False,
            "description": (
                "Every section MUST be non-empty with useful concrete items. "
                "Empty arrays are a HARD FAILURE. For Fluidstack-like "
                "production-engineering roles, include the foundation → final "
                "ladder evidence listed in the system rules."
            ),
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
                    "maxItems": 12,
                    "description": (
                        "Named Engineering Pages. Fluidstack-like example set: "
                        "Reproducible Execution; Python Automation with Config and Logs; "
                        "Health Checks and Failure States; Metrics and Alerts; "
                        "Repair State Machines; Mocked Hardware Telemetry; "
                        "GPU Repair Pipeline Simulation."
                    ),
                },
                "github_repos_or_folders": {
                    "type": "array",
                    "items": {"type": "string"},
                    "minItems": 2,
                    "maxItems": 8,
                    "description": (
                        "Prefer folders/modules inside the ONE growing system repo, "
                        "not disconnected projects."
                    ),
                },
                "diagrams": {
                    "type": "array",
                    "items": {"type": "string"},
                    "minItems": 4,
                    "maxItems": 10,
                    "description": (
                        "Fluidstack-like examples: dependency graph; service lifecycle "
                        "diagram; health-check flow; repair state machine; metrics "
                        "pipeline; mocked Redfish/BMC telemetry flow."
                    ),
                },
                "benchmarks_or_logs": {
                    "type": "array",
                    "items": {"type": "string"},
                    "minItems": 4,
                    "maxItems": 10,
                    "description": (
                        "Fluidstack-like examples: setup log; failure injection log; "
                        "health-check test output; MTTD/MTTR measurement output; "
                        "alert trigger log; return-to-service verification log."
                    ),
                },
                "readme_sections": {
                    "type": "array",
                    "items": {"type": "string"},
                    "minItems": 4,
                    "maxItems": 10,
                },
                "interview_artifacts": {
                    "type": "array",
                    "items": {"type": "string"},
                    "minItems": 3,
                    "maxItems": 8,
                },
            },
        },
        "interview_readiness_map": {
            "type": "array",
            "minItems": 5,
            "maxItems": 10,
            "description": (
                "Must include role-specific expectations when present in the JD. "
                "For Fluidstack-like roles, MUST include separate rows for: "
                "hardware telemetry / Redfish-BMC; fleet health thinking; "
                "incident/postmortem discipline; repair pipeline tradeoffs "
                "(plus foundation expectations as needed)."
            ),
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
                    "expectation": {
                        "type": "string",
                        "description": (
                            "Concrete expectation grounded in the JD or necessary "
                            "foundation — not vague 'know automation'."
                        ),
                    },
                    "current_readiness": {
                        "type": "string",
                        "description": "Honest readiness grounded in the profile only.",
                    },
                    "evidence_needed": {"type": "string"},
                    "likely_interview_challenge": {"type": "string"},
                    "how_to_answer_after_roadmap": {"type": "string"},
                },
            },
        },
    },
}


SYSTEM_PROMPT = """You are Project Lambda — a Role-to-Roadmap Engine.

PRODUCT SHAPE (critical)
You are NOT a Problem-Solution Contract Generator.
You are NOT a project generator that jumps from a JD to job-domain toys
(Kubernetes, Redfish, GPU repair pipelines) in Investigation 1.

You ARE an engineering-growth / learning-ladder system that translates a job
description + engineer background into expensive problems, mental models, skill
dependencies, a progressive investigation roadmap, a CUMULATIVE proof-of-work
ladder (one system that grows), evidence, and interview readiness.

Start from the candidate's CURRENT capability level.
For adjacent-background engineers (industrial / EE / field / partial software),
establish general software/systems value BEFORE job-specific fleet work.

Always ask: what must this engineer understand first before the role project
is credible? The final GPU repair pipeline simulation is LAST, never early.

LEARNING PIPELINE (every investigation)
Expensive Problem → Engineering Question → Mental Model → Engineering Principles
→ Technologies (only as needed) → Observe Existing Systems → Build or Modify
→ Break / Debug / Improve → Explain Tradeoffs → Produce Evidence

RULE A — FOUNDATION-FIRST
Before Redfish/BMC, Kubernetes, Prometheus, Grafana, or GPU fleet simulation,
the investigation_roadmap MUST include prerequisite investigations such as:
1) Why does software need reproducible execution across machines?
2) Python automation with config and logs
3) HTTP/API basics if needed
4) Health checks and failure states
5) Workflow / state machines
6) Metrics and alerts
Only THEN: mocked hardware telemetry
Only THEN: final GPU repair pipeline simulation (last investigation / last ladder level)

RULE B — DEPENDENCY GRAPH
Skill dependencies must be low-level and realistic.
Good chain example:
Python script → config/env vars → logging/errors → HTTP API → Docker/reproducible
env → health checks → metrics → state machine → mocked telemetry → final repair
pipeline.
FORBIDDEN: hardware failure modes → Kubernetes jumps; Redfish before HTTP/health;
Prometheus before a process that emits logs/events; disconnected tech islands.

RULE C — CUMULATIVE PROOF LADDER
proof_of_work_ladder is ONE progressive system that grows over time — not
disconnected mini-projects. Each level EXTENDS the previous level of the SAME
system (same_system_name stable across levels).
Example:
Level 1: reproducible Python service
Level 2: add config / logging / errors
Level 3: add health endpoint and failure states
Level 4: add repair state machine
Level 5: add metrics and alerting
Level 6: add mocked Redfish/BMC telemetry
Level 7: final GPU repair pipeline simulation
investigation_roadmap must also be cumulative: each produces
artifact_this_investigation_produces that the next builds_on_prior_artifact.

RULE D — FIRST INVESTIGATION PROMPT
first_investigation_prompt MUST include non-empty:
- expensive problem
- engineering question
- phase 0 mental model
- dependency_layers (min 3)
- subquestions (min 3)
- visual_resources_or_search_prompts (min 3 concrete search/video/diagram prompts)
- observe/build/improve/evidence plan
- reflection question
Empty lists are a HARD FAILURE. ready_to_paste_prompt must include all of the above.

RULE E — GENERAL VALUE THRESHOLD
Include BOTH capability_scope='general_engineering' AND 'role_specific'.
For Fluidstack-like production engineering roles, general_engineering MUST cover:
Linux/server fluency, Python automation, reproducible environments, config/env
vars, logging/errors, basic HTTP/API understanding, health checks, simple metrics,
state machines, incident/debug notes, hardware telemetry concepts.
Role-specific items come after those foundations are listed.

RULE F — AUTOMATION LANGUAGE
Never use absolute "fully automated" / "full automation" wording in
role_interpretation, success criteria, investigations, proof ladder, or interview
answers. Prefer:
"highly automated common repair paths with explicit human escalation for
ambiguous, unsafe, or failed recovery states."

RULE G — EVIDENCE PLAN (never empty)
Every evidence_plan section MUST have useful non-empty items:
obsidian_pages, github_repos_or_folders, diagrams, benchmarks_or_logs,
readme_sections, interview_artifacts.
For Fluidstack-like roles, Obsidian pages should include:
Reproducible Execution; Python Automation with Config and Logs; Health Checks
and Failure States; Metrics and Alerts; Repair State Machines; Mocked Hardware
Telemetry; GPU Repair Pipeline Simulation.
Diagrams should include: dependency graph; service lifecycle diagram;
health-check flow; repair state machine; metrics pipeline; mocked Redfish/BMC
telemetry flow.
Benchmarks/logs should include: setup log; failure injection log; health-check
test output; MTTD/MTTR measurement output; alert trigger log;
return-to-service verification log.

RULE H — INTERVIEW READINESS
When the JD includes fleet/repair/telemetry themes, interview_readiness_map
MUST include role-specific expectations for:
- hardware telemetry / Redfish-BMC
- fleet health thinking
- incident/postmortem discipline
- repair pipeline tradeoffs
Do not only list generic "automation" / "API" soft expectations.

ANTI-PATTERNS (failures)
- Investigation 1 about hardware failure modes / K8s / Redfish / fleet repair
- Disconnected mini-projects (new repo every level)
- Generic study plans or course recommendations
- Learning technologies in isolation
- Inventing candidate experience or employer metrics
- Empty first-investigation arrays
- Empty evidence_plan sections
- Absolute "fully automated" language
- Final repair pipeline appearing before foundation layers
- Regressing to project-first output (skipping the learning ladder)

CANDIDATE TRANSLATION
Translate the profile honestly. Transferable strengths need profile anchors.
Real gaps: what blocks credibility + what mental model/principle comes first.

OUTPUT
Match the JSON schema exactly.
Keep the foundation-first investigation roadmap as a learning ladder.
Do not regress to project-first generation.
Be progressive, cumulative, and grounded in the candidate's actual starting level.
"""


def build_user_prompt(job_description: str, engineer_profile: str) -> str:
    return f"""Translate this role into a Foundation-First Role-to-Roadmap for this engineer.

Critical priorities:
1. Start investigations from THIS candidate's current capability level — not the
   final JD domain. Keep the learning ladder; do NOT regress to project-first.
2. For adjacent-background engineers, establish general software/systems value
   before fleet/GPU/Redfish/K8s work.
3. Make the roadmap cumulative: each investigation's artifact becomes input to
   the next.
4. Skill dependency graph must be low-level (Python → config → logs → HTTP →
   Docker → health → metrics → state machine → mocked telemetry → final pipeline).
5. Proof-of-work ladder = ONE growing system (same_system_name). Final GPU repair
   pipeline simulation is LAST only. Prefer highly automated common repair paths
   with explicit human escalation — NEVER "fully automated".
6. general_value_threshold: both general_engineering and role_specific.
7. first_investigation_prompt: NO empty lists (min 3 each for dependencies,
   subquestions, visual prompts).
8. evidence_plan: EVERY section non-empty with useful items (Obsidian pages,
   diagrams, benchmarks/logs per Fluidstack-like examples in the rules).
9. interview_readiness_map: when JD includes them, include Redfish-BMC / hardware
   telemetry, fleet health thinking, incident/postmortem discipline, and repair
   pipeline tradeoffs.

=== JOB DESCRIPTION ===
{job_description.strip()}

=== ENGINEER PROFILE / BACKGROUND ===
{engineer_profile.strip()}

Produce the structured Role-to-Roadmap JSON now.
"""
