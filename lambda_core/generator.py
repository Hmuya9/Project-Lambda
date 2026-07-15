"""Single-shot LLM generation of a Role-to-Roadmap."""

from __future__ import annotations

import json
import os
import sys
from typing import Any

from openai import OpenAI

from lambda_core.prompts import CONTRACT_JSON_SCHEMA, SYSTEM_PROMPT, build_user_prompt

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


def generate_contract(job_description: str, engineer_profile: str) -> dict[str, Any]:
    api_key, model, base_url = resolve_config()
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is missing or blank (set it in .env).")
    client = _client(api_key, base_url)
    user_prompt = build_user_prompt(job_description, engineer_profile)

    # Prefer structured outputs when the backend supports them; fall back to JSON mode.
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
    data = json.loads(content)
    _require_keys(data)
    return data


REQUIRED_TOP_LEVEL = [
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
]


def _require_keys(data: dict[str, Any]) -> None:
    missing = [k for k in REQUIRED_TOP_LEVEL if k not in data]
    if missing:
        raise ValueError(f"Model JSON missing required keys: {', '.join(missing)}")
