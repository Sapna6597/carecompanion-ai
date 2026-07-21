"""Machine-learning diagnosis model.

Trains a Bernoulli Naive Bayes classifier that maps a binary symptom vector to a
probable condition. Because a real labelled patient dataset can't ship in a demo,
we synthesise a realistic training set from the open knowledge base: for each
condition we generate many "patients" who usually present its characteristic
symptoms plus a little random noise. This produces a genuine, trainable model
with calibrated ``predict_proba`` output.

The model is trained once, lazily, and cached for the process lifetime.
"""

from __future__ import annotations

from functools import lru_cache

import numpy as np
from sklearn.naive_bayes import BernoulliNB

from . import knowledge_base

# Synthetic-data generation parameters.
_SAMPLES_PER_CONDITION = 400
_CORE_SYMPTOM_PROB = 0.85  # chance a characteristic symptom is reported
_NOISE_SYMPTOM_PROB = 0.03  # chance an unrelated symptom is reported
_RANDOM_SEED = 42


@lru_cache(maxsize=1)
def _vocab_index() -> dict[str, int]:
    return {symptom: i for i, symptom in enumerate(knowledge_base.symptom_vocabulary())}


def _vectorize(symptoms: list[str]) -> np.ndarray:
    """Convert a list of symptom strings into a binary feature vector."""
    index = _vocab_index()
    vector = np.zeros(len(index), dtype=np.int8)
    for symptom in symptoms:
        pos = index.get(symptom.strip().lower())
        if pos is not None:
            vector[pos] = 1
    return vector


@lru_cache(maxsize=1)
def _train_model() -> BernoulliNB:
    """Generate synthetic patients and train the classifier (cached)."""
    rng = np.random.default_rng(_RANDOM_SEED)
    vocab = knowledge_base.symptom_vocabulary()
    index = _vocab_index()
    conditions = knowledge_base.load_conditions()

    samples: list[np.ndarray] = []
    labels: list[str] = []

    for condition in conditions:
        core = set(condition["symptoms"])
        for _ in range(_SAMPLES_PER_CONDITION):
            vector = np.zeros(len(vocab), dtype=np.int8)
            for symptom in core:
                if rng.random() < _CORE_SYMPTOM_PROB:
                    vector[index[symptom]] = 1
            for symptom in vocab:
                if symptom not in core and rng.random() < _NOISE_SYMPTOM_PROB:
                    vector[index[symptom]] = 1
            samples.append(vector)
            labels.append(condition["disease"])

    model = BernoulliNB()
    model.fit(np.array(samples), np.array(labels))
    return model


def recognized_symptoms(symptoms: list[str]) -> tuple[list[str], list[str]]:
    """Split input symptoms into those known to the model and those unknown."""
    vocab = set(knowledge_base.symptom_vocabulary())
    known, unknown = [], []
    for symptom in symptoms:
        cleaned = symptom.strip().lower()
        if not cleaned:
            continue
        (known if cleaned in vocab else unknown).append(cleaned)
    return known, unknown


def predict(symptoms: list[str], top_k: int = 4) -> list[dict]:
    """Return the top-k probable conditions with model probabilities.

    Args:
        symptoms: Free-text symptom strings.
        top_k: Maximum number of conditions to return.

    Returns:
        A list of ``{"disease", "probability"}`` dicts sorted by probability.
    """
    known, _ = recognized_symptoms(symptoms)
    if not known:
        return []

    model = _train_model()
    vector = _vectorize(known).reshape(1, -1)
    probabilities = model.predict_proba(vector)[0]

    ranked = sorted(zip(model.classes_, probabilities), key=lambda pair: pair[1], reverse=True)
    return [
        {"disease": str(disease), "probability": round(float(prob), 4)}
        for disease, prob in ranked[:top_k]
    ]
