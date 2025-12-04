import os
import time
from typing import Any, Optional, Dict
from src.backend.utils.logger import setup_logger

logger = setup_logger(__name__)

_cache_store: Dict[str, Dict[str, Any]] = {}

ENABLE_CACHE = os.getenv("ENABLE_CACHE", "true").lower() == "true"

def set_cache(key: str, value: Any, ttl_seconds: int = 300) -> None:
    
    if not ENABLE_CACHE:
        return

    expiry = time.time() + ttl_seconds
    _cache_store[key] = {
        "value": value,
        "expiry": expiry
    }

def get_cache(key: str) -> Optional[Any]:
    
    if not ENABLE_CACHE:
        return None

    item = _cache_store.get(key)
    
    if not item:
        logger.debug(f"[Cache] Miss: {key}")
        return None
        
    if time.time() > item["expiry"]:
        logger.debug(f"[Cache] Expired: {key}")
        del _cache_store[key]
        return None
        
    logger.debug(f"[Cache] Hit: {key}")
    return item["value"]

def clear_cache(key: str) -> None:
    
    if key in _cache_store:
        del _cache_store[key]
        logger.info(f"[Cache] Invalidated: {key}")

def clear_all_cache() -> None:
    
    _cache_store.clear()
    logger.info("[Cache] Cleared all cache")
