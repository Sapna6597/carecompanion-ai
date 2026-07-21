"""AI-assisted symptom analysis.

Combines three layers:

1. **Red-flag detection** — hard-coded safety rules that always flag emergencies.
2. **ML diagnosis** — a Bernoulli Naive Bayes model (``ai.ml_model``) ranks
   probable conditions from the reported symptoms.
3. **Open-data enrichment** — top conditions are enriched with public reference
   summaries from the Wikipedia REST API (``ai.open_data``), with a local
   fallback so the app still works offline.

This remains an *educational* tool and never replaces a licensed clinician.
"""

from __future__ import annotations

from . import knowledge_base, ml_model, open_data

# Symptoms that should always trigger an emergency recommendation.
RED_FLAG_SYMPTOMS = {
    "chest pain",
    "shortness of breath",
    "difficulty breathing",
    "severe bleeding",
    "loss of consciousness",
    "confusion",
    "slurred speech",
    "face drooping",
    "arm weakness",
    "pain radiating to arm",
    "sudden headache",
    "vision loss",
    "suicidal thoughts",
}

URGENCY_RANK = {"low": 0, "medium": 1, "high": 2, "emergency": 3}

_DISCLAIMER = (
    "This AI tool is for education only and does not provide a medical diagnosis. "
    "If you are worried about your health, contact a licensed clinician. "
    "In an emergency, call your local emergency number immediately."
)


def _normalize(symptoms: list[str]) -> list[str]:
    return [s.strip().lower() for s in symptoms if s and s.strip()]


def check_symptoms(symptoms: list[str], enrich: bool = True) -> dict:
    """Analyze reported symptoms and return a ranked, enriched assessment.

    Args:
        symptoms: A list of free-text symptom strings.
        enrich: When True, fetch open-source reference info for top conditions.

    Returns:
        A dict with the model-ranked conditions (probability, urgency, guidance,
        and optional open-data summary), an overall urgency, red flags, and the
        recognized/unrecognized symptom split.
    """
    reported = _normalize(symptoms)
    red_flags = sorted(set(reported) & RED_FLAG_SYMPTOMS)
    known, unknown = ml_model.recognized_symptoms(reported)

    predictions = ml_model.predict(reported, top_k=4)
    kb = knowledge_base.condition_by_name()

    possible_conditions = []
    for rank, pred in enumerate(predictions):
        record = kb.get(pred["disease"], {})
        matched = sorted(set(known) & set(record.get("symptoms", [])))
        condition = {
            "name": pred["disease"],
            "probability": pred["probability"],
            "matched_symptoms": matched,
            "description": record.get("description", ""),
            "self_care": record.get("self_care", ""),
            "urgency": record.get("urgency", "low"),
            "reference": None,
        }

        # Enrich only the top two matches to keep responses fast.
        if enrich and rank < 2:
            info = open_data.fetch_condition_info(record.get("wiki_title", ""))
            condition["reference"] = info or {
                "summary": record.get("description", ""),
                "url": None,
                "source": "Local knowledge base (offline)",
            }

        possible_conditions.append(condition)

    overall = "low"
    if red_flags:
        overall = "emergency"
    elif possible_conditions:
        overall = max(possible_conditions, key=lambda c: URGENCY_RANK[c["urgency"]])["urgency"]

    return {
        "engine": "BernoulliNB (scikit-learn) + open-data enrichment",
        "recognized_symptoms": known,
        "unrecognized_symptoms": unknown,
        "red_flags": red_flags,
        "overall_urgency": overall,
        "possible_conditions": possible_conditions,
        "disclaimer": _DISCLAIMER,
    }
