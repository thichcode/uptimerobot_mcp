from typing import Any, Dict, Optional
from datetime import datetime, timedelta
import hashlib

class SimpleCache:
    def __init__(self, ttl: int = 3600):
        self._cache: Dict[str, tuple[Any, datetime]] = {}
        self.ttl = ttl
    
    def get(self, key: str) -> Optional[Any]:
        if key in self._cache:
            value, expires = self._cache[key]
            if datetime.now() < expires:
                return value
            del self._cache[key]
        return None
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        expires = datetime.now() + timedelta(seconds=ttl or self.ttl)
        self._cache[key] = (value, expires)
    
    def clear(self) -> None:
        self._cache.clear()
    
    def get_stats(self) -> Dict[str, Any]:
        valid_entries = sum(1 for _, exp in self._cache.values() if datetime.now() < exp)
        return {
            "total_entries": len(self._cache),
            "valid_entries": valid_entries,
            "expired_entries": len(self._cache) - valid_entries
        }

report_cache = SimpleCache()
monitor_cache = SimpleCache(ttl=300)
maintenance_cache = SimpleCache(ttl=600)

class CacheManager:
    def __init__(self):
        self._caches = {
            "report": report_cache,
            "monitor": monitor_cache,
            "maintenance": maintenance_cache
        }
    
    def get_cache(self, name: str) -> Optional[SimpleCache]:
        return self._caches.get(name)
    
    def get_all_stats(self) -> Dict[str, Dict[str, Any]]:
        return {name: cache.get_stats() for name, cache in self._caches.items()}

cache_manager = CacheManager()
