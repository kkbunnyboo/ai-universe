"""
Joke service – fetches jokes from JokeAPI.dev and caches them in-memory
(or in Redis when available).
"""

import asyncio
import json
import logging
import time
from typing import Any, Dict, List, Optional

import aiohttp

from src.config import settings

logger = logging.getLogger(__name__)

JOKE_API_BASE = "https://v2.jokeapi.dev/joke"

# Map friendly type names to JokeAPI categories.
# Note: JokeAPI does not have a dedicated "knock-knock" category;
# we map it to "Misc" (general jokes).
CATEGORY_MAP: Dict[str, str] = {
    "general": "Misc",
    "programming": "Programming",
    "knock-knock": "Misc",
    "dark": "Dark",
    "pun": "Pun",
    "any": "Any",
}

# Simple in-memory cache: { cache_key: (timestamp, data) }
_memory_cache: Dict[str, tuple] = {}

# Optional Redis client (initialised lazily)
_redis_client: Any = None


def _get_redis():
    """Return a Redis client if REDIS_URL is configured, else None."""
    global _redis_client
    if _redis_client is not None:
        return _redis_client
    if not settings.REDIS_URL:
        return None
    try:
        import redis  # type: ignore

        _redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)
        _redis_client.ping()
        logger.info("Redis cache connected at %s", settings.REDIS_URL)
    except Exception as exc:
        logger.warning("Redis unavailable – using in-memory cache: %s", exc)
        _redis_client = None
    return _redis_client


def _cache_get(key: str) -> Optional[Dict]:
    """Read from Redis or fall back to in-memory cache."""
    redis = _get_redis()
    if redis:
        try:
            value = redis.get(key)
            if value:
                return json.loads(value)
        except Exception as exc:
            logger.warning("Redis GET failed: %s", exc)

    # In-memory fallback
    entry = _memory_cache.get(key)
    if entry:
        ts, data = entry
        if time.time() - ts < settings.JOKE_CACHE_TTL:
            return data
        del _memory_cache[key]
    return None


def _cache_set(key: str, data: Dict) -> None:
    """Write to Redis or fall back to in-memory cache."""
    redis = _get_redis()
    if redis:
        try:
            redis.setex(key, settings.JOKE_CACHE_TTL, json.dumps(data))
            return
        except Exception as exc:
            logger.warning("Redis SET failed: %s", exc)

    # In-memory fallback
    _memory_cache[key] = (time.time(), data)


def _format_joke(raw: Dict) -> Dict:
    """Normalise a raw JokeAPI response into our standard shape."""
    is_two_part = raw.get("type") == "twopart"
    return {
        "id": str(raw.get("id", "")),
        "category": raw.get("category", "Any").lower(),
        "is_two_part": is_two_part,
        "setup": raw.get("setup") if is_two_part else None,
        "delivery": raw.get("delivery") if is_two_part else None,
        "joke": raw.get("joke") if not is_two_part else None,
        "flags": raw.get("flags", {}),
        "safe": raw.get("safe", True),
        "language": raw.get("lang", "en"),
    }


async def fetch_joke(
    category: str = "any",
    safe_mode: bool = True,
    blacklist_flags: Optional[List[str]] = None,
) -> Dict:
    """
    Fetch a single joke from JokeAPI.

    Args:
        category: One of 'general', 'programming', 'knock-knock', 'dark', 'pun', 'any'.
        safe_mode: When True adds the safemode flag so no explicit content is returned.
        blacklist_flags: List of flags to suppress (e.g. ['nsfw', 'racist']).

    Returns:
        Normalised joke dict.
    """
    api_category = CATEGORY_MAP.get(category.lower(), "Any")
    cache_key = f"joke:{api_category}:safe={safe_mode}"

    cached = _cache_get(cache_key)
    if cached:
        logger.debug("Cache hit for %s", cache_key)
        return cached

    params: Dict[str, Any] = {"lang": "en", "format": "json"}
    if safe_mode:
        params["safe-mode"] = ""
    if blacklist_flags:
        params["blacklistFlags"] = ",".join(blacklist_flags)

    url = f"{JOKE_API_BASE}/{api_category}"

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params, timeout=aiohttp.ClientTimeout(total=5)) as resp:
                if resp.status != 200:
                    raise RuntimeError(f"JokeAPI returned HTTP {resp.status}")
                raw = await resp.json(content_type=None)
    except asyncio.TimeoutError:
        raise RuntimeError("JokeAPI request timed out")
    except Exception as exc:
        raise RuntimeError(f"Failed to fetch joke: {exc}") from exc

    if raw.get("error"):
        raise RuntimeError(raw.get("message", "JokeAPI error"))

    joke = _format_joke(raw)
    _cache_set(cache_key, joke)
    return joke


async def fetch_jokes_batch(
    category: str = "any",
    count: int = 5,
    safe_mode: bool = True,
) -> List[Dict]:
    """
    Fetch multiple jokes at once (uses JokeAPI's amount parameter).

    Args:
        category: Joke category.
        count: Number of jokes (1-10).
        safe_mode: Restrict to safe content.

    Returns:
        List of normalised joke dicts.
    """
    count = max(1, min(count, 10))
    api_category = CATEGORY_MAP.get(category.lower(), "Any")
    cache_key = f"jokes_batch:{api_category}:safe={safe_mode}:count={count}"

    cached = _cache_get(cache_key)
    if cached:
        return cached

    params: Dict[str, Any] = {"lang": "en", "format": "json", "amount": count}
    if safe_mode:
        params["safe-mode"] = ""

    url = f"{JOKE_API_BASE}/{api_category}"

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                if resp.status != 200:
                    raise RuntimeError(f"JokeAPI returned HTTP {resp.status}")
                raw = await resp.json(content_type=None)
    except asyncio.TimeoutError:
        raise RuntimeError("JokeAPI batch request timed out")
    except Exception as exc:
        raise RuntimeError(f"Failed to fetch jokes: {exc}") from exc

    if raw.get("error"):
        raise RuntimeError(raw.get("message", "JokeAPI error"))

    jokes_raw = raw.get("jokes", [raw])
    jokes = [_format_joke(j) for j in jokes_raw]
    _cache_set(cache_key, jokes)
    return jokes
