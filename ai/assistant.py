"""Rule-based patient assistant.

A lightweight, offline conversational helper that answers common patient
questions with safe, general information. Intent is matched with keyword rules
so the demo works without any external AI service.
"""

from __future__ import annotations

# Ordered list of intents. The first matching intent wins.
INTENTS = [
    {
        "name": "emergency",
        "keywords": ["chest pain", "can't breathe", "cant breathe", "unconscious", "suicide", "bleeding heavily"],
        "response": (
            "This may be a medical emergency. Please stop using this tool and call your "
            "local emergency number or go to the nearest emergency department right now."
        ),
    },
    {
        "name": "greeting",
        "keywords": ["hello", "hi", "hey", "good morning", "good evening"],
        "response": "Hello! I'm your health assistant. I can share general wellness information. How can I help today?",
    },
    {
        "name": "medication",
        "keywords": ["medicine", "medication", "dosage", "pill", "prescription", "drug"],
        "response": (
            "Always take medication exactly as prescribed and read the label. Never share prescriptions. "
            "For dosage questions, check with your pharmacist or clinician."
        ),
    },
    {
        "name": "fever",
        "keywords": ["fever", "temperature", "hot"],
        "response": (
            "For a mild fever: rest, drink fluids, and monitor your temperature. Seek care if it stays above "
            "39.4°C (103°F), lasts more than 3 days, or comes with a stiff neck, rash, or confusion."
        ),
    },
    {
        "name": "hydration",
        "keywords": ["water", "hydration", "thirsty", "dehydrated"],
        "response": "Aim for regular fluid intake throughout the day. Increase fluids during illness, heat, or exercise.",
    },
    {
        "name": "sleep",
        "keywords": ["sleep", "insomnia", "tired", "rest"],
        "response": (
            "Most adults need 7–9 hours of sleep. Keep a consistent schedule, limit screens before bed, "
            "and avoid caffeine late in the day."
        ),
    },
    {
        "name": "appointment",
        "keywords": ["appointment", "book", "doctor", "clinic", "visit"],
        "response": (
            "To prepare for an appointment, note your symptoms, when they started, and any medications you take. "
            "This helps your clinician help you faster."
        ),
    },
]

FALLBACK = (
    "I can share general health and wellness information, but I can't diagnose conditions. "
    "For personal medical advice, please speak with a licensed clinician. "
    "You can also try the Symptom Checker on this site."
)


def reply(message: str) -> dict:
    """Return an assistant reply for a user message.

    Args:
        message: The patient's free-text message.

    Returns:
        A dict containing the matched intent and the reply text.
    """
    text = (message or "").lower().strip()

    for intent in INTENTS:
        if any(keyword in text for keyword in intent["keywords"]):
            return {"intent": intent["name"], "reply": intent["response"]}

    return {"intent": "fallback", "reply": FALLBACK}
