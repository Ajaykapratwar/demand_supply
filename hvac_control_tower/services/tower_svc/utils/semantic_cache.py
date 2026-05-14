import hashlib
from datetime import datetime, timedelta

class SemanticCache:
    def __init__(self, ttl_seconds: int = 3600):
        self.cache = {}         # {cache_key: {response, expires_at}}
        self.ttl = ttl_seconds
    
    def _make_key(self, user_message: str, kpi_snapshot_hash: str) -> str:
        """Key = hash(normalized question + current data context)"""
        normalized = user_message.lower().strip()
        combined = f"{normalized}|{kpi_snapshot_hash}"
        return hashlib.sha256(combined.encode()).hexdigest()[:16]
    
    def get(self, user_message: str, kpi_snapshot_hash: str) -> dict | None:
        key = self._make_key(user_message, kpi_snapshot_hash)
        entry = self.cache.get(key)
        if entry and datetime.now() < entry["expires_at"]:
            return entry["response"]
        return None
    
    def set(self, user_message: str, kpi_snapshot_hash: str, response: dict):
        key = self._make_key(user_message, kpi_snapshot_hash)
        self.cache[key] = {
            "response": response,
            "expires_at": datetime.now() + timedelta(seconds=self.ttl)
        }
    
    def invalidate_all(self):
        """Call when fact_financial data refreshes"""
        self.cache.clear()

global_semantic_cache = SemanticCache()
