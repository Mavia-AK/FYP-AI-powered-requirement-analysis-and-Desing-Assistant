# app/ml/uml/openrouter_client.py
"""
Shared OpenRouter API client for UML modules.

Provides a single `call_openrouter(prompt)` function that tries multiple
free models in order, falling back gracefully.
"""
from __future__ import annotations

import json
import os
import urllib.request
import urllib.error
from pathlib import Path

from dotenv import load_dotenv


# Free models to try in order of preference
_FREE_MODELS = [
    "google/gemini-2.0-flash-exp:free",
    "google/gemini-2.0-pro-exp-02-05:free",
    "google/gemma-3-27b-it:free",
    "inclusionai/ling-2.6-flash:free",
    "meta-llama/llama-3.3-70b-instruct:free",
    "openai/gpt-oss-20b:free",
    "nvidia/nemotron-3-super-120b-a12b:free",
]

_OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"


def _load_env_file() -> None:
    """Load environment variables from .env files if present."""
    env_paths = [
        Path(__file__).resolve().parent / ".env",
        Path(__file__).resolve().parents[3] / ".env",
    ]
    for env_path in env_paths:
        if env_path.exists():
            load_dotenv(dotenv_path=env_path, override=False)
            break


def call_openrouter(prompt: str, *, timeout: int = 60) -> str:
    """
    Call OpenRouter API with fallback across multiple free models.

    Parameters
    ----------
    prompt : str
        The prompt to send.
    timeout : int
        HTTP request timeout in seconds.

    Returns
    -------
    str
        The model's response text.

    Raises
    ------
    RuntimeError
        If all free models fail.
    """
    _load_env_file()
    api_key = os.getenv('OPENROUTER_API_KEY')
    if not api_key:
        raise ValueError(
            "OPENROUTER_API_KEY environment variable is not set. "
            "Get a free key at https://openrouter.ai/settings/keys"
        )

    last_error = None
    for model_id in _FREE_MODELS:
        try:
            payload = json.dumps({
                "model": model_id,
                "messages": [{"role": "user", "content": prompt}],
            }).encode("utf-8")

            req = urllib.request.Request(
                _OPENROUTER_URL, data=payload, method="POST",
            )
            req.add_header("Authorization", f"Bearer {api_key}")
            req.add_header("Content-Type", "application/json")

            with urllib.request.urlopen(req, timeout=timeout) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                return data["choices"][0]["message"]["content"]

        except urllib.error.HTTPError as e:
            last_error = f"{model_id}: HTTP {e.code}"
            continue
        except Exception as e:
            last_error = f"{model_id}: {e}"
            continue

    raise RuntimeError(f"All free models failed. Last error: {last_error}")
