"""Single-shot LLM generation of a Role-to-Roadmap."""

from __future__ import annotations

import json
import os
import sys
from typing import Any

from openai import OpenAI

from lambda_core.align import align_roadmap_structure
from lambda_core.prompts import CONTRACT_JSON_SCHEMA, SYSTEM_PROMPT, build_user_prompt
from lambda_core.validate import ValidationError, validate_roadmap

DEFAULT_MODEL = "gpt-4o-mini"


def resolve_config() -> tuple[str, str, str | None]:
    """Read env config. Blank OPENAI_BASE_URL is treated as unset.

    Returns (api_key, model, base_url_or_none).
    """
    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    model_env = os.getenv("OPENAI_MODEL", "").strip()
    model = model_env or DEFAULT_MODEL
    base_url = os.getenv("OPENAI_BASE_URL", "").strip() or None

    # The OpenAI SDK also reads OPENAI_BASE_URL from the process environment.
    # A blank value there can break connections — remove it when unused.
    if not base_url:
        os.environ.pop("OPENAI_BASE_URL", None)

    return api_key, model, base_url


def validate_config() -> tuple[str, str, str | None]:
    """Validate env config and print a short startup summary.

    Returns (api_key, model, base_url_or_none).
    Raises RuntimeError if required values are missing.
    """
    api_key, model, base_url = resolve_config()
    model_from_env = bool(os.getenv("OPENAI_MODEL", "").strip())

    print("Config:", file=sys.stderr)
    print(
        f"  OPENAI_API_KEY: {'set' if api_key else 'MISSING'}",
        file=sys.stderr,
    )
    print(
        f"  OPENAI_MODEL: {model}"
        + ("" if model_from_env else " (default)"),
        file=sys.stderr,
    )
    if base_url:
        print(f"  OPENAI_BASE_URL: {base_url}", file=sys.stderr)
    else:
        print(
            "  OPENAI_BASE_URL: (not used - default OpenAI API)",
            file=sys.stderr,
        )

    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is missing or blank (set it in .env).")
    if not model:
        raise RuntimeError("OPENAI_MODEL is missing or blank.")

    return api_key, model, base_url


def _client(api_key: str, base_url: str | None = None) -> OpenAI:
    # Only pass base_url when it is a non-empty string.
    if base_url:
        return OpenAI(api_key=api_key, base_url=base_url)
    return OpenAI(api_key=api_key)


def _call_model(client: OpenAI, model: str, user_prompt: str) -> dict[str, Any]:
    """Call the model once and return parsed JSON (keys checked)."""
    try:
        response = client.chat.completions.create(
            model=model,
            temperature=0.3,
            response_format={
                "type": "json_schema",
                "json_schema": {
                    "name": "role_to_roadmap",
                    "strict": True,
                    "schema": CONTRACT_JSON_SCHEMA,
                },
            },
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
        )
    except Exception:
        response = client.chat.completions.create(
            model=model,
            temperature=0.3,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {
                    "role": "user",
                    "content": user_prompt
                    + "\n\nReturn ONLY a single JSON object matching this schema:\n"
                    + json.dumps(CONTRACT_JSON_SCHEMA),
                },
            ],
        )

    content = response.choices[0].message.content
    if not content:
        raise RuntimeError("Model returned empty content.")
    try:
        data = json.loads(content)
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"Model returned invalid JSON: {exc}") from exc
    _require_keys(data)
    return data


def generate_contract(job_description: str, engineer_profile: str) -> dict[str, Any]:
    api_key, model, base_url = resolve_config()
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is missing or blank (set it in .env).")
    client = _client(api_key, base_url)
    user_prompt = build_user_prompt(job_description, engineer_profile)

    data = _call_model(client, model, user_prompt)
    last_err: Exception | None = None
    for attempt in range(2):
        align_roadmap_structure(data, job_description=job_description)
        try:
            validate_roadmap(data, job_description=job_description)
            return data
        except (ValidationError, RuntimeError) as err:
            last_err = err
            print(
                f"Validation/generation issue (attempt {attempt + 1}); retrying...",
                file=sys.stderr,
            )
            repair_prompt = (
                user_prompt
                + "\n\n=== PREVIOUS OUTPUT FAILED — FIX THESE EXACTLY ===\n"
                + str(err)
                + "\n\nRegenerate the FULL corrected JSON with these non-negotiables:\n"
                "- role_family must match THIS JD (model-serving vs fleet-repair).\n"
                "- Prefer 8–10 investigations total. Capstone MUST be the LAST item.\n"
                "- Every investigation needs specific module_or_folder_added.\n"
                "- roadmap_tracks titles are SHORT exact copies of investigation titles.\n"
                "- No BMC/Redfish/GPU repair unless JD supports them.\n"
                "- Capstone + cumulative system names match role_family.\n"
                "- Proposed metrics: latency/throughput/error rate/queue/MTTD/MTTR.\n"
                "- missing_mental_models pointers must be exact investigation titles.\n"
                "- Investigation 1 = machine-report; paste prompt includes Phase 0, "
                "mental model, observe, build, break, improve, GitHub, Obsidian.\n"
                "- Every phase_0_mental_model uses >=2 causal/layer words; every "
                "visual_system_model includes -> or layer/flow/pipeline/state.\n"
                "- Return complete valid JSON only."
            )
            try:
                data = _call_model(client, model, repair_prompt)
            except RuntimeError as gen_err:
                last_err = gen_err
                # Try one more clean generation without repair context if JSON broke
                data = _call_model(client, model, user_prompt)
    assert last_err is not None
    align_roadmap_structure(data, job_description=job_description)
    validate_roadmap(data, job_description=job_description)
    return data


REQUIRED_TOP_LEVEL = [
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
]


def _require_keys(data: dict[str, Any]) -> None:
    missing = [k for k in REQUIRED_TOP_LEVEL if k not in data]
    if missing:
        raise ValueError(f"Model JSON missing required keys: {', '.join(missing)}")
