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
    "host",
    "image",
    "container",
    "component",
    "gateway",
    "queue",
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

FORBIDDEN_SYSTEM_NAMES = (
    "software portability",
    "python automation",
    "docker project",
    "api project",
    "docker setup",
    "health check project",
)

ROLE_SHAPED_SYSTEM_WORDS = (
    "fleet",
    "repair",
    "compute",
    "gpu",
    "ops",
    "health",
    "infrastructure",
    "telemetry",
    "inference",
    "serving",
    "model",
    "latency",
    "platform",
    "reliability",
)

ALLOWED_ROLE_FAMILIES = (
    "ai_infrastructure_model_serving",
    "gpu_fleet_production_engineering",
    "backend_platform_engineering",
    "robotics_systems",
    "embedded_ai",
    "cloud_infrastructure",
    "controls_automation_software",
    "data_center_compute_infrastructure",
    "general_systems_software",
)

# JD must support these before BMC/Redfish/IPMI investigations are allowed.
JD_HARDWARE_TOOLING_SIGNALS = (
    "redfish",
    "bmc",
    "ipmi",
    "firmware-level",
    "firmware level",
    "firmware telemetry",
    "bare metal",
    "hardware lifecycle",
    "hardware qualification",
    "physical repair",
    "physical fleet",
    "rma",
    "repair pipeline",
    "parts management",
)

# JD must support these before GPU repair pipeline simulation is allowed.
JD_REPAIR_PIPELINE_SIGNALS = (
    "repair pipeline",
    "repair",
    "rma",
    "return to service",
    "return-to-service",
    "fleet health",
    "hardware failure",
    "bare metal repair",
    "physical repair",
    "gpu failure",
    "triage",
    "parts management",
    "fault detection",
)

FLEET_REPAIR_OUTPUT_TERMS = (
    "bmc",
    "redfish",
    "ipmi",
    "gpu repair pipeline",
    "repair pipeline simulation",
    "hardware fleet repair",
    "repair state machine",
    "fleet repair",
)

MODEL_SERVING_ROLE_TERMS = (
    "model serving",
    "inference",
    "latency",
    "throughput",
    "batching",
    "queue",
    "p50",
    "p95",
    "p99",
    "load test",
    "cold start",
    "token",
    "vllm",
    "triton",
)

MODEL_SERVING_SYSTEM_TERMS = (
    "inference",
    "serving",
    "model-serving",
    "model_serving",
    "ai-inference",
    "ai_inference",
    "reliability",
)

FLEET_SYSTEM_TERMS = (
    "fleet",
    "repair",
    "compute-fleet",
    "gpu-fleet",
)

UNMEASURABLE_PROPOSED_METRIC_PHRASES = (
    "user satisfaction",
    "customer satisfaction",
    "revenue",
    "nps",
    "business kpi",
    "business outcome",
    "six-month",
    "6 month",
    "6-month",
    "first 6 months",
    "within the first 6 months",
    "org target",
    "stakeholder happiness",
)

PROJECT_MEASURABLE_METRIC_TERMS = (
    "latency",
    "p50",
    "p95",
    "p99",
    "throughput",
    "requests/sec",
    "req/s",
    "request count",
    "error rate",
    "queue depth",
    "batch size",
    "gpu utilization",
    "cpu",
    "memory",
    "cold start",
    "mttd",
    "mttr",
    "return to service",
    "return-to-service",
    "false positive",
    "false negative",
    "telemetry freshness",
    "escalation rate",
    "alert noise",
    "pass rate",
    "health check",
    "successful health",
    "qualification",
    "first attempt",
    "accurate",
    "actionable",
    "fleet health",
    "repair queue",
    "incident response",
    "manual intervention",
    "visibility",
    "trigger",
    "resolution time",
    "incident resolution",
    "repair workflow",
    "successfully executed",
    "automated repair",
    "workflows successfully",
)

OBSERVABILITY_MENTAL_MODEL_TERMS = (
    "observability",
    "metrics",
    "alerting",
    "alert",
    "health check",
    "monitoring",
    "telemetry",
)

API_INVESTIGATION_MARKERS = (
    "expose api",
    "expose apis",
    "services expose",
    "why do services expose",
)

ROLE_SPECIFIC_ONLY_TERMS = (
    "hardware telemetry",
    "redfish",
    "bmc",
    "ipmi",
    "gpu repair",
    "fleet repair",
    "gpu qualification",
    "repair pipeline",
    "fleet health",
    "fleet ops",
    "repair become a state",
    "repair state machine",
)

# Hard role/hardware terms that must never appear on a general investigation.
# Broader "repair*" language can appear as foreshadowing in early mental models.
GENERAL_TRACK_FORBIDDEN = (
    "hardware telemetry",
    "redfish",
    "bmc",
    "ipmi",
    "gpu repair",
    "fleet repair",
    "gpu qualification",
    "repair pipeline",
    "mocked redfish",
    "mocked bmc",
)

CAPSTONE_EARLY_TERMS = (
    "capstone",
    "final pipeline",
    "end-to-end gpu repair",
)

# Role-specific pipeline sims may appear before the final capstone verification.
# Only reject these when they appear in the first few investigations.
PIPELINE_SIM_EARLY_ONLY = (
    "gpu repair pipeline simulation",
    "full repair pipeline",
    "repair pipeline simulation",
)

CAPSTONE_DELTA_TERMS = (
    "verification",
    "failure injection",
    "mttd",
    "mttr",
    "false positive",
    "escalat",
    "postmortem",
    "incident",
    "measurement",
    "benchmark",
)

ABSOLUTE_AUTOMATION_PHRASES = (
    "fully automated",
    "fully-automated",
    "no humans needed",
    "no human needed",
    "complete automation",
    "automated everything",
    "automate everything",
    "without any human",
    "zero human",
)

AUTOMATION_BOUNDARY_PAIRS = (
    "escalat",
    "human",
    "fail-closed",
    "fail closed",
    "approval",
    "boundary",
    "common path",
    "common-path",
    "manual",
)

OPS_METRIC_TERMS = (
    "mttd",
    "mttr",
    "return to service",
    "return-to-service",
    "time to return",
    "mean time",
    "false positive",
    "false negative",
    "escalation rate",
    "queue depth",
    "telemetry freshness",
    "alert noise",
)

DOCKER_ARTIFACT_TERMS = (
    "dockerfile",
    "docker-compose",
    "docker compose",
    "containerization",
    "docker-portability",
    "docker_portability",
    "containerization-tradeoffs",
    "containerization_tradeoffs",
)

ALLOWED_METRIC_SOURCES = (
    "stated_in_jd",
    "implied_by_jd",
    "proposed_project_target",
)

# Legacy / prose source labels that mean "stated in JD"
STATED_IN_JD_ALIASES = (
    "stated_in_jd",
    "stated in jd",
    "stated in the jd",
    "stated in job description",
    "from the jd",
    "explicit in jd",
)

PROPOSED_TARGET_ALIASES = (
    "proposed_project_target",
    "proposed project target",
    "proposed project bar",
    "proposed project bar (not an employer requirement)",
    "project target",
    "project bar",
)

IMPLIED_ALIASES = (
    "implied_by_jd",
    "implied by jd",
    "likely implied",
    "implied",
)

HARDWARE_TOOLING_TERMS = (
    "redfish",
    "bmc",
    "ipmi",
)

VAGUE_INV1_BUILD_PHRASES = (
    "create a simple application",
    "build a simple application",
    "create a basic application",
    "build a basic app",
    "create a simple app",
    "build a simple project",
    "create a simple project",
    "make a simple application",
    "write a simple application",
)

MACHINE_REPORT_TERMS = (
    "machine-report",
    "machine_report",
    "machinereport",
)

MACHINE_REPORT_CONCRETE_BITS = (
    "python version",
    "app_env",
    "environment variable",
    "env var",
    "output/report.txt",
    "report.txt",
)

FAKE_ACHIEVEMENT_PHRASES = (
    "i successfully validated",
    "successfully validated",
    "mttd was consistently under",
    "mttr was maintained below",
    "mttr was consistently under",
    "mttd was under",
    "mttr was under",
    "i built",
    "i proved",
    "i achieved",
    "i demonstrated that",
    "was consistently under",
    "was maintained below",
)

FUTURE_FRAMING_PHRASES = (
    "after completing",
    "should be able to say",
    "candidate should",
    "target measurement",
    "target:",
    "evidence to produce",
    "final readout should",
    "will be able to",
    "once complete",
    "upon completion",
    "template",
    "future script",
    "planned readout",
)

# JD must treat containers as a primary role-specific duty to allow Docker on role_specific
CONTAINER_PRIMARY_DUTY_PATTERNS = (
    r"own\s+.*\b(docker|container)\b",
    r"\bcontainer infrastructure\b",
    r"\bcontainer platform\b",
    r"primary.*\b(docker|containerization)\b",
    r"\bdocker\b.*\b(primary|own|responsible)\b",
)


class ValidationError(Exception):
    """Raised when a roadmap violates Project Lambda semantic rules."""


def _lower(text: str | None) -> str:
    return (text or "").lower()


def _norm_path(path: str) -> str:
    """Normalize module/folder paths for comparison."""
    p = _lower(path).strip().replace("\\", "/")
    p = re.sub(r"/+", "/", p)
    return p.rstrip("/")


def _modules_align(a: str, b: str) -> bool:
    """True if two module/folder paths refer to the same addition."""
    na, nb = _norm_path(a), _norm_path(b)
    if not na or not nb:
        return False
    if na == nb:
        return True
    # Identical leaf file/folder name (not bare top-level dirs)
    a_parts = [p for p in na.split("/") if p]
    b_parts = [p for p in nb.split("/") if p]
    if not a_parts or not b_parts:
        return False
    if a_parts[-1] == b_parts[-1] and a_parts[-1] not in {
        "src",
        "docs",
        "tests",
        "outputs",
    }:
        return True
    return False


def _is_vague_module(path: str) -> bool:
    p = _norm_path(path)
    return p in {"", "src", "docs", "tests", "outputs", "lib", "app"}


def _norm_title(title: str) -> str:
    t = _lower(title)
    t = re.sub(r"[^a-z0-9\s/+-]", " ", t)
    t = re.sub(r"\s+", " ", t).strip()
    return t


def _titles_align(a: str, b: str) -> bool:
    """True if titles refer to the same investigation topic."""
    na, nb = _norm_title(a), _norm_title(b)
    if not na or not nb:
        return False
    if na == nb:
        return True
    if na in nb or nb in na:
        return True
    # Significant token overlap (ignore short stopwords); allow simple stems
    stop = {
        "how", "why", "does", "do", "a", "an", "the", "and", "or", "to", "of",
        "in", "for", "with", "what", "when", "still", "need", "needs", "between",
    }

    def tokens(text: str) -> set[str]:
        out: set[str] = set()
        for w in text.split():
            if len(w) <= 2 or w in stop:
                continue
            out.add(w)
            if w.endswith("s") and len(w) > 4:
                out.add(w[:-1])
            if w.endswith("ing") and len(w) > 5:
                out.add(w[:-3])
        return out

    ta, tb = tokens(na), tokens(nb)
    if not ta or not tb:
        return False
    overlap = ta & tb
    return len(overlap) >= min(2, min(len(ta), len(tb)))


def _track_entry_matches_investigation(entry: str, inv: dict[str, Any]) -> bool:
    """Whether a roadmap_tracks entry corresponds to an investigation."""
    title = str(inv.get("title") or "")
    blob = _norm_title(
        " ".join(
            [
                title,
                str(inv.get("engineering_question") or ""),
                str(inv.get("expensive_problem") or ""),
                str(inv.get("module_or_folder_added") or ""),
            ]
        )
    )
    entry_n = _norm_title(entry)
    if not entry_n or not blob:
        return False
    if entry_n in blob or blob in entry_n:
        return True
    if _titles_align(entry, title):
        return True
    stop = {"how", "why", "does", "do", "the", "and", "for", "with", "what"}
    entry_tokens = [tok for tok in entry_n.split() if len(tok) > 3 and tok not in stop]
    if not entry_tokens:
        entry_tokens = [tok for tok in entry_n.split() if len(tok) > 2]
    hits = sum(1 for tok in entry_tokens if tok in blob)
    # Match if half+ of meaningful entry tokens appear in the investigation blob
    return hits >= max(1, (len(entry_tokens) + 1) // 2)


def _normalize_metric_source(source: str) -> str | None:
    """Map freeform source labels to canonical enum, or None if unknown."""
    s = _lower(source).strip()
    if not s:
        return None
    if s in STATED_IN_JD_ALIASES or s.startswith("stated"):
        return "stated_in_jd"
    if s in IMPLIED_ALIASES or "implied" in s:
        return "implied_by_jd"
    if s in PROPOSED_TARGET_ALIASES or "proposed" in s or "project target" in s or "project bar" in s:
        return "proposed_project_target"
    return None


def _extract_numeric_thresholds(text: str) -> list[str]:
    """Pull numeric threshold tokens (numbers, percentages, time units) from text."""
    found: list[str] = []
    # e.g. 5 minutes, 30 min, <5, under 5, 99%, 6-month
    for m in re.finditer(
        r"\b\d+(?:\.\d+)?\s*(?:minutes?|mins?|seconds?|secs?|hours?|hrs?|ms|%|percent)?\b",
        text,
        flags=re.I,
    ):
        found.append(m.group(0).strip().lower())
    for m in re.finditer(r"(?:under|below|less than|<|>|<=)\s*\d+(?:\.\d+)?", text, flags=re.I):
        found.append(m.group(0).strip().lower())
    return found


def _number_token_in_jd(token: str, jd: str) -> bool:
    """Check whether the numeric core of a threshold appears in the JD."""
    jd_l = _lower(jd)
    nums = re.findall(r"\d+(?:\.\d+)?", token)
    if not nums:
        return True
    for num in nums:
        # Require the number as a whole token somewhere in JD
        if not re.search(rf"(?<!\d){re.escape(num)}(?!\d)", jd_l):
            return False
    return True


def _jd_has_container_primary_duty(jd: str) -> bool:
    jd_l = _lower(jd)
    return any(re.search(p, jd_l) for p in CONTAINER_PRIMARY_DUTY_PATTERNS)


def _jd_supports_hardware_tooling(jd: str) -> bool:
    return bool(_contains_any(jd, JD_HARDWARE_TOOLING_SIGNALS))


def _jd_supports_repair_pipeline(jd: str) -> bool:
    return bool(_contains_any(jd, JD_REPAIR_PIPELINE_SIGNALS))


def _infer_family_from_jd(jd: str) -> str | None:
    """Best-effort family hint from JD text for cross-checks."""
    if not jd.strip():
        return None
    jd_l = _lower(jd)
    if _jd_supports_hardware_tooling(jd) or (
        _jd_supports_repair_pipeline(jd)
        and any(t in jd_l for t in ("fleet", "bare metal", "gpu failure", "rma"))
    ):
        return "gpu_fleet_production_engineering"
    if any(
        t in jd_l
        for t in (
            "model serving",
            "inference",
            "vllm",
            "triton",
            "token throughput",
            "cold start",
            "latency budget",
            "$/token",
            "p95 inference",
        )
    ):
        return "ai_infrastructure_model_serving"
    return None


def _titles_exact(a: str, b: str) -> bool:
    return _norm_title(a) == _norm_title(b) and bool(_norm_title(a))


def _is_paragraph_track_item(text: str) -> bool:
    t = (text or "").strip()
    if len(t) > 120:
        return True
    if t.count(".") >= 2:
        return True
    if "\n" in t:
        return True
    return False


def _track_titles_exact_set(entries: list[Any]) -> list[str]:
    return [str(e).strip() for e in entries if str(e).strip()]


def _has_future_framing(text: str) -> bool:
    low = _lower(text)
    return any(p in low for p in FUTURE_FRAMING_PHRASES)


def _fake_achievement_hits(text: str) -> list[str]:
    low = _lower(text)
    return [p for p in FAKE_ACHIEVEMENT_PHRASES if p in low]


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


def validate_roadmap(
    data: dict[str, Any],
    job_description: str | None = None,
) -> None:
    """Validate a generated roadmap. Raises ValidationError with all failures.

    When job_description is provided, also enforce JD-anchored rules (metric
    sourcing, Redfish/BMC coverage, Docker role-specific exceptions).
    """
    failures: list[str] = []
    jd_text = job_description or ""

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
        capstone_hits = _contains_any(blob, CAPSTONE_EARLY_TERMS)
        pipeline_hits = _contains_any(blob, PIPELINE_SIM_EARLY_ONLY)
        if capstone_hits and i < early_cutoff:
            failures.append(
                f"Capstone/final pipeline terms appear too early in Investigation {i + 1} "
                f"({inv.get('title', '')}): {', '.join(sorted(set(capstone_hits)))}."
            )
        if capstone_hits and i < late_start and i >= early_cutoff:
            failures.append(
                f"Capstone/final simulation '{inv.get('title', '')}' appears before the "
                f"last 20% of investigations (index {i + 1}/{n})."
            )
        if pipeline_hits and i < early_cutoff:
            failures.append(
                f"Repair pipeline simulation appears too early in Investigation {i + 1} "
                f"({inv.get('title', '')}): {', '.join(sorted(set(pipeline_hits)))}."
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

    # 9. Tracks must be separated + track discipline
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
        failures.append("All investigations are marked only 'general' - role_specific missing.")
    if unique_tracks and unique_tracks <= {"role_specific"}:
        failures.append("All investigations are marked only 'role_specific' - general missing.")

    for label in general_track:
        hits = _contains_any(str(label), ROLE_SPECIFIC_ONLY_TERMS)
        if hits:
            failures.append(
                "roadmap_tracks.general_engineering_track contains role-specific topic "
                f"'{label}' ({', '.join(hits)}). Move to role_specific_track."
            )
    for inv in investigations:
        if str(inv.get("track", "")).lower() != "general":
            continue
        # Only reject clear role/hardware specialization on general track — title field.
        title = _lower(str(inv.get("title") or ""))
        hits = _contains_any(title, GENERAL_TRACK_FORBIDDEN)
        if hits:
            failures.append(
                f"Investigation '{inv.get('title', '')}' is marked general but includes "
                f"role-specific terms: {', '.join(sorted(set(hits)))}."
            )

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
            # Concrete machine-report project required (not vague build language)
            vague_hits = [p for p in VAGUE_INV1_BUILD_PHRASES if p in ready_l]
            has_machine_report = any(t in ready_l for t in MACHINE_REPORT_TERMS)
            concrete_bits = _contains_any(ready_l, MACHINE_REPORT_CONCRETE_BITS)
            build_blob = _lower(
                str(first_prompt.get("build_or_modify") or "")
                + " "
                + str(inv1.get("build_or_modify") or "")
                + " "
                + ready
            )
            if vague_hits and not has_machine_report:
                failures.append(
                    "Investigation 1 uses vague build language without a concrete "
                    f"machine-report project: {', '.join(vague_hits)}."
                )
            if not has_machine_report and not any(
                t in _lower(build_blob) for t in MACHINE_REPORT_TERMS
            ):
                # Also accept concrete bits without exact name if enough specifics present
                if len(concrete_bits) < 3 and len(
                    _contains_any(build_blob, MACHINE_REPORT_CONCRETE_BITS)
                ) < 3:
                    failures.append(
                        "Investigation 1 / first_investigation_prompt must specify a "
                        "concrete machine-report-style project (name machine-report / "
                        "machine_report, or include Python version check + required env "
                        "var + output/report.txt)."
                    )
            elif has_machine_report or any(
                t in _lower(build_blob) for t in MACHINE_REPORT_TERMS
            ):
                bits = _contains_any(build_blob, MACHINE_REPORT_CONCRETE_BITS)
                if len(bits) < 2:
                    failures.append(
                        "machine-report Investigation 1 is missing concrete requirements "
                        "(need at least two of: Python version check, APP_ENV / env var, "
                        "output/report.txt)."
                    )

    # 11. Cumulative system exists and is role-shaped
    cumulative = data.get("cumulative_system")
    if not isinstance(cumulative, dict):
        failures.append("cumulative_system is missing.")
    else:
        system_name = str(cumulative.get("system_name") or "").strip()
        suggested = str(cumulative.get("suggested_repo_name") or "").strip()
        if not system_name:
            failures.append("cumulative_system.system_name is missing.")
        if not suggested:
            failures.append("cumulative_system.suggested_repo_name is missing.")
        name_blob = _lower(system_name + " " + suggested)
        if any(bad == name_blob or bad in name_blob for bad in FORBIDDEN_SYSTEM_NAMES):
            failures.append(
                f"cumulative_system name '{system_name}' is too generic / syllabus-like "
                "(avoid Software Portability, Python Automation, Docker Project, API Project)."
            )
        if system_name and not any(w in name_blob for w in ROLE_SHAPED_SYSTEM_WORDS):
            failures.append(
                f"cumulative_system name '{system_name}' should be role-shaped "
                "(include words like fleet, repair, compute, GPU, ops, health, infrastructure)."
            )
        growth = cumulative.get("repo_growth_model") or []
        if not isinstance(growth, list) or len(growth) < 5:
            failures.append(
                "cumulative_system.repo_growth_model must list how the repo grows "
                "(>=5 module additions)."
            )

    # 12. Stable same_system_name + module growth on ladder
    ladder = data.get("proof_of_work_ladder") or []
    system_names: list[str] = []
    for i, level in enumerate(ladder, start=1):
        if not isinstance(level, dict):
            failures.append(f"proof_of_work_ladder item {i} must be an object.")
            continue
        same = str(level.get("same_system_name") or "").strip()
        if not same:
            failures.append(f"proof_of_work_ladder level {i} missing same_system_name.")
        else:
            system_names.append(same)
            if any(bad in same.lower() for bad in FORBIDDEN_SYSTEM_NAMES):
                failures.append(
                    f"proof_of_work_ladder level {i} uses forbidden/generic system name "
                    f"'{same}'."
                )
        module = str(level.get("module_or_folder_added") or "").strip()
        if not module:
            failures.append(
                f"proof_of_work_ladder level {i} missing module_or_folder_added."
            )
        capability = str(level.get("new_capability_added") or "").strip()
        if not capability:
            failures.append(
                f"proof_of_work_ladder level {i} missing new_capability_added."
            )
        why_not_sep = str(level.get("why_this_is_not_a_separate_project") or "").strip()
        if not why_not_sep:
            failures.append(
                f"proof_of_work_ladder level {i} missing why_this_is_not_a_separate_project."
            )

    if system_names and len(set(s.lower() for s in system_names)) > 1:
        failures.append(
            "proof_of_work_ladder same_system_name is not stable across levels: "
            + ", ".join(sorted(set(system_names)))
            + "."
        )
    if (
        isinstance(cumulative, dict)
        and system_names
        and str(cumulative.get("system_name") or "").strip()
    ):
        expected = str(cumulative.get("system_name")).strip().lower()
        if any(s.lower() != expected for s in system_names):
            failures.append(
                "proof_of_work_ladder.same_system_name must match "
                f"cumulative_system.system_name ('{cumulative.get('system_name')}')."
            )

    # 13. One-repo evidence plan (no multi-repo syllabus)
    evidence_plan = data.get("evidence_plan") or {}
    github = evidence_plan.get("github_repository") if isinstance(evidence_plan, dict) else None
    if not isinstance(github, dict):
        # legacy multi-repo field
        legacy = (
            evidence_plan.get("github_repos_or_folders")
            if isinstance(evidence_plan, dict)
            else None
        )
        if isinstance(legacy, list) and len(legacy) >= 3:
            failures.append(
                "evidence_plan suggests multiple disconnected repos "
                f"({len(legacy)} entries). Use one github_repository with folders/modules."
            )
        failures.append("evidence_plan.github_repository is missing (one primary repo required).")
    else:
        repo_name = str(github.get("repo_name") or "").strip()
        tree = str(github.get("final_folder_structure") or "")
        files = github.get("evidence_files") or []
        if not repo_name:
            failures.append("evidence_plan.github_repository.repo_name is missing.")
        if not tree or len(tree.strip()) < 40:
            failures.append(
                "evidence_plan.github_repository.final_folder_structure is missing/too short."
            )
        # reject multi-repo smell inside tree / files
        combined = _lower(tree + " " + " ".join(str(x) for x in files) + " " + repo_name)
        repo_mentions = len(re.findall(r"\brepo\b", combined))
        if repo_mentions >= 3 and (
            "repos" in combined or combined.count("github.com") >= 2
        ):
            failures.append(
                "evidence_plan appears to describe multiple repos; keep one primary repository."
            )
        if isinstance(files, list):
            titled_repos = [
                f for f in files if isinstance(f, str) and re.search(r"\brepo\b", f, re.I)
            ]
            if len(titled_repos) >= 3:
                failures.append(
                    "evidence_plan.evidence_files contains multiple 'Repo' entries implying "
                    "disconnected projects."
                )

    # 14. Capstone delta required on final investigation
    final = investigations[-1]
    capstone_delta = str(final.get("capstone_delta") or "").strip()
    if not capstone_delta or capstone_delta.lower().startswith("n/a"):
        failures.append(
            "Final investigation missing real capstone_delta "
            "(must add verification/measurement/incident/postmortem proof)."
        )
    elif not _contains_any(capstone_delta, CAPSTONE_DELTA_TERMS):
        failures.append(
            "Final investigation capstone_delta does not clearly add operational proof "
            "(expected verification, failure injection, MTTD/MTTR, false positive, "
            "escalation, postmortem, incident, measurement, or benchmark language)."
        )

    for i, inv in enumerate(investigations[1:], start=2):
        delta = str(inv.get("delta_from_previous_investigation") or "").strip()
        if not delta or delta.lower().startswith("none"):
            failures.append(
                f"Investigation {i} ({inv.get('title', '')}) missing "
                "delta_from_previous_investigation."
            )

    # 15. Reject absolute automation language unless paired with boundaries
    text_blobs: list[tuple[str, str]] = []
    role = data.get("role_interpretation")
    if isinstance(role, dict):
        text_blobs.append(
            ("role_interpretation.what_success_looks_like", str(role.get("what_success_looks_like") or ""))
        )
        text_blobs.append(("role_interpretation.real_mission", str(role.get("real_mission") or "")))
        for claim in role.get("role_signature_claims") or []:
            text_blobs.append(("role_signature_claims", str(claim)))
    if isinstance(cumulative, dict):
        text_blobs.append(
            ("cumulative_system.final_capstone_shape", str(cumulative.get("final_capstone_shape") or ""))
        )
        text_blobs.append(
            ("cumulative_system.system_purpose", str(cumulative.get("system_purpose") or ""))
        )
    for inv in investigations:
        text_blobs.append(
            (
                f"investigation:{inv.get('title', '')}",
                _join_fields(
                    inv,
                    (
                        "expensive_problem",
                        "build_or_modify",
                        "improve",
                        "capstone_delta",
                        "artifact_this_investigation_produces",
                    ),
                ),
            )
        )

    for label, text in text_blobs:
        low = _lower(text)
        hits = [p for p in ABSOLUTE_AUTOMATION_PHRASES if p in low]
        if not hits:
            continue
        has_boundary = any(b in low for b in AUTOMATION_BOUNDARY_PAIRS)
        if not has_boundary:
            failures.append(
                f"Absolute automation language without escalation/boundary framing "
                f"in {label}: {', '.join(hits)}."
            )

    # 16. Operational metrics required for production/ops roadmaps
    metrics = data.get("operational_metrics_contract")
    if not isinstance(metrics, list) or len(metrics) < 5:
        failures.append(
            "operational_metrics_contract is missing or too thin "
            "(need >=5 measurable ops metrics)."
        )
    else:
        metrics_blob = _lower(
            " ".join(
                str(m.get("metric", "")) + " " + str(m.get("how_to_measure_in_the_project", ""))
                for m in metrics
                if isinstance(m, dict)
            )
        )
        if not _contains_any(metrics_blob, OPS_METRIC_TERMS):
            failures.append(
                "operational_metrics_contract lacks production ops metrics "
                "(expected MTTD, MTTR / return-to-service, FP/FN, queue depth, "
                "escalation rate, telemetry freshness, or alert noise)."
            )
        has_mttd = "mttd" in metrics_blob or "mean time to detect" in metrics_blob
        has_mttr = (
            "mttr" in metrics_blob
            or "mean time to repair" in metrics_blob
            or "return to service" in metrics_blob
            or "return-to-service" in metrics_blob
            or "time to return" in metrics_blob
        )
        if not (has_mttd and has_mttr):
            failures.append(
                "operational_metrics_contract must include both MTTD and MTTR "
                "(or return-to-service timing)."
            )

    # 17. Automation boundaries required
    boundaries = data.get("automation_boundaries")
    if not isinstance(boundaries, dict):
        failures.append("automation_boundaries is missing.")
    else:
        for key, min_n in (
            ("safe_to_automate", 3),
            ("requires_human_escalation", 3),
            ("fail_closed_conditions", 2),
            ("manual_approval_gates", 2),
        ):
            vals = boundaries.get(key) or []
            if not isinstance(vals, list) or len(vals) < min_n:
                failures.append(
                    f"automation_boundaries.{key} needs >= {min_n} concrete items."
                )

    # 18. Capstone proof contract must include MTTD/MTTR-like measurements
    proof = data.get("capstone_proof_contract")
    if not isinstance(proof, dict):
        failures.append("capstone_proof_contract is missing.")
    else:
        measurements = " ".join(str(x) for x in (proof.get("required_measurements") or []))
        injections = proof.get("required_failure_injections") or []
        docs = " ".join(str(x) for x in (proof.get("required_docs") or []))
        demo = " ".join(str(x) for x in (proof.get("what_it_must_demonstrate") or []))
        readout = str(proof.get("hiring_manager_readout") or "")
        meas_l = _lower(measurements + " " + demo + " " + capstone_delta)
        if "mttd" not in meas_l and "mean time to detect" not in meas_l:
            failures.append(
                "capstone_proof_contract / capstone must include MTTD "
                "(or mean time to detect) measurement."
            )
        if (
            "mttr" not in meas_l
            and "mean time to repair" not in meas_l
            and "return to service" not in meas_l
            and "return-to-service" not in meas_l
            and "time to return" not in meas_l
        ):
            failures.append(
                "capstone_proof_contract / capstone must include MTTR "
                "(or return-to-service) measurement."
            )
        if not isinstance(injections, list) or len(injections) < 3:
            failures.append(
                "capstone_proof_contract.required_failure_injections needs >=3 cases."
            )
        docs_l = _lower(docs)
        if "postmortem" not in docs_l and "incident" not in docs_l:
            failures.append(
                "capstone_proof_contract.required_docs must include incident/postmortem evidence."
            )
        if "verification" not in docs_l:
            failures.append(
                "capstone_proof_contract.required_docs must include a verification log."
            )
        if len(readout.strip()) < 80:
            failures.append(
                "capstone_proof_contract.hiring_manager_readout is missing or too short."
            )

    # 19. Docker investigation must add a Docker artifact to the same system
    docker_invs = [
        inv
        for inv in investigations
        if "docker" in _lower(str(inv.get("title") or ""))
    ]
    if docker_invs:
        growth_blob = ""
        if isinstance(cumulative, dict):
            growth_blob = _lower(
                " ".join(
                    str(g.get("folder_or_module_added", ""))
                    + " "
                    + str(g.get("capability_added", ""))
                    + " "
                    + str(g.get("evidence_created", ""))
                    for g in (cumulative.get("repo_growth_model") or [])
                    if isinstance(g, dict)
                )
            )
        ladder_blob = _lower(
            " ".join(
                str(level.get("module_or_folder_added", ""))
                + " "
                + str(level.get("title", ""))
                + " "
                + str(level.get("new_capability_added", ""))
                for level in ladder
                if isinstance(level, dict)
            )
        )
        inv_blob = _lower(
            " ".join(
                str(inv.get("module_or_folder_added", ""))
                + " "
                + str(inv.get("artifact_this_investigation_produces", ""))
                for inv in docker_invs
            )
        )
        combined = growth_blob + " " + ladder_blob + " " + inv_blob
        if not _contains_any(combined, DOCKER_ARTIFACT_TERMS):
            failures.append(
                "Docker investigation exists but no Docker artifact/module appears in "
                "cumulative_system / proof ladder (expected Dockerfile, docker-compose, "
                "or docker portability/containerization docs in the same repo)."
            )

    # 20. Role signature claims should be present and non-generic
    if isinstance(role, dict):
        claims = role.get("role_signature_claims") or []
        if not isinstance(claims, list) or len(claims) < 4:
            failures.append(
                "role_interpretation.role_signature_claims needs >=4 sharp claims."
            )
        else:
            generic_hits = 0
            for claim in claims:
                c = _lower(str(claim))
                if any(
                    g in c
                    for g in (
                        "responsible for",
                        "work with stakeholders",
                        "cross-functional",
                        "strong communication",
                        "team player",
                    )
                ):
                    generic_hits += 1
            if generic_hits >= 2:
                failures.append(
                    "role_signature_claims look like generic job-summary language; "
                    "need sharp engineering truths."
                )

    # 21. Roadmap consistency: growth / ladder / investigations agree
    growth_list: list[dict[str, Any]] = []
    if isinstance(cumulative, dict):
        raw_growth = cumulative.get("repo_growth_model") or []
        if isinstance(raw_growth, list):
            growth_list = [g for g in raw_growth if isinstance(g, dict)]

    inv_modules = [
        _norm_path(str(inv.get("module_or_folder_added") or ""))
        for inv in investigations
        if isinstance(inv, dict)
    ]
    inv_titles = [
        str(inv.get("title") or "") for inv in investigations if isinstance(inv, dict)
    ]

    sorted_growth: list[dict[str, Any]] = sorted(
        growth_list,
        key=lambda g: int(g.get("investigation_number") or 0),
    )
    if growth_list and len(growth_list) != n:
        failures.append(
            f"repo_growth_model count ({len(growth_list)}) must match "
            f"investigation_roadmap count ({n})."
        )
    elif growth_list:
        for i, inv in enumerate(investigations):
            if not isinstance(inv, dict):
                continue
            if i >= len(sorted_growth):
                break
            g = sorted_growth[i]
            g_num = int(g.get("investigation_number") or 0)
            expected_num = i + 1
            if g_num and g_num != expected_num:
                failures.append(
                    f"repo_growth_model investigation_number {g_num} does not align "
                    f"with investigation index {expected_num}."
                )
            g_title = str(g.get("investigation_title") or "").strip()
            inv_title = str(inv.get("title") or "")
            if g_title and inv_title and not _titles_align(g_title, inv_title):
                failures.append(
                    f"Investigation {expected_num} title mismatch: roadmap says "
                    f"'{inv_title}' but repo_growth_model says '{g_title}'."
                )
            g_mod = str(g.get("folder_or_module_added") or "")
            inv_mod = str(inv.get("module_or_folder_added") or "")
            if _is_vague_module(inv_mod):
                failures.append(
                    f"Investigation {expected_num} module_or_folder_added is too vague "
                    f"('{inv_mod}'). Use the same specific path as repo_growth_model "
                    "(e.g. src/machine_report.py, not just src/)."
                )
            elif g_mod and inv_mod and not _modules_align(g_mod, inv_mod):
                failures.append(
                    f"Investigation {expected_num} module mismatch: roadmap module "
                    f"'{inv.get('module_or_folder_added')}' vs repo growth "
                    f"'{g.get('folder_or_module_added')}'."
                )
            elif inv_mod and not g_mod:
                failures.append(
                    f"Investigation {expected_num} has module "
                    f"'{inv.get('module_or_folder_added')}' but repo_growth_model "
                    "entry is missing folder_or_module_added."
                )

    if isinstance(ladder, list) and ladder:
        ladder_items = [lv for lv in ladder if isinstance(lv, dict)]
        if len(ladder_items) != n:
            failures.append(
                f"proof_of_work_ladder count ({len(ladder_items)}) must match "
                f"investigation_roadmap count ({n})."
            )
        else:
            sorted_ladder = sorted(
                ladder_items,
                key=lambda lv: int(lv.get("level") or 0),
            )
            for i, inv in enumerate(investigations):
                if not isinstance(inv, dict) or i >= len(sorted_ladder):
                    continue
                lv = sorted_ladder[i]
                level = int(lv.get("level") or 0)
                if level and level != i + 1:
                    failures.append(
                        f"proof_of_work_ladder level {level} does not align with "
                        f"investigation index {i + 1}."
                    )
                lv_mod = str(lv.get("module_or_folder_added") or "")
                inv_mod = str(inv.get("module_or_folder_added") or "")
                if lv_mod and inv_mod and not _is_vague_module(inv_mod) and not _modules_align(
                    lv_mod, inv_mod
                ):
                    failures.append(
                        f"Investigation {i + 1} module mismatch vs proof ladder: "
                        f"roadmap '{inv.get('module_or_folder_added')}' vs ladder "
                        f"'{lv.get('module_or_folder_added')}'."
                    )
                inv_title = str(inv.get("title") or "").strip()
                lv_title = str(lv.get("title") or "").strip()
                if inv_title and lv_title and not _titles_exact(inv_title, lv_title):
                    failures.append(
                        f"proof_of_work_ladder[{i}] title '{lv_title}' must exactly equal "
                        f"investigation_roadmap[{i}] title '{inv_title}'."
                    )
                connected = [
                    str(c).strip()
                    for c in (lv.get("connected_investigations") or [])
                    if str(c).strip()
                ]
                if inv_title and not any(_titles_exact(inv_title, c) for c in connected):
                    failures.append(
                        f"proof_of_work_ladder[{i}].connected_investigations must include "
                        f"its own investigation title '{inv_title}'."
                    )
                # Growth and ladder must agree even when investigation is vague
                if i < len(sorted_growth):
                    g_mod = str(sorted_growth[i].get("folder_or_module_added") or "")
                    if g_mod and lv_mod and not _modules_align(g_mod, lv_mod):
                        failures.append(
                            f"Investigation {i + 1}: repo_growth_model module "
                            f"'{g_mod}' does not match proof_of_work_ladder module "
                            f"'{lv_mod}'."
                        )

    # Growth folders must appear in roadmap or ladder modules
    roadmap_ladder_modules = set(m for m in inv_modules if m)
    for lv in ladder if isinstance(ladder, list) else []:
        if isinstance(lv, dict):
            m = _norm_path(str(lv.get("module_or_folder_added") or ""))
            if m:
                roadmap_ladder_modules.add(m)
    for g in growth_list:
        g_mod = _norm_path(str(g.get("folder_or_module_added") or ""))
        if g_mod and g_mod not in roadmap_ladder_modules:
            # Allow if any roadmap/ladder module contains the growth path or vice versa
            if not any(
                g_mod in m or m in g_mod for m in roadmap_ladder_modules
            ):
                failures.append(
                    f"repo_growth_model folder '{g.get('folder_or_module_added')}' "
                    "does not appear in investigation_roadmap or proof_of_work_ladder "
                    "modules."
                )

    # final_folder_structure should mention growth modules (loose path fragments)
    if isinstance(github, dict) and growth_list:
        tree_l = _lower(str(github.get("final_folder_structure") or ""))
        if tree_l:
            missing_in_tree: list[str] = []
            for g in growth_list:
                raw = str(g.get("folder_or_module_added") or "").strip()
                if not raw:
                    continue
                # Check leaf name appears in tree
                leaf = raw.replace("\\", "/").rstrip("/").split("/")[-1]
                parent_hint = raw.replace("\\", "/").split("/")[0] if "/" in raw.replace("\\", "/") else ""
                if leaf and leaf.lower() not in tree_l:
                    # Dockerfile at root is a common miss if tree omits it
                    if parent_hint and parent_hint.lower() in tree_l and len(leaf) > 20:
                        continue
                    missing_in_tree.append(raw)
            # Only flag when many growth modules are absent (avoid brittle single misses)
            if len(missing_in_tree) >= max(2, len(growth_list) // 2):
                failures.append(
                    "evidence_plan.final_folder_structure is missing many modules from "
                    f"repo_growth_model (e.g. {', '.join(missing_in_tree[:4])})."
                )

    # 22. Track titles must EXACTLY match investigation titles (short titles only)
    general_invs = [
        inv for inv in investigations
        if isinstance(inv, dict) and str(inv.get("track", "")).lower() == "general"
    ]
    role_invs = [
        inv for inv in investigations
        if isinstance(inv, dict) and str(inv.get("track", "")).lower() == "role_specific"
    ]
    general_titles = [str(inv.get("title") or "").strip() for inv in general_invs]
    role_titles = [str(inv.get("title") or "").strip() for inv in role_invs]
    general_track_titles = _track_titles_exact_set(general_track)
    role_track_titles = _track_titles_exact_set(role_track)

    for entry in general_track_titles + role_track_titles:
        if _is_paragraph_track_item(entry):
            failures.append(
                f"roadmap_tracks item is paragraph-length / not a short title: '{entry[:80]}…'"
                if len(entry) > 80
                else f"roadmap_tracks item is paragraph-length / not a short title: '{entry}'"
            )

    def _title_in(titles: list[str], candidate: str) -> bool:
        return any(_titles_exact(candidate, t) for t in titles)

    for entry in general_track_titles:
        if not _title_in(general_titles, entry):
            failures.append(
                f"roadmap_tracks.general_engineering_track title '{entry}' does not "
                "exactly match any investigation with track=general."
            )
    for entry in role_track_titles:
        if not _title_in(role_titles, entry):
            failures.append(
                f"roadmap_tracks.role_specific_track title '{entry}' does not "
                "exactly match any investigation with track=role_specific."
            )
    for title in general_titles:
        if not _title_in(general_track_titles, title):
            failures.append(
                f"Investigation '{title}' (general) missing from "
                "roadmap_tracks.general_engineering_track."
            )
        if _title_in(role_track_titles, title):
            failures.append(
                f"Investigation '{title}' appears in both general and role_specific tracks."
            )
    for title in role_titles:
        if not _title_in(role_track_titles, title):
            failures.append(
                f"Investigation '{title}' (role_specific) missing from "
                "roadmap_tracks.role_specific_track."
            )
        if _title_in(general_track_titles, title):
            failures.append(
                f"Investigation '{title}' appears in both general and role_specific tracks."
            )
    if len(general_track_titles) != len(general_titles):
        failures.append(
            "roadmap_tracks.general_engineering_track count must equal number of "
            f"general investigations ({len(general_titles)} vs {len(general_track_titles)})."
        )
    if len(role_track_titles) != len(role_titles):
        failures.append(
            "roadmap_tracks.role_specific_track count must equal number of "
            f"role_specific investigations ({len(role_titles)} vs {len(role_track_titles)})."
        )

    # Docker cannot be role-specific unless JD treats containers as primary duty
    docker_role_specific = False
    for inv in role_invs:
        blob = _lower(
            _join_fields(
                inv,
                ("title", "engineering_question", "expensive_problem", "build_or_modify"),
            )
        )
        if "docker" in blob:
            docker_role_specific = True
    for entry in role_track:
        if "docker" in _lower(str(entry)):
            docker_role_specific = True
    if docker_role_specific:
        if not jd_text or not _jd_has_container_primary_duty(jd_text):
            failures.append(
                "Docker appears on the role_specific track, but the JD does not treat "
                "container infrastructure as a primary role-specific duty. Move Docker "
                "to general_engineering_track."
            )

    # 23. Metric / performance source honesty
    def _check_sourced_item(label: str, text: str, source_raw: str) -> None:
        canonical = _normalize_metric_source(source_raw)
        if source_raw and canonical is None:
            failures.append(
                f"{label} has unrecognized source '{source_raw}' "
                f"(use stated_in_jd | implied_by_jd | proposed_project_target)."
            )
            return
        if not canonical:
            failures.append(
                f"{label} is missing source "
                "(stated_in_jd | implied_by_jd | proposed_project_target)."
            )
            return
        # Reject prose "stated in JD" style when we can detect it was meant as stated
        thresholds = _extract_numeric_thresholds(text)
        if canonical == "stated_in_jd" and thresholds and jd_text:
            for tok in thresholds:
                if not _number_token_in_jd(tok, jd_text):
                    failures.append(
                        f"{label} marks numeric threshold '{tok}' as stated_in_jd, "
                        "but that number does not appear in the job description. "
                        "Use proposed_project_target."
                    )
                    break
        elif canonical == "stated_in_jd" and thresholds and not jd_text:
            # Without JD text, still reject invented ops SLOs commonly fabricated
            invented = any(
                x in _lower(text)
                for x in (
                    "under 5 minute",
                    "under 5 min",
                    "under 30 minute",
                    "under 30 min",
                    "<5 min",
                    "<30 min",
                    "5 minutes",
                    "30 minutes",
                )
            )
            if invented and ("mttd" in _lower(text) or "mttr" in _lower(text)):
                failures.append(
                    f"{label} looks like a fabricated MTTD/MTTR threshold marked "
                    "stated_in_jd; use proposed_project_target unless the JD states "
                    "the exact number."
                )

    for i, item in enumerate(metrics if isinstance(metrics, list) else [], start=1):
        if not isinstance(item, dict):
            continue
        metric_text = " ".join(
            [
                str(item.get("metric") or ""),
                str(item.get("how_to_measure_in_the_project") or ""),
                str(item.get("why_it_matters") or ""),
            ]
        )
        source_raw = str(item.get("source") or "")
        _check_sourced_item(f"operational_metrics_contract[{i}] ({item.get('metric', '?')})", metric_text, source_raw)

    for i, item in enumerate(data.get("performance_requirements") or [], start=1):
        if not isinstance(item, dict):
            continue
        req_text = str(item.get("requirement") or "")
        source_raw = str(item.get("source") or "")
        _check_sourced_item(f"performance_requirements[{i}]", req_text, source_raw)

    # 24. Hardware tooling / repair leakage vs JD support
    role_output_blob = _lower(
        " ".join(
            [_join_fields(inv, ("title", "engineering_question", "expensive_problem",
                                "phase_0_mental_model", "subquestions",
                                "concepts_and_vocabulary", "build_or_modify"))
             for inv in role_invs]
            + [str(e) for e in role_track]
            + [
                str((data.get("cumulative_system") or {}).get("system_name") or ""),
                str((data.get("cumulative_system") or {}).get("final_capstone_shape") or ""),
                str(final.get("title") or ""),
                str(final.get("capstone_delta") or ""),
            ]
        )
    )
    if jd_text:
        jd_tooling = _contains_any(jd_text, HARDWARE_TOOLING_TERMS)
        if jd_tooling:
            if not any(t in role_output_blob for t in jd_tooling):
                failures.append(
                    "JD mentions "
                    + ", ".join(sorted(set(jd_tooling)))
                    + " but the role-specific roadmap never names those concepts "
                    "explicitly (do not collapse into only generic 'hardware telemetry')."
                )
        else:
            leaked = [t for t in HARDWARE_TOOLING_TERMS if t in role_output_blob]
            # also scan all investigations/tracks for BMC/Redfish invention
            all_blob = role_output_blob + " " + _lower(
                " ".join(str(e) for e in general_track)
            )
            leaked = [t for t in HARDWARE_TOOLING_TERMS if t in all_blob]
            if leaked and not _jd_supports_hardware_tooling(jd_text):
                failures.append(
                    "Roadmap invents BMC/Redfish/IPMI concepts but the JD does not "
                    "mention hardware fleet tooling / firmware telemetry / bare metal "
                    f"lifecycle ({', '.join(sorted(set(leaked)))})."
                )

        repair_hits = _contains_any(role_output_blob, (
            "gpu repair pipeline",
            "repair pipeline simulation",
            "fleet repair",
        ))
        if repair_hits and not _jd_supports_repair_pipeline(jd_text):
            failures.append(
                "Roadmap includes GPU/fleet repair pipeline simulation but the JD does "
                "not support repair/RMA/return-to-service/fleet-health operations "
                f"({', '.join(sorted(set(repair_hits)))})."
            )

    # 25. Capstone must not use fake past-tense achievement language
    if isinstance(proof, dict):
        readout = str(proof.get("hiring_manager_readout") or "")
        demo = " ".join(str(x) for x in (proof.get("what_it_must_demonstrate") or []))
        measurements = " ".join(str(x) for x in (proof.get("required_measurements") or []))
        capstone_blob = " ".join([readout, demo, measurements])
        fake_hits = _fake_achievement_hits(capstone_blob)
        if fake_hits and not _has_future_framing(capstone_blob):
            failures.append(
                "capstone_proof_contract uses fake past-tense achievement language "
                f"({', '.join(sorted(set(fake_hits)))}) without future-target framing. "
                "Use 'After completing…', 'Target measurement…', or "
                "'Evidence to produce…'."
            )
        readout_fakes = _fake_achievement_hits(readout)
        if readout_fakes and not _has_future_framing(readout):
            failures.append(
                "capstone_proof_contract.hiring_manager_readout claims completed "
                f"results ({', '.join(sorted(set(readout_fakes)))}). Project Lambda "
                "generates a roadmap, not fake achievements."
            )

    # 26. Role family classification + family-correct routing
    role_family = data.get("role_family")
    primary_family = ""
    if not isinstance(role_family, dict):
        failures.append("role_family is missing.")
    else:
        primary_family = str(role_family.get("primary_family") or "").strip()
        if primary_family not in ALLOWED_ROLE_FAMILIES:
            failures.append(
                f"role_family.primary_family '{primary_family}' is not an allowed family."
            )
        why = str(role_family.get("why_this_family") or "").strip()
        if len(why) < 40:
            failures.append("role_family.why_this_family is missing or too thin.")
        excluded = role_family.get("excluded_families")
        if not isinstance(excluded, list):
            failures.append("role_family.excluded_families must be a list.")

        inferred = _infer_family_from_jd(jd_text) if jd_text else None
        if (
            inferred == "ai_infrastructure_model_serving"
            and primary_family == "gpu_fleet_production_engineering"
            and not _jd_supports_repair_pipeline(jd_text)
        ):
            failures.append(
                "role_family.primary_family is gpu_fleet_production_engineering but the "
                "JD reads as AI infrastructure / model serving without fleet-repair support."
            )
        if (
            inferred == "gpu_fleet_production_engineering"
            and primary_family == "ai_infrastructure_model_serving"
            and _jd_supports_hardware_tooling(jd_text)
        ):
            # Soft: Fluidstack-like JDs should not be classified as model serving
            failures.append(
                "role_family.primary_family is ai_infrastructure_model_serving but the "
                "JD strongly indicates GPU fleet production engineering "
                "(repair/BMC/Redfish/hardware lifecycle)."
            )

        system_blob = _lower(
            str((cumulative or {}).get("system_name") or "")
            + " "
            + str((cumulative or {}).get("suggested_repo_name") or "")
            + " "
            + str((cumulative or {}).get("final_capstone_shape") or "")
        )
        if primary_family == "ai_infrastructure_model_serving":
            if not any(t in system_blob for t in MODEL_SERVING_SYSTEM_TERMS):
                failures.append(
                    "ai_infrastructure_model_serving cumulative system should be named "
                    "like ai-inference-reliability-lab / model-serving-ops-lab / "
                    "inference-platform-lab (inference/serving/model reliability)."
                )
            if any(t in system_blob for t in ("fleet-repair", "repair-lab", "gpu-fleet-ops")):
                failures.append(
                    "ai_infrastructure_model_serving must not use a fleet-repair "
                    "cumulative system name."
                )
            role_titles_blob = _lower(" ".join(role_titles + [str(final.get("title") or "")]))
            if not _contains_any(role_titles_blob, MODEL_SERVING_ROLE_TERMS):
                failures.append(
                    "ai_infrastructure_model_serving role-specific investigations must "
                    "include model serving / inference / latency / throughput style work."
                )
            capstone_blob = _lower(
                str(final.get("title") or "")
                + " "
                + str(final.get("capstone_delta") or "")
                + " "
                + str((cumulative or {}).get("final_capstone_shape") or "")
                + " "
                + (
                    " ".join(str(x) for x in (proof.get("what_it_must_demonstrate") or []))
                    if isinstance(proof, dict)
                    else ""
                )
            )
            if not _contains_any(
                capstone_blob,
                ("inference", "serving", "latency", "throughput", "load test", "p95", "p99"),
            ):
                failures.append(
                    "ai_infrastructure_model_serving capstone must prove inference/"
                    "model-serving reliability (latency/throughput/load/error metrics), "
                    "not fleet repair."
                )
            if _contains_any(
                capstone_blob,
                ("gpu repair pipeline", "fleet repair", "return-to-service repair"),
            ) and not _jd_supports_repair_pipeline(jd_text or ""):
                failures.append(
                    "ai_infrastructure_model_serving capstone must not be a GPU fleet "
                    "repair simulation when the JD does not support fleet repair."
                )
            # Reject fleet-repair leakage in role-specific track for this family
            leaked_fleet = _contains_any(role_output_blob, FLEET_REPAIR_OUTPUT_TERMS)
            if leaked_fleet and jd_text and not _jd_supports_repair_pipeline(jd_text):
                failures.append(
                    "ai_infrastructure_model_serving roadmap leaks fleet-repair topics "
                    f"without JD support: {', '.join(sorted(set(leaked_fleet)))}."
                )

        if primary_family == "gpu_fleet_production_engineering":
            if not any(t in system_blob for t in FLEET_SYSTEM_TERMS + ("health", "compute", "gpu")):
                failures.append(
                    "gpu_fleet_production_engineering cumulative system should be "
                    "role-shaped (fleet/repair/compute/gpu health)."
                )

    # 27. Proposed metrics must be project-measurable
    for i, item in enumerate(metrics if isinstance(metrics, list) else [], start=1):
        if not isinstance(item, dict):
            continue
        source_c = _normalize_metric_source(str(item.get("source") or ""))
        metric_text = " ".join(
            [
                str(item.get("metric") or ""),
                str(item.get("how_to_measure_in_the_project") or ""),
            ]
        )
        low_m = _lower(metric_text)
        if source_c == "proposed_project_target":
            bad = [p for p in UNMEASURABLE_PROPOSED_METRIC_PHRASES if p in low_m]
            if bad:
                failures.append(
                    f"operational_metrics_contract[{i}] proposed metric looks like a "
                    f"business/org KPI not measurable in the project ({', '.join(bad)})."
                )
            elif not _contains_any(low_m, PROJECT_MEASURABLE_METRIC_TERMS):
                failures.append(
                    f"operational_metrics_contract[{i}] ('{item.get('metric', '')}') "
                    "is not clearly measurable by the cumulative project "
                    "(prefer latency/throughput/error rate/queue/MTTD/MTTR/etc.)."
                )

    # 28. missing_mental_models must point at investigations that build them
    inv_title_list = [str(inv.get("title") or "").strip() for inv in investigations]
    for i, mm in enumerate(data.get("missing_mental_models") or [], start=1):
        if not isinstance(mm, dict):
            continue
        pointer = str(mm.get("first_investigation_that_builds_it") or "").strip()
        model = str(mm.get("mental_model") or "").strip()
        if not pointer:
            failures.append(
                f"missing_mental_models[{i}] missing first_investigation_that_builds_it."
            )
            continue
        if inv_title_list and not any(
            _titles_exact(pointer, t) or _titles_align(pointer, t) for t in inv_title_list
        ):
            failures.append(
                f"missing_mental_models[{i}] first_investigation_that_builds_it "
                f"'{pointer}' does not match any investigation title."
            )
            continue
        model_l = _lower(model)
        pointer_l = _lower(pointer)
        if any(t in model_l for t in OBSERVABILITY_MENTAL_MODEL_TERMS):
            if any(m in pointer_l for m in API_INVESTIGATION_MARKERS) and not any(
                t in pointer_l
                for t in ("health", "metric", "alert", "observ", "latency", "monitor")
            ):
                failures.append(
                    f"missing_mental_models[{i}] observability/metrics model incorrectly "
                    f"points at API investigation '{pointer}'. Point at health checks, "
                    "metrics/alerts, or inference observability instead."
                )

    if failures:
        bullet = "\n".join(f"- {f}" for f in failures)
        raise ValidationError(f"Project Lambda validation failed:\n{bullet}")
