"""Thin client for calling open-weight models via Ollama.

Ollama runs models locally and exposes a simple API — used here instead of
a closed-model provider so every agent's outputs are free to rerun and the
model heterogeneity in config/models.py is genuine architectural diversity
across model families, not prompt variation on one vendor's model.
"""

import json

import ollama

from config.models import ModelConfig


class ModelCallError(RuntimeError):
    pass


def call_model(model_config: ModelConfig, system_prompt: str, user_prompt: str) -> str:
    try:
        response = ollama.chat(
            model=model_config.model_id,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            options={"temperature": model_config.temperature},
        )
    except Exception as exc:
        raise ModelCallError(
            f"Failed to call '{model_config.model_id}' via Ollama. Is Ollama running "
            f"(`ollama serve`) and has the model been pulled "
            f"(`ollama pull {model_config.model_id}`)? Original error: {exc}"
        ) from exc
    return response["message"]["content"]


def parse_structured_response(raw_text: str) -> dict:
    """Extract a JSON object from a model response, tolerating surrounding text.

    Open-weight models are less reliable than frontier closed models about
    respecting "respond with only JSON" instructions, so this scans for the
    outermost braces rather than assuming raw_text is pure JSON.
    """
    start = raw_text.find("{")
    end = raw_text.rfind("}")
    if start == -1 or end == -1 or end < start:
        raise ModelCallError(f"No JSON object found in model response: {raw_text!r}")
    try:
        return json.loads(raw_text[start : end + 1])
    except json.JSONDecodeError as exc:
        raise ModelCallError(f"Could not parse JSON from model response: {raw_text!r}") from exc
