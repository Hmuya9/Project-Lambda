"""Render and write Markdown Project Lambda Role-to-Roadmap outputs."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def _bullets(items: list[str]) -> str:
    if not items:
        return "_None listed._"
    return "\n".join(f"- {item}" for item in items)


def _yes_no(value: bool) -> str:
    return "yes" if value else "no"


def render_markdown(contract: dict[str, Any], *, job_source: str, profile_source: str) -> str:
    role = contract["role_interpretation"]
    transfer = contract["candidate_transfer_map"]
    tracks = contract["roadmap_tracks"]
    first = contract["first_investigation_prompt"]
    evidence = contract["evidence_plan"]
    guards = contract["guardrail_checks"]
    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    problems = "\n\n".join(
        f"### {i}. {item['problem']}\n"
        f"- **Why company pays for it:** {item['why_company_pays_for_it']}\n"
        f"- **Constraints:** {', '.join(item['constraints']) if item['constraints'] else '_none_'}\n"
        f"- **Failure modes:**\n{_bullets(item['failure_modes'])}\n"
        f"- **JD evidence:** {item['jd_evidence']}"
        for i, item in enumerate(contract["expensive_problem_map"], start=1)
    )

    performance = "\n".join(
        f"- **{item['requirement']}** _(source: {item['source']})_ — {item['why_it_matters']}"
        for item in contract["performance_requirements"]
    )

    keywords = "\n\n".join(
        f"### `{item['surface_keyword']}` → {item['deep_skill_or_principle']}\n"
        f"- **Engineering pain behind it:** {item['engineering_pain_behind_it']}\n"
        f"- **Danger of learning in isolation:** {item['danger_of_learning_it_in_isolation']}"
        for item in contract["surface_keywords_vs_deep_skills"]
    )

    intuition = "\n\n".join(
        f"### {item['intuition']}\n"
        f"- **Profile anchor:** {item['profile_anchor']}\n"
        f"- **Role relevance:** {item['role_relevance']}\n"
        f"- **Why this is not yet software evidence:** {item['why_this_is_not_yet_software_evidence']}"
        for item in transfer["transferable_intuition"]
    )

    missing_ev = "\n\n".join(
        f"### Gap: {item['gap']}\n"
        f"- **Why it blocks credibility:** {item['why_it_blocks_credibility']}\n"
        f"- **Artifact required:** {item['artifact_required']}\n"
        f"- **First mental model to build:** {item['first_mental_model_to_build']}"
        for item in transfer["missing_evidence"]
    )

    missing_mm = "\n\n".join(
        f"### {item['mental_model']}\n"
        f"- **Why required before role work:** {item['why_required_before_role_work']}\n"
        f"- **What goes wrong without it:** {item['what_goes_wrong_without_it']}\n"
        f"- **First investigation that builds it:** {item['first_investigation_that_builds_it']}"
        for item in contract["missing_mental_models"]
    )

    threshold = "\n\n".join(
        f"### [{item['capability_scope']}] {item['capability']}\n"
        f"- **Why it matters generally:** {item['why_it_matters_generally']}\n"
        f"- **Connected role problem:** {item['connected_role_problem']}\n"
        f"- **Artifact evidence required:** {item['artifact_evidence_required']}\n"
        f"- **Transferable intuition note:** {item['transferable_intuition_note']}"
        for item in contract["general_engineering_value_threshold"]
    )

    deps = "\n\n".join(
        f"### {i}. {item['skill_or_model']}\n"
        f"- **Depends on:** {', '.join(item['depends_on']) if item['depends_on'] else '_none_'}\n"
        f"- **Unlocks:** {', '.join(item['unlocks']) if item['unlocks'] else '_none_'}\n"
        f"- **Why before later work:** {item['why_it_comes_before_later_work']}"
        for i, item in enumerate(contract["skill_dependency_graph"], start=1)
    )

    roadmap_parts: list[str] = []
    for i, item in enumerate(contract["investigation_roadmap"], start=1):
        techs = item["technologies_involved"]
        if techs:
            tech_block = "\n".join(
                f"- **{t['technology']}** — pain: {t['engineering_pain_it_solves']}"
                for t in techs
            )
        else:
            tech_block = "_None yet — understand the pain before introducing tools._"

        roadmap_parts.append(
            f"### Investigation {i}: {item['title']}\n"
            f"**Track:** `{item['track']}`\n\n"
            f"**Expensive problem:** {item['expensive_problem']}\n\n"
            f"**Engineering question:** {item['engineering_question']}\n\n"
            f"**Why this matters for the role:** {item['why_matters_for_role']}\n\n"
            f"#### Phase 0 — Mental model\n\n{item['phase_0_mental_model']}\n\n"
            f"#### Visual system model\n\n{item['visual_system_model']}\n\n"
            f"**Subquestions**\n{_bullets(item['subquestions'])}\n\n"
            f"**Concepts and vocabulary**\n{_bullets(item['concepts_and_vocabulary'])}\n\n"
            f"**Engineering principles**\n{_bullets(item['engineering_principles'])}\n\n"
            f"**Technologies involved**\n{tech_block}\n\n"
            f"**Observe first:** {item['observe_first']}\n\n"
            f"**Build or modify:** {item['build_or_modify']}\n\n"
            f"**Intentionally break / debug:** {item['intentionally_break_debug']}\n\n"
            f"**Improve:** {item['improve']}\n\n"
            f"**GitHub evidence:** {item['github_evidence']}\n\n"
            f"**Obsidian Engineering Page:** {item['obsidian_engineering_page']}\n\n"
            f"**Two-minute explanation target:** {item['two_minute_explanation_target']}\n\n"
            f"**Exit criteria**\n{_bullets(item['exit_criteria'])}\n\n"
            f"**Builds on prior artifact:** {item['builds_on_prior_artifact']}\n\n"
            f"**Module / folder added to cumulative system:** `{item.get('module_or_folder_added', '')}`\n\n"
            f"**Artifact this investigation produces:** {item['artifact_this_investigation_produces']}\n\n"
            f"**Delta from previous investigation:** {item.get('delta_from_previous_investigation', '')}\n\n"
            f"**Capstone delta:** {item.get('capstone_delta', '')}"
        )
    roadmap = "\n\n".join(roadmap_parts)

    cumulative = contract["cumulative_system"]
    growth = "\n".join(
        f"{g['investigation_number']}. Investigation {g['investigation_number']} adds "
        f"`{g['folder_or_module_added']}` — {g['capability_added']} "
        f"({g['why_it_matters']}). Evidence: {g['evidence_created']}"
        for g in sorted(
            cumulative.get("repo_growth_model") or [],
            key=lambda x: x.get("investigation_number", 0),
        )
    )

    ladder = "\n\n".join(
        f"### Level {item['level']} — {item['title']}\n\n"
        f"- **Same system:** `{item['same_system_name']}`\n"
        f"- **Module added:** `{item['module_or_folder_added']}`\n"
        f"- **Extends previous:** {item['extends_previous']}\n"
        f"- **New capability:** {item['new_capability_added']}\n"
        f"- **New proof:** {item['what_new_proof_it_creates']}\n"
        f"- **Why not separate project:** {item['why_this_is_not_a_separate_project']}\n"
        f"- **Evidence:**\n{_bullets(item['evidence'])}\n"
        f"- **Connected investigations:** {', '.join(item['connected_investigations'])}"
        for item in sorted(contract["proof_of_work_ladder"], key=lambda x: x["level"])
    )

    github = evidence.get("github_repository") or {}
    github_block = (
        f"**Repo:** `{github.get('repo_name', '')}`\n\n"
        f"**Purpose:** {github.get('repo_purpose', '')}\n\n"
        f"**Final folder structure:**\n\n```text\n{github.get('final_folder_structure', '')}\n```\n\n"
        f"**Evidence files**\n{_bullets(github.get('evidence_files') or [])}"
    )

    interviews = "\n\n".join(
        f"### {item['expectation']}\n"
        f"- **Current readiness:** {item['current_readiness']}\n"
        f"- **Evidence needed:** {item['evidence_needed']}\n"
        f"- **Likely interview challenge:** {item['likely_interview_challenge']}\n"
        f"- **How to answer after roadmap:** {item['how_to_answer_after_roadmap']}"
        for item in contract["interview_readiness_map"]
    )

    return f"""# Project Lambda — Role-to-Roadmap

_Generated by Project Lambda · {generated_at}_  
_Job source:_ `{job_source}` · _Profile source:_ `{profile_source}`

## Cumulative System

**Repo:** `{cumulative['suggested_repo_name']}`

**System name:** `{cumulative['system_name']}`

**Purpose:** {cumulative['system_purpose']}

**Why this system matches the role:** {cumulative['why_this_system_matches_the_role']}

**Starting scope:** {cumulative['starting_scope']}

**Final capstone shape:** {cumulative['final_capstone_shape']}

### How it grows

{growth}

## 1. Role interpretation

**{role['one_liner']}**

**Real mission:** {role['real_mission']}

**What success looks like:** {role['what_success_looks_like']}

**What this role is not**
{_bullets(role['what_this_role_is_not'])}

## 2. Expensive problem map

{problems}

## 3. Performance requirements

{performance}

## 4. Surface keywords vs deep skills

{keywords}

## 5. Candidate transfer map

### Transferable intuition (not evidence)

{intuition}

### Missing evidence (artifacts required)

{missing_ev}

### Misleading overclaims to avoid

{_bullets(transfer['misleading_overclaims_to_avoid'])}

### Strongest positioning angle

{transfer['strongest_positioning_angle']}

## 6. Missing mental models

{missing_mm}

## 7. General engineering value threshold

{threshold}

## 8. Skill dependency graph

{deps}

## 9. Roadmap tracks

### General engineering track

{_bullets(tracks['general_engineering_track'])}

### Role-specific track

{_bullets(tracks['role_specific_track'])}

## 10. Investigation roadmap

{roadmap}

## 11. Proof-of-work ladder

{ladder}

## 12. First investigation prompt

**Expensive problem:** {first['expensive_problem']}

**Engineering question:** {first['engineering_question']}

### Phase 0 — Mental model

{first['phase_0_mental_model']}

### Visual system model

{first['visual_system_model']}

**Subquestions**
{_bullets(first['subquestions'])}

**Concepts and vocabulary**
{_bullets(first['concepts_and_vocabulary'])}

**Observe first:** {first['observe_first']}

**Build or modify:** {first['build_or_modify']}

**Intentionally break / debug:** {first['intentionally_break_debug']}

**Improve:** {first['improve']}

**GitHub evidence:** {first['github_evidence']}

**Obsidian Engineering Page:** {first['obsidian_engineering_page']}

**Two-minute explanation target:** {first['two_minute_explanation_target']}

**Exit criteria**
{_bullets(first['exit_criteria'])}

### Ready to paste

```text
{first['ready_to_paste_prompt']}
```

## 13. Evidence plan

**Obsidian pages**
{_bullets(evidence['obsidian_pages'])}

### One GitHub repository

{github_block}

**Diagrams**
{_bullets(evidence['diagrams'])}

**Benchmarks or logs**
{_bullets(evidence['benchmarks_or_logs'])}

**README sections**
{_bullets(evidence['readme_sections'])}

**Interview artifacts**
{_bullets(evidence['interview_artifacts'])}

## 14. Interview readiness map

{interviews}

## 15. Guardrail checks

- **Inv 1 avoids Docker/K8s/Prometheus/Redfish:** {_yes_no(guards['investigation_1_avoids_docker_k8s_prometheus_redfish'])}
- **Inv 1 is software portability:** {_yes_no(guards['investigation_1_is_software_portability'])}
- **Docker only after portability pain:** {_yes_no(guards['docker_appears_only_after_portability_pain'])}
- **Mental models layered (not one-liners):** {_yes_no(guards['mental_models_are_layered_not_one_liners'])}
- **Background not treated as software evidence:** {_yes_no(guards['background_not_treated_as_software_evidence'])}
- **Capstone is last:** {_yes_no(guards['capstone_is_last'])}
- **Technologies tied to engineering pain:** {_yes_no(guards['technologies_tied_to_engineering_pain'])}
- **One cumulative system (not many repos):** {_yes_no(guards.get('one_cumulative_system_not_many_repos', False))}

**Notes**
{_bullets(guards['notes'])}
"""


def default_output_path(outputs_dir: Path, stem: str = "roadmap") -> Path:
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    return outputs_dir / f"{stem}_{stamp}.md"


def write_markdown(markdown: str, path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(markdown, encoding="utf-8")
    return path
