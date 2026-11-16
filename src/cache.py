"""
Movie Cache
DS 3500 - MP3

Caches GET /movies responses in FakeRedis, one entry per limit.

Entries are stored as JSON strings, expire after 90 seconds, and are
cleared after any upload or processing request saves new data.
"""

import json
import logging

import fakeredis

logger = logging.getLogger(__name__)


class MovieCache:
    """In-memory cache of movie retrieval responses, keyed by limit."""

    def __init__(self):
        self.client = fakeredis.FakeRedis(decode_responses=True)

    def make_key(self, limit):
        """Return the cache key for a given limit."""
        return f"movies:limit:{limit}"

    def get(self, limit):
        """Return the cached response dictionary, or None."""
        key = self.make_key(limit)
        cached = self.client.get(key)
        if cached is None:
            logger.debug("Cache MISS: %s", key)
            return None
        logger.debug("Cache HIT: %s", key)
        return json.loads(cached)

    def set(self, limit, response):
        """Cache the response dictionary for 90 seconds."""
        key = self.make_key(limit)
        self.client.set(key, json.dumps(response), ex=90)

    def invalidate(self):
        """Remove all cached movie retrievals."""
        self.client.flushdb()
        logger.debug("Invalidated movie cache")
