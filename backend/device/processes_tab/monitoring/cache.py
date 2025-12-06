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
            
            # Update last seen for all clients to keep session alive
            session["clients"][client_id] = current_time
            session["last_seen"] = current_time
            
            if session["primary_client"] == client_id:
                # Primary client updating interval
                session["interval_ms"] = interval_ms
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
            else:
                # Check if primary expired and promote this secondary
                primary_last_seen = session["clients"].get(session["primary_client"])
                if primary_last_seen and (current_time - primary_last_seen) > self._session_timeout:
                    old_primary = session["primary_client"]
                    session["primary_client"] = client_id
                    session["last_seen"] = current_time
                    logger.info(
                        f"[RUNTIME PRIMARY PROMOTED] Device {device_id}: "
                        f"{old_primary} (expired) -> {client_id} (now primary)"
                    )
            
            return session["interval_ms"]
    
    def get_interval(self, device_id: str) -> int:
        # Returns the active polling interval for a device (default 2000ms)
        with self._lock:
            session = self._sessions.get(device_id)
            if session:
                return session["interval_ms"]
            return 2000
    
    def get_ttl(self, device_id: str) -> float:
        # Returns cache TTL based on polling interval
        # TTL equals interval - cache serves concurrent requests in same tick only
        interval_ms = self.get_interval(device_id)
        return max(0.5, interval_ms / 1000.0)
    
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
        # Key format: "metric_type:device_serial:extra_params..."
        # Device serial formats: "emulator-5554" (no colon) or "127.0.0.1:5555" (IP:port)
        if self._polling_session:
            parts = key.split(":")
            if len(parts) >= 2:
                device_id = self._extract_device_id(parts)
                if device_id:
                    return self._polling_session.get_ttl(device_id)
        
        return self._default_ttl
    
    def _extract_device_id(self, parts: list) -> Optional[str]:
        # parts[0] = metric_type, parts[1] = device_serial (or IP), parts[2+] = extra params or port
        # IP:port format: parts[1] looks like IP, parts[2] is numeric port (4-5 digits)
        if len(parts) < 2:
            return None
        
        if len(parts) >= 3:
            # Check if parts[1] looks like an IP and parts[2] is a valid ADB port
            potential_ip = parts[1]
            potential_port = parts[2]
            
            is_ip_like = (
                potential_ip.replace(".", "").isdigit() and
                potential_ip.count(".") == 3
            )
            is_adb_port = (
                potential_port.isdigit() and
                len(potential_port) in (4, 5) and
                potential_port.startswith("5")
            )
            
            if is_ip_like and is_adb_port:
                return f"{potential_ip}:{potential_port}"
        
        # Simple device serial (no colon in serial itself)
        return parts[1]
    
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
# Session timeout should be longer than the longest expected polling interval
# to survive missed heartbeats, but short enough to detect closed tabs
polling_session = PollingSession(session_timeout=15.0)
device_metrics_cache = MetricsCache(default_ttl=1.5, polling_session=polling_session)

