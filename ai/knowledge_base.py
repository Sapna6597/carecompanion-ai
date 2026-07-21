"""Knowledge base loader.

Loads the disease/symptom dataset from ``data/disease_symptoms.csv`` and exposes
it as structured records plus a sorted symptom vocabulary. The dataset uses a
pipe (``|``) delimiter because several free-text fields contain commas.
"""

from __future__ import annotations

import csv
import os
from functools import lru_cache

_DATA_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "disease_symptoms.csv")


@lru_cache(maxsize=1)
def load_conditions() -> list[dict]:
    """Load and cache all condition records from the dataset."""
    conditions: list[dict] = []
    with open(_DATA_PATH, newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle, delimiter="|")
        for row in reader:
            symptoms = [s.strip().lower() for s in row["symptoms"].split(";") if s.strip()]
            conditions.append(
                {
                    "disease": row["disease"].strip(),
                    "wiki_title": row["wiki_title"].strip(),
                    "symptoms": symptoms,
                    "description": row["description"].strip(),
                    "self_care": row["self_care"].strip(),
                    "urgency": row["urgency"].strip().lower(),
                }
            )
    return conditions


@lru_cache(maxsize=1)
def symptom_vocabulary() -> list[str]:
    """Return the sorted list of every unique symptom in the dataset."""
    vocab: set[str] = set()
    for condition in load_conditions():
        vocab.update(condition["symptoms"])
    return sorted(vocab)


@lru_cache(maxsize=1)
def condition_by_name() -> dict[str, dict]:
    """Return a mapping of disease name to its record."""
    return {c["disease"]: c for c in load_conditions()}
