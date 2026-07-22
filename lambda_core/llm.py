"""Thin LLM client wrapper. One job: prompt in, validated JSON out.

Provider selection (checked in this order):
  LAMBDA_PROVIDER=anthropic|openai  — explicit override, else:
  ANTHROPIC_API_KEY set             — Anthropic
  OPENAI_API_KEY set                — OpenAI-compatible (honors OPENAI_BASE_URL,
                                      so Ollama/local servers work too)
"""

from __future__ import annotations

import json
import os
import re
from typing import Any

DEFAULT_ANTHROPIC_MODEL = "claude-sonnet-5"
DEFAULT_OPENAI_MODEL = "gpt-5.6-terra"


def resolve_config() -> tuple[str, str, str]:
    """Read env config. Returns (provider, api_key, model)."""
    override = os.getenv("LAMBDA_PROVIDER", "").strip().lower()
    anthropic_key = os.getenv("ANTHROPIC_API_KEY", "").strip()
    openai_key = os.getenv("OPENAI_API_KEY", "").strip()

    if override == "anthropic" or (not override and anthropic_key):
        model = os.getenv("ANTHROPIC_MODEL", "").strip() or DEFAULT_ANTHROPIC_MODEL
        return "anthropic", anthropic_key, model
    if override == "openai" or (not override and openai_key):
        model = os.getenv("OPENAI_MODEL", "").strip() or DEFAULT_OPENAI_MODEL
        return "openai", openai_key, model
    return "none", "", ""


def validate_config() -> tuple[str, str, str]:
    provider, api_key, model = resolve_config()
    if provider == "none" or not api_key:
        raise RuntimeError(
            "No LLM credentials found. Set ANTHROPIC_API_KEY or OPENAI_API_KEY "
            "in .env (LAMBDA_PROVIDER=anthropic|openai to force one)."
        )
    return provider, api_key, model


def _extract_json(text: str) -> Any:
    """Parse JSON from a model reply, tolerating fences and surrounding prose."""
    text = text.strip()
    if not text:
        raise ValueError("model returned empty text")
    fence = re.search(r"```(?:json)?\s*(.*?)```", text, re.DOTALL)
    if fence:
        text = fence.group(1).strip()
    # Decode the FIRST JSON object found, ignoring prose before or after it —
    # raw_decode handles trailing text that plain json.loads would reject.
    start = text.find("{")
    if start == -1:
        raise ValueError("no JSON object in model reply")
    obj, _ = json.JSONDecoder().raw_decode(text[start:])
    if not isinstance(obj, dict):
        raise ValueError("model reply parsed to a non-object")
    return obj


def _call_anthropic(api_key: str, model: str, system: str, prompt: str, max_tokens: int) -> str:
    import anthropic  # deferred so offline paths (render, tests) never need it

    client = anthropic.Anthropic(api_key=api_key)
    try:
        message = client.messages.create(
            model=model,
            max_tokens=max_tokens,
            system=system,
            messages=[{"role": "user", "content": prompt}],
        )
    except anthropic.AuthenticationError as err:
        raise RuntimeError(
            "ANTHROPIC_API_KEY was rejected. Check the key in .env "
            "(console.anthropic.com → API keys). API said: " + str(err)
        ) from err
    except anthropic.NotFoundError as err:
        raise RuntimeError(
            f"Model '{model}' is not available to your account. Set "
            "ANTHROPIC_MODEL in .env to a model you have access to. "
            "API said: " + str(err)
        ) from err
    except anthropic.APIStatusError as err:
        raise RuntimeError(
            f"Anthropic API error (HTTP {err.status_code}) with model "
            f"'{model}': {err.message}"
        ) from err
    return "".join(b.text for b in message.content if b.type == "text")


def _call_openai(api_key: str, model: str, system: str, prompt: str, max_tokens: int) -> str:
    import openai  # deferred

    base_url = os.getenv("OPENAI_BASE_URL", "").strip() or None
    client = openai.OpenAI(api_key=api_key, base_url=base_url) if base_url else openai.OpenAI(api_key=api_key)
    messages = [
        {"role": "system", "content": system},
        {"role": "user", "content": prompt},
    ]
    try:
        try:
            response = client.chat.completions.create(
                model=model,
                max_completion_tokens=max_tokens,
                response_format={"type": "json_object"},
                messages=messages,
            )
        except openai.BadRequestError:
            # Older models / some OpenAI-compatible servers (Ollama etc.) reject
            # max_completion_tokens or response_format — retry with legacy params.
            response = client.chat.completions.create(
                model=model,
                max_tokens=max_tokens,
                messages=messages,
            )
    except openai.AuthenticationError as err:
        raise RuntimeError(
            "OPENAI_API_KEY was rejected. Check the key in .env "
            "(platform.openai.com → API keys). API said: " + str(err)
        ) from err
    except openai.NotFoundError as err:
        raise RuntimeError(
            f"Model '{model}' is not available to your account. Set "
            "OPENAI_MODEL in .env to a model you have access to. "
            "API said: " + str(err)
        ) from err
    except openai.BadRequestError as err:
        raise RuntimeError(
            f"OpenAI API rejected the request for model '{model}': {err}. "
            "Try a different model via OPENAI_MODEL in .env."
        ) from err
    except openai.APIStatusError as err:
        raise RuntimeError(
            f"OpenAI API error (HTTP {err.status_code}) with model '{model}': {err.message}"
        ) from err
    return response.choices[0].message.content or ""


def complete_json(
    system: str,
    user: str,
    *,
    max_tokens: int = 8192,
    retries: int = 2,
) -> Any:
    """One model call returning parsed JSON, with parse-failure retries."""
    provider, api_key, model = validate_config()
    call = _call_anthropic if provider == "anthropic" else _call_openai

    prompt = user
    last_err: Exception | None = None
    for _ in range(retries + 1):
        text = call(api_key, model, system, prompt, max_tokens)
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
