"""Open-source medical data enrichment.

Fetches concise, authoritative background about a condition from the free and
open Wikipedia REST API. Results are cached in-memory for the process lifetime.
If the network is unavailable, callers should fall back to the local knowledge
base so the app keeps working fully offline.

No API key is required and no personal/patient data is ever transmitted—only the
name of a condition is sent to look up public reference material.
"""

from __future__ import annotations

from functools import lru_cache
from urllib.parse import quote

import requests

_WIKI_SUMMARY_URL = "https://en.wikipedia.org/api/rest_v1/page/summary/{title}"
_TIMEOUT_SECONDS = 5
_HEADERS = {"User-Agent": "carecompanion-ai/1.0 (educational demo)"}


@lru_cache(maxsize=128)
def fetch_condition_info(wiki_title: str) -> dict | None:
    """Fetch a public summary for a condition from the Wikipedia REST API.

    Args:
        wiki_title: The Wikipedia article title for the condition.

    Returns:
        A dict with ``summary``, ``url``, and ``source`` on success, or ``None``
        if the lookup fails (e.g. offline). Callers should degrade gracefully.
    """
    if not wiki_title:
        return None

    url = _WIKI_SUMMARY_URL.format(title=quote(wiki_title.replace(" ", "_")))
    try:
        response = requests.get(url, headers=_HEADERS, timeout=_TIMEOUT_SECONDS)
        response.raise_for_status()
        data = response.json()
    except (requests.RequestException, ValueError):
        return None

    extract = data.get("extract")
    if not extract:
        return None

    return {
        "summary": extract,
        "url": data.get("content_urls", {}).get("desktop", {}).get("page"),
        "source": "Wikipedia (open data)",
    }
