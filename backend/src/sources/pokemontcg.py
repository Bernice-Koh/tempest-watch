"""Client for the pokemontcg.io REST API.

Fetches canonical card metadata and the embedded TCGplayer / Cardmarket market
prices. Returns parsed JSON dicts; turning those into domain models is the
service layer's job, not this module's. API reference: https://docs.pokemontcg.io/
"""

from typing import Any

import httpx
from tenacity import retry, retry_if_exception, stop_after_attempt, wait_exponential

from core.config import get_settings

_BASE_URL = "https://api.pokemontcg.io/v2"
_PAGE_SIZE = 250
_TIMEOUT = httpx.Timeout(30.0)


def _headers() -> dict[str, str]:
    """Return request headers, including the API key only if one is configured."""
    api_key = get_settings().pokemontcg_api_key
    return {"X-Api-Key": api_key} if api_key else {}


def _is_retryable(exc: BaseException) -> bool:
    """Return True for transient failures worth retrying.

    Retry on connection/timeout errors, rate limiting (429), and server errors
    (5xx). Do not retry client errors like 404 (not found) or 401 (bad key) —
    those will never succeed on a retry and should fail fast.
    """
    if isinstance(exc, httpx.TransportError):
        return True
    if isinstance(exc, httpx.HTTPStatusError):
        status = exc.response.status_code
        return status == 429 or status >= 500
    return False


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, max=10),
    retry=retry_if_exception(_is_retryable),
    reraise=True,
)
def _get(
    client: httpx.Client, path: str, params: dict[str, Any] | None = None
) -> dict[str, Any]:
    """Issue a GET request and return the parsed JSON body.

    Retries transient failures with exponential backoff (1s, 2s, 4s…). After
    three attempts, re-raises the original exception.
    """
    response = client.get(path, params=params)
    response.raise_for_status()
    body: dict[str, Any] = response.json()
    return body


def list_cards_in_set(set_id: str) -> list[dict[str, Any]]:
    """Fetch every card in a set, following pagination.

    Args:
        set_id: pokemontcg.io set identifier, e.g. "swsh12" for Silver Tempest.

    Returns:
        Raw card objects (parsed JSON dicts), one per card in the set.
    """
    cards: list[dict[str, Any]] = []
    page = 1
    with httpx.Client(
        base_url=_BASE_URL, headers=_headers(), timeout=_TIMEOUT
    ) as client:
        while True:
            body = _get(
                client,
                "/cards",
                params={"q": f"set.id:{set_id}", "page": page, "pageSize": _PAGE_SIZE},
            )
            batch: list[dict[str, Any]] = body.get("data", [])
            cards.extend(batch)
            total = body.get("totalCount", 0)
            if not batch or len(cards) >= total:
                break
            page += 1
    return cards


def get_card(card_id: str) -> dict[str, Any]:
    """Fetch a single card by its pokemontcg.io ID.

    Args:
        card_id: e.g. "swsh12-1".

    Returns:
        The raw card object (parsed JSON dict).
    """
    with httpx.Client(
        base_url=_BASE_URL, headers=_headers(), timeout=_TIMEOUT
    ) as client:
        body = _get(client, f"/cards/{card_id}")
    data: dict[str, Any] = body["data"]
    return data
