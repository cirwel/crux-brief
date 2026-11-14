"""Local Ollama /api/chat JSON client.

Calls http://localhost:11434/api/chat directly (never /v1, which silently
truncates long prompts from the front) with think=false and format=json.
"""

from __future__ import annotations

import json
import time
import urllib.request
from typing import Any

OLLAMA_CHAT_URL = "http://localhost:11434/api/chat"
OLLAMA_GENERATE_URL = "http://localhost:11434/api/generate"


def model_slug(model: str) -> str:
    """Convert an Ollama model tag into a filesystem-safe directory name."""
    return model.replace(":", "_").replace("/", "_")


def unload_model(model: str) -> None:
    """Best-effort unload of a loaded Ollama model to avoid unified-memory pressure."""
    payload = json.dumps({"model": model, "keep_alive": 0}).encode("utf-8")
    req = urllib.request.Request(
        OLLAMA_GENERATE_URL,
        data=payload,
        headers={"Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            resp.read()
    except Exception:
        pass


def _extract_json_object(text: str) -> dict[str, Any]:
    """Parse a JSON dict, tolerating surrounding markdown/text if present."""
    stripped = text.strip()
    try:
        parsed = json.loads(stripped)
        if isinstance(parsed, dict):
            return parsed
    except ValueError:
        pass

    start = stripped.find("{")
    end = stripped.rfind("}")
    if start != -1 and end > start:
        parsed = json.loads(stripped[start : end + 1])
        if isinstance(parsed, dict):
            return parsed
    raise ValueError("Response did not contain a JSON object")


def _post_chat(
    model: str,
    messages: list[dict[str, str]],
    *,
    seed: int,
    temperature: float,
    num_ctx: int,
    timeout: int,
) -> tuple[str, dict[str, Any]]:
    payload = json.dumps(
        {
            "model": model,
            "stream": False,
            "think": False,
            "format": "json",
            "options": {
                "temperature": temperature,
                "seed": seed,
                "num_ctx": num_ctx,
            },
            "messages": messages,
        }
    ).encode("utf-8")
    req = urllib.request.Request(
        OLLAMA_CHAT_URL,
        data=payload,
        headers={"Content-Type": "application/json"},
    )
    t0 = time.time()
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        data = json.load(resp)
    wall_s = time.time() - t0
    content = data.get("message", {}).get("content", "")
    meta = {
        "prompt_tokens": int(data.get("prompt_eval_count") or 0),
        "output_tokens": int(data.get("eval_count") or 0),
        "seconds": round(
            float(data.get("total_duration") or 0) / 1e9 if data.get("total_duration") else wall_s,
            2,
        ),
    }
    return content, meta


def chat_json(
    model: str,
    system: str,
    user: str,
    *,
    seed: int = 0,
    temperature: float = 0.3,
    num_ctx: int = 8192,
    timeout: int = 300,
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Call Ollama /api/chat expecting a JSON object; retry once on parse error."""
    messages: list[dict[str, str]] = [
        {"role": "system", "content": system},
        {"role": "user", "content": user},
    ]
    total_prompt = 0
    total_output = 0
    total_seconds = 0.0
    last_err: Exception | None = None

    for attempt in range(2):
        text, meta = _post_chat(
            model,
            messages,
            seed=seed + attempt,
            temperature=temperature,
            num_ctx=num_ctx,
            timeout=timeout,
        )
        total_prompt += meta["prompt_tokens"]
        total_output += meta["output_tokens"]
        total_seconds += meta["seconds"]
        try:
            obj = _extract_json_object(text)
            return obj, {
                "prompt_tokens": total_prompt,
                "output_tokens": total_output,
                "seconds": round(total_seconds, 2),
                "repaired": attempt > 0,
            }
        except ValueError as exc:
            last_err = exc
            messages.append({"role": "assistant", "content": text})
            messages.append(
                {
                    "role": "user",
                    "content": (
                        f"Your previous reply was not a valid JSON object ({exc}). "
                        "Reply with ONLY one valid JSON object matching the requested schema."
                    ),
                }
            )

    raise ValueError(f"Model {model} failed JSON output after repair retry: {last_err}")
