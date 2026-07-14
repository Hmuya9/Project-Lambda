"""Prompt templates and output schema for Problem-Solution Contract generation.

Improve the product by iterating here — keep the CLI and I/O layers stable.
"""

from __future__ import annotations

CONTRACT_JSON_SCHEMA: dict = {
    "type": "object",
    "additionalProperties": False,
    "required": [
        "role_truth",
        "rejected_generic_interpretations",
        "role_specific_problem_signature",
        "surface_keywords",
        "hidden_engineering_problems",
        "constraints",
        "tradeoffs",
        "performance_expectations",
        "candidate_background_translation",
        "missing_proof_of_capability",
        "proof_of_work_project",
        "evidence_artifacts",
        "verification_checklist",
        "staff_engineer_review",
        "problem_solution_contract_summary",
    ],
    "properties": {
        "role_truth": {
            "type": "object",
            "additionalProperties": False,
            "required": ["one_liner", "mission", "what_success_looks_like"],
            "properties": {
                "one_liner": {
                    "type": "string",
                    "description": (
                        "What this job is really about in one sharp, role-specific sentence. "
                        "Forbidden: generic infra slogans like 'optimize latency and GPU utilization'."
                    ),
                },
                "mission": {
                    "type": "string",
                    "description": (
                        "The underlying engineering mission beneath the JD wording. "
                        "Name the actual control problem, ownership boundary, or failure domain."
                    ),
                },
                "what_success_looks_like": {
                    "type": "string",
                    "description": (
                        "Concrete outcomes grounded in the JD. "
                        "Do not invent employer metrics; if proposing measurable bars, "
                        "prefix with 'Proposed project bar:' and mark them as proposed."
                    ),
                },
            },
        },
        "rejected_generic_interpretations": {
            "type": "array",
            "description": (
                "Obvious/generic readings of the JD that a weak analysis would produce, "
                "and why each is insufficient for THIS role."
            ),
            "minItems": 3,
            "maxItems": 6,
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": ["generic_interpretation", "why_insufficient"],
                "properties": {
                    "generic_interpretation": {
                        "type": "string",
                        "description": (
                            "A shallow reading, e.g. 'Learn Kubernetes', "
                            "'Add observability', 'Improve GPU utilization'."
                        ),
                    },
                    "why_insufficient": {
                        "type": "string",
                        "description": (
                            "Why that interpretation misses the real engineering problem "
                            "implied by THIS JD."
                        ),
                    },
                },
            },
        },
        "role_specific_problem_signature": {
            "type": "object",
            "additionalProperties": False,
            "description": (
                "The unique engineering signature of this job — what makes it itself, "
                "not a generic 'AI infra' role."
            ),
            "required": [
                "signature_statements",
                "primary_failure_domain",
                "ownership_boundary",
                "what_must_become_a_system",
            ],
            "properties": {
                "signature_statements": {
                    "type": "array",
                    "minItems": 3,
                    "maxItems": 7,
                    "items": {"type": "string"},
                    "description": (
                        "Short, sharp claims unique to this role. Examples of style: "
                        "'GPU failure is a fleet throughput problem'; "
                        "'Repair must become a pipeline, not a manual procedure'; "
                        "'Hardware qualification must happen before production'."
                    ),
                },
                "primary_failure_domain": {
                    "type": "string",
                    "description": "Where value is lost when this role fails (be specific to the JD).",
                },
                "ownership_boundary": {
                    "type": "string",
                    "description": (
                        "What this hire owns end-to-end vs what they influence. "
                        "Prefer 'likely implied' when the JD is ambiguous."
                    ),
                },
                "what_must_become_a_system": {
                    "type": "string",
                    "description": (
                        "The manual, heroic, or ad-hoc work that this role must convert "
                        "into a repeatable pipeline/system."
                    ),
                },
            },
        },
        "surface_keywords": {
            "type": "array",
            "items": {"type": "string"},
            "description": (
                "Keywords/phrases taken from the JD (not invented). "
                "These are signals only — not the analysis."
            ),
        },
        "hidden_engineering_problems": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": [
                    "problem",
                    "why_it_matters",
                    "likely_failure_mode",
                    "why_not_generic",
                    "evidence_basis",
                ],
                "properties": {
                    "problem": {
                        "type": "string",
                        "description": (
                            "A concrete hidden problem specific to this JD — not "
                            "'high latency' or 'need more observability' without a mechanism."
                        ),
                    },
                    "why_it_matters": {"type": "string"},
                    "likely_failure_mode": {"type": "string"},
                    "why_not_generic": {
                        "type": "string",
                        "description": (
                            "One sentence explaining why this is not interchangeable with "
                            "generic AI-infra advice."
                        ),
                    },
                    "evidence_basis": {
                        "type": "string",
                        "description": (
                            "Where this came from: quote/paraphrase of JD language, or "
                            "'Likely implied because …'. Never claim fake certainty."
                        ),
                    },
                },
            },
            "minItems": 3,
            "maxItems": 6,
        },
        "constraints": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": ["constraint", "source"],
                "properties": {
                    "constraint": {"type": "string"},
                    "source": {
                        "type": "string",
                        "description": (
                            "One of: 'stated in JD', 'likely implied', "
                            "or 'proposed project constraint'. "
                            "Project Lambda design defaults — local-first, "
                            "simulated if real infrastructure unavailable, "
                            "produce logs/metrics/tests/README, failure injection, "
                            "verification checklist — MUST be labeled "
                            "'proposed project constraint'. They are NOT "
                            "'stated in JD' unless the JD explicitly requires them."
                        ),
                    },
                },
            },
            "description": (
                "Hard or likely constraints with explicit source labels. "
                "Never label Project Lambda project-design defaults as "
                "'stated in JD'."
            ),
        },
        "tradeoffs": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": [
                    "axis",
                    "choice_a",
                    "choice_b",
                    "recommendation",
                    "why_this_axis_matters_here",
                ],
                "properties": {
                    "axis": {
                        "type": "string",
                        "description": (
                            "A real decision axis for THIS role — not a generic "
                            "'latency vs utilization' platitude unless the JD forces it."
                        ),
                    },
                    "choice_a": {"type": "string"},
                    "choice_b": {"type": "string"},
                    "recommendation": {"type": "string"},
                    "why_this_axis_matters_here": {
                        "type": "string",
                        "description": "Tie the tradeoff to the role's problem signature.",
                    },
                },
            },
            "minItems": 2,
            "maxItems": 5,
        },
        "performance_expectations": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": [
                    "metric_or_bar",
                    "why_it_exists",
                    "how_to_demonstrate",
                    "source",
                ],
                "properties": {
                    "metric_or_bar": {
                        "type": "string",
                        "description": (
                            "Prefer qualitative bars from the JD. If numeric, "
                            "only use numbers present in the JD, OR label as a "
                            "proposed project metric."
                        ),
                    },
                    "why_it_exists": {"type": "string"},
                    "how_to_demonstrate": {"type": "string"},
                    "source": {
                        "type": "string",
                        "description": (
                            "'stated in JD' | 'likely implied' | "
                            "'proposed project metric (not an employer requirement)'."
                        ),
                    },
                },
            },
        },
        "candidate_background_translation": {
            "type": "object",
            "additionalProperties": False,
            "description": (
                "Translate the engineer profile into role-relevant strengths and gaps. "
                "Do not invent background experience not present in the profile."
            ),
            "required": [
                "role_relevant_strengths",
                "transferable_patterns",
                "honest_gaps",
                "what_must_not_be_claimed",
            ],
            "properties": {
                "role_relevant_strengths": {
                    "type": "array",
                    "minItems": 2,
                    "maxItems": 6,
                    "items": {
                        "type": "object",
                        "additionalProperties": False,
                        "required": ["strength", "profile_anchor", "role_relevance"],
                        "properties": {
                            "strength": {"type": "string"},
                            "profile_anchor": {
                                "type": "string",
                                "description": "Paraphrase of something actually in the profile.",
                            },
                            "role_relevance": {
                                "type": "string",
                                "description": "How this maps onto the role's problem signature.",
                            },
                        },
                    },
                },
                "transferable_patterns": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": (
                        "Engineering patterns the candidate has shown that transfer "
                        "(e.g. admission control, backpressure) — still grounded in profile."
                    ),
                },
                "honest_gaps": {
                    "type": "array",
                    "minItems": 1,
                    "maxItems": 5,
                    "items": {
                        "type": "object",
                        "additionalProperties": False,
                        "required": ["gap", "why_it_matters_for_this_role"],
                        "properties": {
                            "gap": {"type": "string"},
                            "why_it_matters_for_this_role": {"type": "string"},
                        },
                    },
                },
                "what_must_not_be_claimed": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": (
                        "Things a resume rewrite might invent here that the profile "
                        "does not support — explicitly forbid them."
                    ),
                },
            },
        },
        "missing_proof_of_capability": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": ["gap", "evidence_that_would_close_it", "profile_relevance"],
                "properties": {
                    "gap": {"type": "string"},
                    "evidence_that_would_close_it": {"type": "string"},
                    "profile_relevance": {
                        "type": "string",
                        "description": (
                            "How the candidate's ACTUAL background helps or fails to "
                            "cover this gap. Do not invent experience."
                        ),
                    },
                },
            },
        },
        "proof_of_work_project": {
            "type": "object",
            "additionalProperties": False,
            "required": [
                "title",
                "problem_statement",
                "scope",
                "non_goals",
                "deliverables",
                "tech_stack_suggestion",
                "success_criteria",
                "timebox",
                "why_this_project",
                "operational_model",
                "automation_boundaries",
                "state_machine",
                "hardware_management_simulation",
                "proposed_ops_metrics",
                "design_constraints",
                "simulation_strategy",
                "failure_injection_plan",
            ],
            "properties": {
                "title": {
                    "type": "string",
                    "description": "Short, specific title — not 'AI Infra Optimization Platform'.",
                },
                "problem_statement": {
                    "type": "string",
                    "description": (
                        "The single engineering problem this project proves the "
                        "candidate can attack — tied to the role signature."
                    ),
                },
                "scope": {
                    "type": "string",
                    "description": (
                        "Narrow scope for 1–3 weeks. Explicitly list what is in-bounds. "
                        "Must be buildable locally or with simulation."
                    ),
                },
                "non_goals": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": (
                        "What this project will NOT attempt (real GPU fleets, company "
                        "systems, multi-month platforms, etc.)."
                    ),
                },
                "deliverables": {
                    "type": "array",
                    "items": {"type": "string"},
                    "minItems": 3,
                    "maxItems": 8,
                },
                "tech_stack_suggestion": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Local-first tools the candidate can actually run.",
                },
                "success_criteria": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": (
                        "Pass/fail criteria for the project. Prefer ops metrics "
                        "(MTTD, time-to-triage, MTTRS, auto-resolve %, escalate %, "
                        "false positive rate, RTS pass rate). Numbers are proposed "
                        "project metrics, not invented employer SLOs."
                    ),
                },
                "timebox": {
                    "type": "string",
                    "description": "Must be 1–3 weeks (e.g. '10 focused days' or '2 weeks').",
                },
                "why_this_project": {
                    "type": "string",
                    "description": (
                        "Why this single, small project is high-signal for THIS role "
                        "and THIS candidate profile — not generic resume padding."
                    ),
                },
                "operational_model": {
                    "type": "object",
                    "additionalProperties": False,
                    "description": (
                        "Observe → decide → act → verify recovery → escalate humans. "
                        "Required for repair/deployment/qualification/ops projects."
                    ),
                    "required": [
                        "what_is_observed",
                        "what_decision_is_made",
                        "what_action_is_taken",
                        "how_recovery_is_verified",
                        "when_humans_are_escalated",
                    ],
                    "properties": {
                        "what_is_observed": {"type": "string"},
                        "what_decision_is_made": {"type": "string"},
                        "what_action_is_taken": {"type": "string"},
                        "how_recovery_is_verified": {"type": "string"},
                        "when_humans_are_escalated": {"type": "string"},
                    },
                },
                "automation_boundaries": {
                    "type": "object",
                    "additionalProperties": False,
                    "description": (
                        "Prefer highly automated common paths with explicit human "
                        "escalation for ambiguous or unsafe states. Do NOT use "
                        "absolute 'fully automated' / 'full automation' language. "
                        "Distinguish automated common paths, human escalation, "
                        "unsafe/ambiguous states, and manual approval gates."
                    ),
                    "required": [
                        "automated_common_paths",
                        "human_escalation_paths",
                        "unsafe_or_ambiguous_states",
                        "manual_approval_gates",
                        "why_not_full_automation",
                    ],
                    "properties": {
                        "automated_common_paths": {
                            "type": "array",
                            "items": {"type": "string"},
                            "minItems": 1,
                            "description": (
                                "Common paths that are highly automated — not "
                                "'fully automated forever'."
                            ),
                        },
                        "human_escalation_paths": {
                            "type": "array",
                            "items": {"type": "string"},
                            "minItems": 1,
                        },
                        "unsafe_or_ambiguous_states": {
                            "type": "array",
                            "items": {"type": "string"},
                            "minItems": 1,
                        },
                        "manual_approval_gates": {
                            "type": "array",
                            "items": {"type": "string"},
                            "minItems": 1,
                        },
                        "why_not_full_automation": {
                            "type": "string",
                            "description": (
                                "Explain preferred phrasing: highly automated common "
                                "paths with explicit human escalation for ambiguous "
                                "or unsafe states — not absolute full automation."
                            ),
                        },
                    },
                },
                "state_machine": {
                    "type": "object",
                    "additionalProperties": False,
                    "description": (
                        "REQUIRED when the role involves workflow, repair, deployment, "
                        "incident response, qualification, or automation. Example "
                        "happy path ends in a terminal success state: detected → "
                        "triage → isolated → logs_collected → repair_action_selected → "
                        "waiting_for_parts → return_to_service_test → production_ready. "
                        "Use escalated as a separate terminal path. Do NOT transition "
                        "from return_to_service / return_to_service_test back to detected."
                    ),
                    "required": [
                        "required_for_this_role",
                        "rationale",
                        "states",
                        "happy_path",
                        "transitions",
                        "terminal_states",
                    ],
                    "properties": {
                        "required_for_this_role": {
                            "type": "boolean",
                            "description": (
                                "True for workflow/repair/deployment/incident/"
                                "qualification/automation roles. Almost always true "
                                "for production-engineering / fleet / ops JDs."
                            ),
                        },
                        "rationale": {
                            "type": "string",
                            "description": "Why a state machine is or is not required.",
                        },
                        "states": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": (
                                "Explicit states. Prefer concrete names like "
                                "detected, triage, isolated, logs_collected, "
                                "repair_action_selected, waiting_for_parts, "
                                "return_to_service_test, production_ready, escalated."
                            ),
                        },
                        "happy_path": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": (
                                "Ordered happy-path state sequence ending in a "
                                "terminal success state (e.g. production_ready), "
                                "not looping back to detected."
                            ),
                        },
                        "transitions": {
                            "type": "array",
                            "minItems": 3,
                            "items": {
                                "type": "object",
                                "additionalProperties": False,
                                "required": [
                                    "from_state",
                                    "to_state",
                                    "trigger",
                                    "path_type",
                                ],
                                "properties": {
                                    "from_state": {"type": "string"},
                                    "to_state": {"type": "string"},
                                    "trigger": {"type": "string"},
                                    "path_type": {
                                        "type": "string",
                                        "description": (
                                            "One of: automated_common_path | "
                                            "human_escalation | manual_approval | "
                                            "unsafe_hold."
                                        ),
                                    },
                                },
                            },
                            "description": (
                                "Forbidden: return_to_service / return_to_service_test "
                                "→ detected. After RTS, go to production_ready "
                                "(terminal) or escalated (terminal). If RTS fails, "
                                "escalate or re-enter triage/repair — do not reopen "
                                "as a fresh 'detected' edge from RTS."
                            ),
                        },
                        "terminal_states": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": (
                                "Must include production_ready and/or treat "
                                "return_to_service_test as terminal on pass. "
                                "Also include escalated. Happy path must end here."
                            ),
                        },
                    },
                },
                "hardware_management_simulation": {
                    "type": "object",
                    "additionalProperties": False,
                    "description": (
                        "If the JD mentions Redfish, BMC, IPMI, firmware telemetry, "
                        "hardware lifecycle, or fleet health, require a mocked "
                        "hardware management API or telemetry source."
                    ),
                    "required": [
                        "required_by_jd",
                        "jd_signals",
                        "mocked_api_or_telemetry_source",
                        "example_endpoints_or_signals",
                        "what_is_intentionally_not_real",
                    ],
                    "properties": {
                        "required_by_jd": {"type": "boolean"},
                        "jd_signals": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": (
                                "JD phrases that triggered this requirement "
                                "(Redfish, BMC, IPMI, firmware, RMA, fleet health, etc)."
                            ),
                        },
                        "mocked_api_or_telemetry_source": {
                            "type": "string",
                            "description": (
                                "Describe the local mock (e.g. fake Redfish/BMC HTTP "
                                "server, synthetic DCGM-like exporter)."
                            ),
                        },
                        "example_endpoints_or_signals": {
                            "type": "array",
                            "items": {"type": "string"},
                        },
                        "what_is_intentionally_not_real": {"type": "string"},
                    },
                },
                "proposed_ops_metrics": {
                    "type": "array",
                    "minItems": 4,
                    "maxItems": 8,
                    "description": (
                        "Proposed project metrics for repair/fleet/ops work. Prefer: "
                        "mean time to detect, mean time to triage, mean time to return "
                        "to service, repair queue depth, percentage auto-resolved, "
                        "percentage escalated, false positive rate, return-to-service "
                        "pass rate. Label as proposed project metrics."
                    ),
                    "items": {
                        "type": "object",
                        "additionalProperties": False,
                        "required": [
                            "metric",
                            "definition",
                            "how_measured_in_project",
                            "source",
                        ],
                        "properties": {
                            "metric": {"type": "string"},
                            "definition": {"type": "string"},
                            "how_measured_in_project": {"type": "string"},
                            "source": {
                                "type": "string",
                                "description": (
                                    "Usually: 'proposed project metric "
                                    "(not an employer requirement)'."
                                ),
                            },
                        },
                    },
                },
                "design_constraints": {
                    "type": "object",
                    "additionalProperties": False,
                    "required": [
                        "local_first",
                        "simulated_when_needed",
                        "required_outputs",
                        "includes_failure_injection",
                        "includes_verification_checklist",
                    ],
                    "properties": {
                        "local_first": {
                            "type": "boolean",
                            "description": "True — project runs without company systems.",
                        },
                        "simulated_when_needed": {
                            "type": "boolean",
                            "description": (
                                "True when real GPUs / fleets / research partners "
                                "are unavailable."
                            ),
                        },
                        "required_outputs": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": (
                                "Must include logs, metrics, tests, README, and "
                                "tradeoff explanation."
                            ),
                        },
                        "includes_failure_injection": {"type": "boolean"},
                        "includes_verification_checklist": {"type": "boolean"},
                    },
                },
                "simulation_strategy": {
                    "type": "string",
                    "description": (
                        "How to simulate missing real infrastructure. If hardware "
                        "management is required, include the mocked Redfish/BMC/IPMI "
                        "or telemetry layer here as well."
                    ),
                },
                "failure_injection_plan": {
                    "type": "array",
                    "minItems": 2,
                    "maxItems": 6,
                    "items": {"type": "string"},
                    "description": "Concrete failures the project will inject and observe.",
                },
            },
        },
        "evidence_artifacts": {
            "type": "object",
            "additionalProperties": False,
            "description": "Required proof artifacts the project must produce.",
            "required": [
                "github_repo",
                "readme",
                "architecture_diagram",
                "failure_mode_table",
                "verification_log",
                "benchmark_or_measurement_output",
                "postmortem_or_incident_note",
                "two_minute_interview_explanation",
            ],
            "properties": {
                "github_repo": {
                    "type": "string",
                    "description": "What the repo must contain / demonstrate.",
                },
                "readme": {
                    "type": "string",
                    "description": "What the README must explain (problem, how to run, results).",
                },
                "architecture_diagram": {
                    "type": "string",
                    "description": "What the architecture diagram must show.",
                },
                "failure_mode_table": {
                    "type": "string",
                    "description": "What rows/columns the failure mode table must cover.",
                },
                "verification_log": {
                    "type": "string",
                    "description": "What a completed verification log looks like.",
                },
                "benchmark_or_measurement_output": {
                    "type": "string",
                    "description": (
                        "What measurement artifact to produce. Numbers here are "
                        "proposed project metrics, not invented employer SLOs."
                    ),
                },
                "postmortem_or_incident_note": {
                    "type": "string",
                    "description": "What the incident/postmortem note must analyze.",
                },
                "two_minute_interview_explanation": {
                    "type": "string",
                    "description": (
                        "A tight spoken script / outline the candidate could deliver "
                        "in two minutes about the problem and evidence."
                    ),
                },
            },
        },
        "verification_checklist": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": ["check", "how_to_verify", "pass_condition"],
                "properties": {
                    "check": {"type": "string"},
                    "how_to_verify": {"type": "string"},
                    "pass_condition": {"type": "string"},
                },
            },
            "minItems": 5,
            "maxItems": 12,
            "description": (
                "Project verification / benchmark checklist — runnable without "
                "company systems."
            ),
        },
        "staff_engineer_review": {
            "type": "object",
            "additionalProperties": False,
            "required": [
                "is_credible",
                "credibility_rationale",
                "what_makes_it_credible",
                "what_could_make_it_look_toy",
                "one_change_for_hiring_manager_relevance",
                "is_too_broad",
                "scope_diagnosis",
                "how_to_make_higher_signal",
                "hiring_manager_challenges",
            ],
            "properties": {
                "is_credible": {
                    "type": "boolean",
                    "description": (
                        "Skeptical default. Do NOT default to true. Set true only if "
                        "the project has an explicit state machine / ops model, "
                        "automation boundaries (highly automated common paths with "
                        "human escalation — not absolute full automation), "
                        "no RTS→detected loops, correct source labels for project "
                        "constraints, meaningful simulation (mocked hardware API "
                        "when relevant), and measurable ops metrics. Otherwise false."
                    ),
                },
                "credibility_rationale": {
                    "type": "string",
                    "description": "Overall skeptical judgment — name remaining doubts.",
                },
                "what_makes_it_credible": {
                    "type": "string",
                    "description": "Exactly ONE concrete credibility strength.",
                },
                "what_could_make_it_look_toy": {
                    "type": "string",
                    "description": (
                        "Exactly ONE concrete way this could look like a toy demo "
                        "to a hiring manager."
                    ),
                },
                "one_change_for_hiring_manager_relevance": {
                    "type": "string",
                    "description": (
                        "Exactly ONE change that would make the project more "
                        "hiring-manager-relevant."
                    ),
                },
                "is_too_broad": {
                    "type": "boolean",
                    "description": "True if the project smells like a 3-month platform.",
                },
                "scope_diagnosis": {
                    "type": "string",
                    "description": "What is correctly narrow vs what still risks sprawl.",
                },
                "how_to_make_higher_signal": {
                    "type": "array",
                    "items": {"type": "string"},
                    "minItems": 2,
                    "maxItems": 5,
                },
                "hiring_manager_challenges": {
                    "type": "array",
                    "items": {"type": "string"},
                    "minItems": 2,
                    "maxItems": 5,
                    "description": (
                        "Hard questions a hiring manager would ask to poke holes "
                        "in the proof."
                    ),
                },
            },
        },
        "problem_solution_contract_summary": {
            "type": "object",
            "additionalProperties": False,
            "required": ["problem", "proposed_solution_shape", "non_goals", "risks"],
            "properties": {
                "problem": {
                    "type": "string",
                    "description": "Restate the role-specific problem, not a generic roadmap.",
                },
                "proposed_solution_shape": {
                    "type": "string",
                    "description": (
                        "Shape of the proof / approach — constrained, local-first, "
                        "failure-aware."
                    ),
                },
                "non_goals": {"type": "array", "items": {"type": "string"}},
                "risks": {"type": "array", "items": {"type": "string"}},
            },
        },
    },
}


SYSTEM_PROMPT = """You are Project Lambda — an engineering translation engine.

CORE JOB
Take a technical job description and an engineer background, then translate
solution-shaped role language into hidden engineering problems, constraints,
tradeoffs, and a sharp proof-of-work artifact.

You are NOT a career coach, resume scorer, interview tutor, or roadmap generator.

ANTI-GENERICITY (critical)
Reject interchangeable AI-infra advice. Outputs that only say "improve latency",
"raise GPU utilization", "add autoscaling", or "improve observability" WITHOUT a
role-specific mechanism, ownership boundary, or failure domain are FAILURES.

Before you analyze, explicitly populate rejected_generic_interpretations with the
obvious shallow readings and why each is insufficient for THIS JD.
Example style:
- "Learn Kubernetes" is insufficient if the role is about bare-metal GPU fleet
  reliability, not writing Deployment YAML.
- "Add dashboards" is insufficient if the real problem is absence of a repair
  pipeline that converts hardware faults into throughput recovery.

Then populate role_specific_problem_signature with what makes this job itself:
- Rename the problem (e.g. "GPU failure is a fleet throughput problem").
- Say what must become a system (e.g. "repair must become a pipeline").
- Name sequencing constraints (e.g. "hardware qualification before production").

GROUNDING RULES
1. Do not invent employer metrics (percentages, dollar amounts, SLO numbers)
   unless they appear in the JD.
2. If you need numbers for the proof project, label them as
   "proposed project metric (not an employer requirement)".
3. Prefer "likely implied because …" over fake certainty.
4. Constraints and performance bars must carry an explicit source label.
   Project Lambda design defaults (local-first, simulated if real
   infrastructure unavailable, produce logs/metrics/tests/README, failure
   injection, verification checklist) are "proposed project constraint" —
   NEVER "stated in JD" unless the JD explicitly requires them.
5. Never invent candidate experience. Only translate what the profile states.
6. Quote or paraphrase JD/profile anchors when making claims.

PROOF-OF-WORK RULES
- ONE small project. Timebox MUST be 1–3 weeks (not months).
- Must be buildable locally or with simulation.
- Must NOT require access to real company systems, production GPU fleets,
  or real research teams.
- Design constraints (all required; source = proposed project constraint):
  - local-first
  - simulated when real infrastructure is unavailable
  - produces logs, metrics, tests, README, and tradeoff explanation
  - includes failure injection
  - includes verification checklist
- operational_model REQUIRED: what is observed, what decision is made,
  what action is taken, how recovery is verified, when humans escalate.
- STATE MACHINE REQUIRED when the role involves workflow, repair, deployment,
  incident response, qualification, or automation (true for almost all
  production-engineering / fleet / ops JDs). Include explicit states such as:
  detected → triage → isolated → logs_collected → repair_action_selected →
  waiting_for_parts → return_to_service_test → production_ready.
  Use escalated as a separate terminal path.
  FORBIDDEN: transitions from return_to_service / return_to_service_test
  back to detected. Happy path must end at production_ready (or treat
  return_to_service_test as terminal on pass).
  Tag transitions as automated_common_path | human_escalation |
  manual_approval | unsafe_hold.
- Avoid absolute "fully automated" language. Prefer:
  "highly automated common paths with explicit human escalation for
  ambiguous or unsafe states." Always distinguish automated common paths,
  human escalation paths, unsafe/ambiguous states, and manual approval gates.
- HARDWARE SIMULATION: if the JD mentions Redfish, BMC, IPMI, firmware
  telemetry, hardware lifecycle, RMA, or fleet health, the project MUST
  include a mocked hardware management API or telemetry source (fake
  Redfish/BMC server, synthetic exporter, etc.).
- VERIFICATION METRICS for repair/fleet/ops projects should prefer:
  mean time to detect, mean time to triage, mean time to return to service,
  repair queue depth, % auto-resolved, % escalated, false positive rate,
  return-to-service pass rate. Label as proposed project metrics.
- evidence_artifacts must specify what each required artifact contains:
  GitHub repo, README, architecture diagram, failure mode table,
  verification log, benchmark/measurement output, postmortem/incident note,
  two-minute interview explanation.

STAFF REVIEW (skeptical)
Do NOT default is_credible=true. Be a harsh reviewer.
Must explicitly name:
1) one thing that makes the project credible
2) one thing that could make it look toy
3) one change that would make it more hiring-manager-relevant
Fail credibility if the project is vague automation theater, lacks a real
state machine/ops model, claims absolute full/fully automated repair with
no escalation boundaries, loops RTS back to detected, mislabels project-
design constraints as "stated in JD", or has no meaningful
hardware/telemetry mock when the JD demands it.

OUTPUT
Match the JSON schema exactly. Be sharp, specific, and falsifiable.
"""


def build_user_prompt(job_description: str, engineer_profile: str) -> str:
    return f"""Translate the following role into a Problem-Solution Contract for this engineer.

Priorities for THIS run:
1. Reject generic AI-infra interpretations first.
2. Extract the role-specific problem signature.
3. Translate the candidate background honestly (no invented experience).
4. Propose ONE local-first, 1–3 week proof-of-work project with:
   - operational_model (observe → decide → act → verify → escalate)
   - explicit state_machine ending in production_ready / escalated
     (no return_to_service → detected loops)
   - automation_boundaries: highly automated common paths with explicit
     human escalation for ambiguous or unsafe states (no "fully automated")
   - mocked hardware management API/telemetry when Redfish/BMC/IPMI/fleet health
   - proposed ops metrics (MTTD, triage time, MTTRS, queue depth, auto-resolve %,
     escalate %, false positive rate, RTS pass rate)
5. Label Project Lambda design defaults as "proposed project constraint",
   not "stated in JD".
6. Staff review must be skeptical (do not default credible=true).
7. Specify evidence artifacts.

=== JOB DESCRIPTION ===
{job_description.strip()}

=== ENGINEER PROFILE / BACKGROUND ===
{engineer_profile.strip()}

Produce the structured contract now. Be role-specific and engineering-concrete.
"""
