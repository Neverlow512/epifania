# Process Overview caching - dedicated cache for process inspection data
# Separate from Runtime Overview cache to allow independent TTL and session management

import time
import threading
from typing import Dict, Any, Optional, Callable, Tuple
from core.logger import get_logger

logger = get_logger(__name__, "device")


class OverviewPollingSession:
    # Manages polling sessions for Process Overview panel per device
    # Tracks which client controls the refresh interval for the overview
    
    def __init__(self, session_timeout: float = 15.0):
        self._sessions: Dict[str, Dict[str, Any]] = {}
        self._lock = threading.Lock()
        self._session_timeout = session_timeout
    
    def register(
        self, device_id: str, client_id: str, interval_ms: int
    ) -> Tuple[bool, str, int]:
        with self._lock:
            current_time = time.time()
            session = self._sessions.get(device_id)
            
            if session and (current_time - session["last_seen"]) > self._session_timeout:
                logger.info(f"Overview session expired for {device_id}, clearing")
                del self._sessions[device_id]
                session = None
            
            if session is None:
                self._sessions[device_id] = {
                    "primary_client": client_id,
                    "interval_ms": interval_ms,
                    "last_seen": current_time,
                    "clients": {client_id: current_time}
                }
                logger.info(
                    f"New overview session for {device_id}: "
                    f"client={client_id}, interval={interval_ms}ms"
                )
                return True, "Primary overview session established", interval_ms
            
            # Update last seen for all clients to keep session alive
            session["clients"][client_id] = current_time
            session["last_seen"] = current_time
            
            if session["primary_client"] == client_id:
                session["interval_ms"] = interval_ms
                return True, "Overview interval updated", interval_ms
            
            active_interval = session["interval_ms"]
            if interval_ms != active_interval:
                return (
                    False,
                    f"Another tab controls overview polling ({active_interval}ms)",
                    active_interval
                )
            
            return False, "Secondary overview session", active_interval
    
    def unregister(self, device_id: str, client_id: str):
        with self._lock:
            session = self._sessions.get(device_id)
            if not session:
                return
            
            if client_id in session["clients"]:
                del session["clients"][client_id]
            
            if session["primary_client"] == client_id:
                if session["clients"]:
                    new_primary = next(iter(session["clients"]))
                    session["primary_client"] = new_primary
                    logger.info(f"Promoted {new_primary} to overview primary for {device_id}")
                else:
                    del self._sessions[device_id]
                    logger.info(f"Overview session cleared for {device_id}")
    
    def get_interval(self, device_id: str) -> int:
        with self._lock:
            session = self._sessions.get(device_id)
            if session:
                return session["interval_ms"]
            return 5000  # Default 5s for overview (less frequent than process list)
    
    def get_ttl(self, device_id: str) -> float:
        interval_ms = self.get_interval(device_id)
        return max(1.0, (interval_ms / 1000.0) * 0.8)
    
    def get_session_info(self, device_id: str) -> Optional[Dict]:
        with self._lock:
            session = self._sessions.get(device_id)
            if not session:
                return None
            return {
                "primary_client": session["primary_client"],
                "interval_ms": session["interval_ms"],
                "client_count": len(session["clients"])
            }


class ProcessOverviewCache:
    # Caches process overview data with TTL per PID
    # Thread-safe with per-key locking to prevent concurrent computation
    
    def __init__(
        self, 
        default_ttl: float = 3.0, 
        polling_session: Optional[OverviewPollingSession] = None
    ):
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._locks: Dict[str, threading.Lock] = {}
        self._global_lock = threading.Lock()
        self._default_ttl = default_ttl
        self._polling_session = polling_session
    
    def _get_lock(self, key: str) -> threading.Lock:
        with self._global_lock:
            if key not in self._locks:
                self._locks[key] = threading.Lock()
            return self._locks[key]
    
    def _get_ttl(self, device_id: str, explicit_ttl: Optional[float]) -> float:
        if explicit_ttl is not None:
            return explicit_ttl
        
        if self._polling_session:
            return self._polling_session.get_ttl(device_id)
        
        return self._default_ttl
    
    def _make_key(self, device_id: str, pid: int) -> str:
        return f"overview:{device_id}:{pid}"
    
    def get_or_compute(
        self,
        device_id: str,
        pid: int,
        compute_fn: Callable[[], Any],
        ttl: Optional[float] = None
    ) -> Tuple[Any, bool, float]:
        # Returns (value, is_cached, age_seconds)
        key = self._make_key(device_id, pid)
        cache_ttl = self._get_ttl(device_id, ttl)
        lock = self._get_lock(key)
        
        with lock:
            cached = self._cache.get(key)
            current_time = time.time()
            
            if cached and (current_time - cached["timestamp"]) < cache_ttl:
                age = current_time - cached["timestamp"]
                logger.debug(f"Overview cache hit for {key}, age={age:.2f}s")
                return cached["value"], True, age
            
            logger.debug(f"Overview cache miss for {key}, computing...")
            value = compute_fn()
            
            self._cache[key] = {
                "value": value,
                "timestamp": current_time
            }
            
            return value, False, 0.0
    
    def invalidate(self, device_id: str, pid: int):
        key = self._make_key(device_id, pid)
        lock = self._get_lock(key)
        with lock:
            if key in self._cache:
                del self._cache[key]
                logger.debug(f"Invalidated overview cache for {key}")
    
    def invalidate_device(self, device_id: str):
        prefix = f"overview:{device_id}:"
        with self._global_lock:
            keys_to_remove = [k for k in self._cache.keys() if k.startswith(prefix)]
        
        for key in keys_to_remove:
            lock = self._get_lock(key)
            with lock:
                if key in self._cache:
                    del self._cache[key]
        
        logger.debug(f"Invalidated {len(keys_to_remove)} overview cache entries for {device_id}")
    
    def get_cache_info(self, device_id: str, pid: int) -> Optional[Dict]:
        key = self._make_key(device_id, pid)
        with self._global_lock:
            cached = self._cache.get(key)
            if not cached:
                return None
            
            current_time = time.time()
            return {
                "age_seconds": current_time - cached["timestamp"],
                "timestamp": cached["timestamp"]
            }
    
    def clear(self):
        with self._global_lock:
            self._cache.clear()
            logger.info("Overview cache cleared")


# Singleton instances for Process Overview
# Session timeout should be short enough to handle tab reloads gracefully
overview_polling_session = OverviewPollingSession(session_timeout=8.0)
process_overview_cache = ProcessOverviewCache(
    default_ttl=3.0, 
    polling_session=overview_polling_session
)

