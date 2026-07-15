"""Semantic validation for Project Lambda Role-to-Roadmap outputs.

Reject misleading roadmaps after JSON generation and before Markdown rendering.
Does not auto-fix or retry — collect all failures and raise clearly.
"""

from __future__ import annotations

import re
from typing import Any

EARLY_INFRA_TERMS = (
    "docker",
    "kubernetes",
    "k8s",
    "prometheus",
    "grafana",
    "redfish",
    "bmc",
    "ipmi",
)

PORTABILITY_TERMS = (
    "portability",
    "environment mismatch",
    "runs on another machine",
    "another machine",
    "runtime",
    "dependencies",
    "configuration",
    "filesystem",
    "operating system",
    "between machines",
    "across machines",
    "across different environments",
)

CAUSAL_LAYER_WORDS = (
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

VISUAL_SIGNS = (
    "→",
    "->",
    "layer",
    "flow",
    "pipeline",
    "state",
    "diagram",
    "sketch",
    "stage",
    "boxes",
    "arrow",
)

GENERIC_PAIN_PHRASES = (
    "used for development",
    "helps with automation",
    "industry standard",
    "needed for this role",
    "important for the role",
    "commonly used",
    "widely used",
    "best practice",
)

BACKGROUND_AS_EVIDENCE_PHRASES = (
    "experience with",
    "background in",
    "familiarity with",
    "worked around",
    "exposure to",
    "proven by experience",
    "proven by field",
    "industrial experience",
)

ARTIFACT_TERMS = (
    "github",
    "repo",
    "repository",
    "readme",
    "log",
    "benchmark",
    "diagram",
    "failure table",
    "failure mode",
    "test output",
    "verification log",
    "postmortem",
    "demo",
    "script",
    "shell",
    "artifact",
    "note",
)

CAPSTONE_EARLY_TERMS = (
    "capstone",
    "final pipeline",
    "gpu repair pipeline simulation",
    "full repair pipeline",
    "end-to-end gpu repair",
)


class ValidationError(Exception):
    """Raised when a roadmap violates Project Lambda semantic rules."""


def _lower(text: str | None) -> str:
    return (text or "").lower()


def _join_fields(item: dict[str, Any], fields: tuple[str, ...]) -> str:
    parts: list[str] = []
    for field in fields:
        value = item.get(field)
        if isinstance(value, str):
            parts.append(value)
        elif isinstance(value, list):
            parts.extend(str(v) for v in value)
        elif isinstance(value, dict):
            parts.append(str(value))
    return " ".join(parts)


def _contains_any(text: str, terms: tuple[str, ...]) -> list[str]:
    found: list[str] = []
    lower = text.lower()
    for term in terms:
        if term.lower() in lower:
            found.append(term)
    return found


def _count_causal_words(text: str) -> int:
    lower = text.lower()
    return sum(1 for word in CAUSAL_LAYER_WORDS if word in lower)


def _has_visual_sign(text: str) -> bool:
    lower = text.lower()
    if "\n" in text and any(ch.isdigit() for ch in text):
        return True
    if re.search(r"\b\d+[.)]\s", text):
        return True
    return any(sign.lower() in lower for sign in VISUAL_SIGNS)


def _is_generic_pain(pain: str) -> bool:
    lower = pain.strip().lower()
    if len(lower) < 40:
        return True
    return any(phrase in lower for phrase in GENERIC_PAIN_PHRASES)


def _artifact_evidence_ok(text: str) -> bool:
    """Background phrases are OK only if concrete artifacts are also named."""
    lower = text.lower()
    has_background = any(p in lower for p in BACKGROUND_AS_EVIDENCE_PHRASES)
    if not has_background:
        return True
    return any(a in lower for a in ARTIFACT_TERMS)


def _inv1_blob(inv1: dict[str, Any], first_prompt: dict[str, Any] | None) -> str:
    chunks = [
        _join_fields(
            inv1,
            (
                "title",
                "expensive_problem",
                "engineering_question",
                "observe_first",
                "build_or_modify",
                "intentionally_break_debug",
                "improve",
                "phase_0_mental_model",
                "visual_system_model",
            ),
        )
    ]
    techs = inv1.get("technologies_involved") or []
    for tech in techs:
        if isinstance(tech, dict):
            chunks.append(str(tech.get("technology", "")))
            chunks.append(str(tech.get("engineering_pain_it_solves", "")))
        else:
            chunks.append(str(tech))
    if first_prompt:
        chunks.append(_join_fields(
            first_prompt,
            (
                "ready_to_paste_prompt",
                "expensive_problem",
                "engineering_question",
                "phase_0_mental_model",
                "observe_first",
                "build_or_modify",
                "intentionally_break_debug",
                "improve",
            ),
        ))
    return " ".join(chunks)


def _portability_without_docker(inv: dict[str, Any]) -> bool:
    blob = _lower(
        _join_fields(
            inv,
            ("title", "engineering_question", "expensive_problem", "phase_0_mental_model"),
        )
    )
    if "docker" in blob:
        return False
    return bool(_contains_any(blob, PORTABILITY_TERMS))


def validate_roadmap(data: dict[str, Any]) -> None:
    """Validate a generated roadmap. Raises ValidationError with all failures."""
    failures: list[str] = []

    investigations = data.get("investigation_roadmap") or []
    if not isinstance(investigations, list) or not investigations:
        raise ValidationError(
            "Project Lambda validation failed:\n"
            "- investigation_roadmap is missing or empty."
        )

    first_prompt = data.get("first_investigation_prompt") or {}
    inv1 = investigations[0]

    # 1. Investigation 1 must not start with advanced infra tools
    inv1_text = _inv1_blob(inv1, first_prompt if isinstance(first_prompt, dict) else None)
    early_hits = _contains_any(inv1_text, EARLY_INFRA_TERMS)
    if early_hits:
        failures.append(
            "Investigation 1 introduces advanced infrastructure tools too early: "
            + ", ".join(sorted(set(early_hits)))
            + "."
        )

    # 2. Investigation 1 should be about software portability
    port_hits = _contains_any(inv1_text, PORTABILITY_TERMS)
    if not port_hits:
        failures.append(
            "Investigation 1 is not about software portability / environment mismatch "
            "(expected terms like portability, runtime, dependencies, configuration, "
            "filesystem, operating system, or between machines)."
        )

    # 3 & 4. Phase 0 mental model + visual system model for every investigation
    for i, inv in enumerate(investigations, start=1):
        title = inv.get("title", f"Investigation {i}")
        mm = inv.get("phase_0_mental_model") or ""
        if not isinstance(mm, str) or len(mm.strip()) < 300:
            failures.append(
                f"Investigation {i} ({title}) has a shallow or missing Phase 0 mental model "
                f"(need >=300 characters)."
            )
        elif _count_causal_words(mm) < 2:
            failures.append(
                f"Investigation {i} ({title}) Phase 0 mental model lacks causal/layer "
                "language (need >=2 of: because, depends, layer, failure, assumption, "
                "runtime, dependency, environment, signal, state)."
            )

        visual = inv.get("visual_system_model") or ""
        if not isinstance(visual, str) or len(visual.strip()) < 80:
            failures.append(
                f"Investigation {i} ({title}) has a missing or too-short visual_system_model "
                f"(need >=80 characters)."
            )
        elif not _has_visual_sign(visual):
            failures.append(
                f"Investigation {i} ({title}) visual_system_model lacks flow/layer language "
                "(expected ->, stages, layer, flow, pipeline, state, etc.)."
            )

        # 5. Technologies must include engineering pain
        techs = inv.get("technologies_involved") or []
        if not isinstance(techs, list):
            failures.append(
                f"Investigation {i} ({title}) technologies_involved must be a list of objects."
            )
        else:
            for j, tech in enumerate(techs, start=1):
                if not isinstance(tech, dict):
                    failures.append(
                        f"Investigation {i} ({title}) technology #{j} must be an object "
                        "with technology + engineering_pain_it_solves."
                    )
                    continue
                name = tech.get("technology")
                pain = tech.get("engineering_pain_it_solves")
                if not name or not isinstance(name, str):
                    failures.append(
                        f"Investigation {i} ({title}) technology #{j} missing 'technology'."
                    )
                if not pain or not isinstance(pain, str):
                    failures.append(
                        f"Investigation {i} ({title}) technology #{j} missing "
                        "'engineering_pain_it_solves'."
                    )
                elif _is_generic_pain(pain):
                    failures.append(
                        f"Investigation {i} ({title}) technology '{name}' has generic "
                        "engineering_pain_it_solves (explain the actual engineering problem)."
                    )

    # 6. Docker ordering: Docker must not precede a portability-without-Docker investigation
    docker_indices: list[int] = []
    portability_indices: list[int] = []
    for i, inv in enumerate(investigations):
        blob = _lower(
            _join_fields(
                inv,
                (
                    "title",
                    "engineering_question",
                    "expensive_problem",
                    "observe_first",
                    "build_or_modify",
                ),
            )
        )
        tech_blob = " ".join(
            _lower(t.get("technology", "")) if isinstance(t, dict) else _lower(str(t))
            for t in (inv.get("technologies_involved") or [])
        )
        combined = blob + " " + tech_blob
        if "docker" in combined:
            docker_indices.append(i)
        if _portability_without_docker(inv):
            portability_indices.append(i)

    if 0 in docker_indices:
        failures.append("Docker should not be Investigation 1.")
    if docker_indices:
        first_docker = min(docker_indices)
        prior_portability = [i for i in portability_indices if i < first_docker]
        if not prior_portability:
            failures.append(
                "Docker appears before an investigation that covers local portability / "
                "environment mismatch without Docker."
            )

    # 7. Capstone must come late (not in first 3; must be in last 20%)
    n = len(investigations)
    early_cutoff = min(3, n)
    late_start = max(0, int(n * 0.8))  # last 20%
    for i, inv in enumerate(investigations):
        blob = _lower(_join_fields(inv, ("title", "engineering_question", "expensive_problem")))
        hits = _contains_any(blob, CAPSTONE_EARLY_TERMS)
        if not hits:
            # also catch "gpu repair pipeline" loosely in early slots
            if i < early_cutoff and (
                "gpu repair pipeline" in blob or "repair pipeline simulation" in blob
            ):
                hits = ["gpu repair pipeline simulation"]
        if hits and i < early_cutoff:
            failures.append(
                f"Capstone/final pipeline terms appear too early in Investigation {i + 1} "
                f"({inv.get('title', '')}): {', '.join(sorted(set(hits)))}."
            )
        if hits and i < late_start and i >= early_cutoff:
            # Capstone-like investigation should live in the final 20%
            failures.append(
                f"Capstone/final simulation '{inv.get('title', '')}' appears before the "
                f"last 20% of investigations (index {i + 1}/{n})."
            )

    # 8. Background must not be treated as software evidence
    evidence_fields: list[tuple[str, str]] = []
    for item in data.get("general_engineering_value_threshold") or []:
        if isinstance(item, dict):
            evidence_fields.append(
                (
                    f"general_engineering_value_threshold:{item.get('capability', '?')}",
                    str(item.get("artifact_evidence_required") or ""),
                )
            )
    transfer = data.get("candidate_transfer_map") or {}
    for item in transfer.get("missing_evidence") or []:
        if isinstance(item, dict):
            evidence_fields.append(
                (
                    f"missing_evidence:{item.get('gap', '?')}",
                    str(item.get("artifact_required") or ""),
                )
            )
    for item in data.get("interview_readiness_map") or []:
        if isinstance(item, dict):
            evidence_fields.append(
                (
                    f"interview_readiness:{item.get('expectation', '?')[:60]}",
                    str(item.get("evidence_needed") or ""),
                )
            )

    for label, text in evidence_fields:
        if text and not _artifact_evidence_ok(text):
            failures.append(
                f"Candidate evidence treats background experience as proof without "
                f"artifacts ({label})."
            )

    # 9. Tracks must be separated
    tracks = data.get("roadmap_tracks") or {}
    general_track = tracks.get("general_engineering_track") or []
    role_track = tracks.get("role_specific_track") or []
    if not general_track:
        failures.append("roadmap_tracks.general_engineering_track is empty.")
    if not role_track:
        failures.append("roadmap_tracks.role_specific_track is empty.")

    track_labels = [
        str(inv.get("track", "")).strip().lower()
        for inv in investigations
        if isinstance(inv, dict)
    ]
    unique_tracks = {t for t in track_labels if t}
    if unique_tracks and unique_tracks <= {"general"}:
        failures.append("All investigations are marked only 'general' — role_specific missing.")
    if unique_tracks and unique_tracks <= {"role_specific"}:
        failures.append("All investigations are marked only 'role_specific' — general missing.")

    # 10. First investigation prompt must be paste-ready
    if not isinstance(first_prompt, dict):
        failures.append("first_investigation_prompt is missing.")
    else:
        ready = first_prompt.get("ready_to_paste_prompt") or ""
        if not isinstance(ready, str) or len(ready.strip()) < 1000:
                failures.append(
                    "first_investigation_prompt.ready_to_paste_prompt is missing or too short "
                    "(need >=1000 characters)."
                )
        else:
            ready_l = ready.lower()
            required_bits = (
                ("phase 0", "phase 0"),
                ("mental model", "mental model"),
                ("observe", "observe"),
                ("build", "build"),
                ("break", "break"),
                ("improve", "improve"),
                ("github", "GitHub evidence"),
                ("obsidian", "Obsidian evidence"),
            )
            missing_bits = [label for key, label in required_bits if key not in ready_l]
            if missing_bits:
                failures.append(
                    "first_investigation_prompt.ready_to_paste_prompt is missing required "
                    "sections: " + ", ".join(missing_bits) + "."
                )
            if "docker" in ready_l:
                failures.append(
                    "first_investigation_prompt.ready_to_paste_prompt includes Docker "
                    "(forbidden for Investigation 1)."
                )

    if failures:
        bullet = "\n".join(f"- {f}" for f in failures)
        raise ValidationError(f"Project Lambda validation failed:\n{bullet}")
