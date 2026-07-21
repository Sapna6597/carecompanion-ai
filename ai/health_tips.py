"""Daily health tips.

Provides a rotating, deterministic "tip of the day" plus the full catalogue.
Deterministic selection keeps the demo stable across reloads on the same day.
"""

from __future__ import annotations

from datetime import date

TIPS = [
    "Move for at least 30 minutes today—even a brisk walk counts.",
    "Fill half your plate with vegetables and fruit at your next meal.",
    "Take three slow, deep breaths when you feel stressed.",
    "Stand up and stretch once every hour of screen time.",
    "Keep a water bottle nearby to stay hydrated through the day.",
    "Wind down without screens 30 minutes before bed for better sleep.",
    "Wash your hands for 20 seconds to prevent common infections.",
    "Check in with a friend or family member—social health matters too.",
    "Swap one sugary drink for water today.",
    "Schedule that preventive check-up you've been putting off.",
]


def tip_of_the_day() -> dict:
    """Return a deterministic tip based on the current date."""
    index = date.today().toordinal() % len(TIPS)
    return {"date": date.today().isoformat(), "tip": TIPS[index]}


def all_tips() -> dict:
    """Return the full catalogue of health tips."""
    return {"count": len(TIPS), "tips": TIPS}
