import hashlib
import time

# In-memory cache MVP
_cache = {}

def get_cache_key(query: str, dashboard_context: str) -> str:
    """Generate a deterministic key for semantic caching."""
    raw = f"{query.strip().lower()}_{dashboard_context}"
    return hashlib.md5(raw.encode()).hexdigest()

def check_semantic_cache(query: str, dashboard_context: str, ttl_seconds: int = 3600):
    key = get_cache_key(query, dashboard_context)
    if key in _cache:
        entry = _cache[key]
        if time.time() - entry["timestamp"] < ttl_seconds:
            return entry["response"]
    return None

def set_semantic_cache(query: str, dashboard_context: str, response: dict):
    key = get_cache_key(query, dashboard_context)
    _cache[key] = {
        "timestamp": time.time(),
        "response": response
    }
