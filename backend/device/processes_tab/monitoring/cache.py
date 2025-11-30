# Thread-safe caching for metrics that require delta calculations
# Prevents race conditions when multiple clients poll simultaneously

import time
import threading
import uuid
from typing import Dict, Any, Optional, Callable, Tuple
from core.logger import get_logger

logger = get_logger(__name__, "device")


class PollingSession:
    # Manages polling sessions per device to ensure single source of truth
    # First client to register becomes the "primary" and controls the interval
    
    def __init__(self, session_timeout: float = 10.0):
        self._sessions: Dict[str, Dict[str, Any]] = {}  # device_id -> session info
        self._lock = threading.Lock()
        self._session_timeout = session_timeout
    
    def register(self, device_id: str, client_id: str, interval_ms: int) -> Tuple[bool, str, int]:
        # Returns (is_primary, message, active_interval_ms)
        with self._lock:
            current_time = time.time()
            session = self._sessions.get(device_id)
            
            # Clean up expired session
            if session and (current_time - session["last_seen"]) > self._session_timeout:
                logger.info(f"Session expired for device {device_id}, clearing")
                del self._sessions[device_id]
                session = None
            
            if session is None:
                # First client becomes primary
                self._sessions[device_id] = {
                    "primary_client": client_id,
                    "interval_ms": interval_ms,
                    "last_seen": current_time,
                    "clients": {client_id: current_time}
                }
                logger.info(f"New primary session for {device_id}: client={client_id}, interval={interval_ms}ms")
                return True, "Primary session established", interval_ms
            
            # Update last seen for existing client
            session["clients"][client_id] = current_time
            
            if session["primary_client"] == client_id:
                # Primary client updating interval
                session["interval_ms"] = interval_ms
                session["last_seen"] = current_time
                return True, "Interval updated", interval_ms
            
            # Secondary client - cannot change interval
            active_interval = session["interval_ms"]
            if interval_ms != active_interval:
                return False, f"Another tab is controlling the polling interval ({active_interval}ms). Close other tabs to change the interval.", active_interval
            
            return False, "Secondary session (read-only)", active_interval
    
    def heartbeat(self, device_id: str, client_id: str) -> Optional[int]:
        # Updates last_seen timestamp, returns current interval or None if no session
        with self._lock:
            session = self._sessions.get(device_id)
            if not session:
                return None
            
            current_time = time.time()
            session["clients"][client_id] = current_time
            
            if session["primary_client"] == client_id:
                session["last_seen"] = current_time
            
            return session["interval_ms"]
    
    def get_interval(self, device_id: str) -> int:
        # Returns the active polling interval for a device (default 2000ms)
        with self._lock:
            session = self._sessions.get(device_id)
            if session:
                return session["interval_ms"]
            return 2000
    
    def get_ttl(self, device_id: str) -> float:
        # Returns cache TTL based on polling interval (slightly less than interval)
        interval_ms = self.get_interval(device_id)
        return max(0.5, (interval_ms / 1000.0) * 0.8)
    
    def unregister(self, device_id: str, client_id: str):
        with self._lock:
            session = self._sessions.get(device_id)
            if not session:
                return
            
            if client_id in session["clients"]:
                del session["clients"][client_id]
            
            # If primary client left, promote another or clear session
            if session["primary_client"] == client_id:
                if session["clients"]:
                    new_primary = next(iter(session["clients"]))
                    session["primary_client"] = new_primary
                    logger.info(f"Promoted {new_primary} to primary for {device_id}")
                else:
                    del self._sessions[device_id]
                    logger.info(f"Session cleared for {device_id}")
    
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


class MetricsCache:
    # Caches metric results with TTL to ensure consistent values across concurrent requests
    # Also serializes delta calculations to prevent race conditions
    
    def __init__(self, default_ttl: float = 1.0, polling_session: Optional['PollingSession'] = None):
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
    
    def _get_ttl(self, key: str, explicit_ttl: Optional[float]) -> float:
        if explicit_ttl is not None:
            return explicit_ttl
        
        # Try to get TTL from polling session based on device_id in key
        if self._polling_session:
            parts = key.split(":")
            if len(parts) >= 2:
                device_id = parts[1]
                return self._polling_session.get_ttl(device_id)
        
        return self._default_ttl
    
    def get_or_compute(
        self,
        key: str,
        compute_fn: Callable[[], Any],
        ttl: Optional[float] = None
    ) -> Any:
        # Returns cached value if fresh, otherwise computes and caches new value
        # Thread-safe: only one thread computes at a time per key
        
        cache_ttl = self._get_ttl(key, ttl)
        lock = self._get_lock(key)
        
        with lock:
            cached = self._cache.get(key)
            current_time = time.time()
            
            if cached and (current_time - cached["timestamp"]) < cache_ttl:
                logger.debug(f"Cache hit for {key}, age={current_time - cached['timestamp']:.2f}s")
                return cached["value"]
            
            # Cache miss or expired - compute new value
            logger.debug(f"Cache miss for {key}, computing...")
            value = compute_fn()
            
            self._cache[key] = {
                "value": value,
                "timestamp": current_time
            }
            
            return value
    
    def invalidate(self, key: str):
        lock = self._get_lock(key)
        with lock:
            if key in self._cache:
                del self._cache[key]
    
    def invalidate_prefix(self, prefix: str):
        # Invalidates all keys starting with prefix
        with self._global_lock:
            keys_to_remove = [k for k in self._cache.keys() if k.startswith(prefix)]
        
        for key in keys_to_remove:
            self.invalidate(key)
    
    def clear(self):
        with self._global_lock:
            self._cache.clear()


# Singleton instances
polling_session = PollingSession(session_timeout=10.0)
device_metrics_cache = MetricsCache(default_ttl=1.5, polling_session=polling_session)

