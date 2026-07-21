"""Thin Anthropic client wrapper. One job: prompt in, validated JSON out."""

from __future__ import annotations

import json
import os
import re
from typing import Any

DEFAULT_MODEL = "claude-sonnet-4-5"


def resolve_config() -> tuple[str, str]:
    """Read env config. Returns (api_key, model)."""
    api_key = os.getenv("ANTHROPIC_API_KEY", "").strip()
    model = os.getenv("ANTHROPIC_MODEL", "").strip() or DEFAULT_MODEL
    return api_key, model


def validate_config() -> tuple[str, str]:
    api_key, model = resolve_config()
    if not api_key:
        raise RuntimeError("ANTHROPIC_API_KEY is missing or blank (set it in .env).")
    return api_key, model


def _extract_json(text: str) -> Any:
    """Parse JSON from a model reply, tolerating markdown fences."""
    text = text.strip()
    fence = re.search(r"```(?:json)?\s*(.*?)```", text, re.DOTALL)
    if fence:
        text = fence.group(1).strip()
    # Fall back to the outermost braces if there is prose around the object.
    if not text.startswith("{") and "{" in text:
        text = text[text.index("{"): text.rindex("}") + 1]
    return json.loads(text)


def complete_json(
    system: str,
    user: str,
    *,
    max_tokens: int = 8192,
    retries: int = 2,
) -> Any:
    """One model call returning parsed JSON, with parse-failure retries."""
    import anthropic  # deferred so offline paths (render, tests) never need it

    api_key, model = validate_config()
    client = anthropic.Anthropic(api_key=api_key)

    prompt = user
    last_err: Exception | None = None
    for _ in range(retries + 1):
        message = client.messages.create(
            model=model,
            max_tokens=max_tokens,
            system=system,
            messages=[{"role": "user", "content": prompt}],
        )
        text = "".join(b.text for b in message.content if b.type == "text")
        try:
            return _extract_json(text)
        except (json.JSONDecodeError, ValueError) as err:
            last_err = err
            prompt = (
                user
                + "\n\nYour previous reply was not valid JSON ("
                + str(err)
                + "). Reply with ONLY one valid JSON object, no prose, no fences."
            )
    raise RuntimeError(f"Model did not return valid JSON after retries: {last_err}")
