"""Optional LLM-powered health assistant (OpenAI).

Activates automatically when an ``OPENAI_API_KEY`` is present in the environment;
otherwise callers should fall back to the offline rule-based assistant.

Safety design:
- A strict system prompt keeps the model to *general* wellness information, forbids
  diagnosis/prescription, and always defers to a licensed clinician.
- A local emergency pre-filter short-circuits red-flag messages *before* any API
  call, so urgent cases get an immediate, deterministic response.
- Any error (missing key, network, quota) returns ``None`` so the caller can fall
  back gracefully. No patient data is stored.
"""

from __future__ import annotations

import os
from functools import lru_cache

_MODEL = os.environ.get("OPENAI_MODEL", "gpt-4o-mini")

_SYSTEM_PROMPT = (
    "You are CareCompanion, a cautious, patient-friendly health assistant for an "
    "educational demo. Provide only general wellness and health-literacy information. "
    "You must NOT diagnose conditions, interpret personal test results, or recommend "
    "specific prescription medications or dosages. Keep answers concise (2-4 short "
    "sentences), use plain language, and always encourage the user to consult a "
    "licensed clinician for personal medical advice. If a message suggests a medical "
    "emergency, tell the user to call their local emergency number immediately. "
    "Never claim to be a doctor."
)

# Deterministic emergency handling runs before any network call.
_EMERGENCY_KEYWORDS = (
    "chest pain",
    "can't breathe",
    "cant breathe",
    "difficulty breathing",
    "unconscious",
    "suicide",
    "suicidal",
    "bleeding heavily",
    "stroke",
    "overdose",
)
_EMERGENCY_REPLY = (
    "This may be a medical emergency. Please stop and call your local emergency number "
    "or go to the nearest emergency department right now."
)


def is_available() -> bool:
    """Return True when an OpenAI API key is configured."""
    return bool(os.environ.get("OPENAI_API_KEY"))


@lru_cache(maxsize=1)
def _client():
    """Create and cache the OpenAI client (import kept local so it's optional)."""
    from openai import OpenAI

    return OpenAI()


def reply(message: str) -> dict | None:
    """Return an LLM reply for a patient message.

    Returns:
        A dict ``{"reply", "source", "intent"}`` on success, an emergency response
        for red-flag messages, or ``None`` when the LLM is unavailable or errors
        (so the caller can fall back to the rule-based assistant).
    """
    text = (message or "").lower().strip()

    if any(keyword in text for keyword in _EMERGENCY_KEYWORDS):
        return {"reply": _EMERGENCY_REPLY, "source": "safety-filter", "intent": "emergency"}

    if not is_available():
        return None

    try:
        response = _client().chat.completions.create(
            model=_MODEL,
            messages=[
                {"role": "system", "content": _SYSTEM_PROMPT},
                {"role": "user", "content": message},
            ],
            temperature=0.3,
            max_tokens=300,
        )
        content = (response.choices[0].message.content or "").strip()
        if not content:
            return None
        return {"reply": content, "source": f"OpenAI · {_MODEL}", "intent": "llm"}
    except Exception:
        # Any failure (network, quota, bad key) falls back to the rule-based path.
        return None
