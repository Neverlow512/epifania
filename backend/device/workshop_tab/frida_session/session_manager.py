# Frida session manager - attach/detach to running processes
import time
import threading
from typing import Dict, Any, Optional, Callable, Tuple
from pathlib import Path
from core.logger import get_logger
from core.log_paths import LOGS_WORKSHOP_FRIDA_SESSIONS
from device.workshop_tab.logging.workshop_logger import get_frida_logger

logger = get_logger(__name__, "backend")


class FridaSessionManager:
    def __init__(self):
        self._sessions: Dict[str, Dict[str, Any]] = {}
        self._lock = threading.Lock()
        self._frida = None
        self._session_counter = 0
        self._load_session_counter()
    
    def _get_frida(self):
        if self._frida is None:
            import frida
            self._frida = frida
        return self._frida
    
    def _load_session_counter(self):
        if not LOGS_WORKSHOP_FRIDA_SESSIONS.exists():
            return
        
        max_session_num = 0
        for folder in LOGS_WORKSHOP_FRIDA_SESSIONS.iterdir():
            if folder.is_dir() and folder.name.startswith("session_"):
                try:
                    session_num = int(folder.name.split("_")[1])
                    max_session_num = max(max_session_num, session_num)
                except (IndexError, ValueError):
                    continue
        
        self._session_counter = max_session_num
        if self._session_counter > 0:
            logger.info(f"Loaded session counter: {self._session_counter}")
    
    def _validate_session_health(self, session_info: Dict[str, Any]) -> Tuple[bool, str, str]:
        session = session_info.get("session")
        
        if not session:
            return (False, "no_session", "Session object not found")
        
        try:
            if session.is_detached:
                return (False, "detached", "Session was detached")
        except:
            return (False, "detached", "Session was detached")
        
        try:
            frida = self._get_frida()
            health_script = session.create_script("rpc.exports = { healthCheck: function() { return { pid: Process.id, alive: true }; } };")
            health_script.load()
            result = health_script.exports_sync.health_check()
            health_script.unload()
            return (True, "healthy", f"Session responsive (PID: {result.get('pid')})")
        except Exception as e:
            frida = self._get_frida()
            error_str = str(e)
            
            if isinstance(e, frida.InvalidOperationError):
                if "destroyed" in error_str or "script has been destroyed" in error_str:
                    return (False, "agent_crashed", "Agent destroyed")
                elif "detached" in error_str:
                    return (False, "detached", "Session detached")
            elif isinstance(e, frida.TransportError):
                return (False, "transport_error", "Connection lost")
            
            return (False, "unknown_error", error_str)
    
    def _verify_pid_exists(self, device_id: str, pid: int) -> bool:
        try:
            from core.device_manager import device_manager
            adb_manager = device_manager.adb_manager
            
            if not adb_manager:
                return True
            
            result = adb_manager.execute_shell(device_id, f"ps -p {pid} -o pid= 2>/dev/null || echo ''", timeout=5)
            
            if result and str(pid) in result:
                return True
            
            return False
        except Exception as e:
            logger.debug(f"PID verification failed for {pid}: {e}")
            return True
    
    def _cleanup_zombie_session(self, device_id: str, reason: str, session_info: Dict[str, Any]):
        from device.workshop_tab.logging.frida_session_logger import get_operations_logger, get_aggregate_logger
        
        session_number = session_info.get("session_number")
        pid = session_info.get("pid")
        
        if session_number:
            try:
                ops_logger = get_operations_logger(session_number)
                agg_logger = get_aggregate_logger(session_number)
                
                ops_logger.error(f"[SESSION_DEAD] Cleaning up zombie session - Reason: {reason}, PID: {pid}")
                agg_logger.error(f"[SESSION_DEAD] Reason: {reason}")
                
                from device.workshop_tab.logging.aggregated_frida_logger import aggregated_frida_logger
                aggregated_frida_logger.log_session_lost(session_number, reason)
            except Exception as e:
                logger.debug(f"Failed to log zombie cleanup: {e}")
        
        try:
            session = session_info.get("session")
            if session:
                session.detach()
        except Exception as e:
            logger.debug(f"Failed to detach zombie session: {e}")
        
        with self._lock:
            if device_id in self._sessions:
                del self._sessions[device_id]
        
        logger.info(f"Cleaned up zombie session for {device_id}, reason: {reason}")
    
    def attach(
        self,
        device_id: str,
        pid: int,
        on_detached: Optional[Callable] = None
    ) -> Dict[str, Any]:
        frida_log = get_frida_logger(device_id)
        
        with self._lock:
            existing = self._sessions.get(device_id)
            if existing and existing.get("pid") == pid:
                frida_log.info(f"Reusing existing session for PID {pid}")
                return {
                    "success": True,
                    "message": "Already attached to this process",
                    "session_reused": True,
                    "pid": pid
                }
            
            if existing:
                frida_log.info(f"Detaching from previous PID {existing.get('pid')} before attaching to {pid}")
                self._detach_internal(device_id, frida_log)
        
        try:
            frida = self._get_frida()
            frida_log.info(f"Getting Frida device: {device_id}")
            
            device = frida.get_device(device_id, timeout=10)
            frida_log.info(f"Device found: {device.name} ({device.type})")
            
            frida_log.info(f"Attaching to PID {pid}")
            session = device.attach(pid)
            
            def detached_handler(reason, crash):
                from device.workshop_tab.logging.frida_session_logger import get_operations_logger, get_aggregate_logger
                
                frida_log.warning(f"Session detached: {reason}")
                
                session_number = None
                with self._lock:
                    if device_id in self._sessions:
                        session_info = self._sessions.get(device_id)
                        session_number = session_info.get("session_number") if session_info else None
                        del self._sessions[device_id]
                    else:
                        for sid, sinfo in list(self._sessions.items()):
                            if sinfo.get("pid") == pid:
                                session_number = sinfo.get("session_number")
                                del self._sessions[sid]
                                break
                
                if session_number:
                    try:
                        ops_logger = get_operations_logger(session_number)
                        agg_logger = get_aggregate_logger(session_number)
                        
                        ops_logger.warning(f"[DETACHED] Reason: {reason}, Crash: {crash}")
                        agg_logger.warning(f"[DETACHED] {reason}")
                        
                        from device.workshop_tab.logging.aggregated_frida_logger import aggregated_frida_logger
                        aggregated_frida_logger.log_session_detached(session_number, str(reason))
                    except Exception as e:
                        logger.debug(f"Failed to log detachment: {e}")
                
                if on_detached:
                    try:
                        on_detached(device_id, pid, reason, crash)
                    except Exception as e:
                        logger.debug(f"on_detached callback failed: {e}")
            
            session.on('detached', detached_handler)
            
            from device.workshop_tab.logging.frida_session_logger import (
                create_session_logs, 
                cleanup_old_session_folders,
                get_operations_logger,
                get_aggregate_logger
            )
            
            self._session_counter += 1
            session_number = self._session_counter
            
            session_logs_folder = create_session_logs(session_number)
            
            cleanup_old_session_folders(keep_count=10)
            
            ops_logger = get_operations_logger(session_number)
            agg_logger = get_aggregate_logger(session_number)
            
            ops_logger.info(f"[SESSION_START] Attached to PID {pid} on device {device_id}")
            ops_logger.info(f"  Device: {device.name} ({device.type})")
            ops_logger.info(f"  Session Number: {session_number}")
            
            agg_logger.info(f"[ATTACHED] PID {pid} - {device.name}")
            
            from device.workshop_tab.logging.aggregated_frida_logger import aggregated_frida_logger
            aggregated_frida_logger.log_session_start(session_number, device_id, pid)
            
            with self._lock:
                self._sessions[device_id] = {
                    "device": device,
                    "session": session,
                    "pid": pid,
                    "device_name": device.name,
                    "session_number": session_number,
                    "attached_at": time.time(),
                    "last_health_check": None,
                    "health_status": "healthy",
                    "session_logs_folder": session_logs_folder
                }
            
            frida_log.info(f"Successfully attached to PID {pid}")
            logger.info(f"Frida attached to PID {pid} on {device_id}")
            
            return {
                "success": True,
                "message": f"Attached to PID {pid}",
                "session_reused": False,
                "pid": pid,
                "device_name": device.name
            }
            
        except Exception as e:
            error_msg = str(e)
            frida_log.error(f"Failed to attach to PID {pid}: {error_msg}")
            logger.error(f"Frida attach failed for {device_id}: {error_msg}")
            
            return {
                "success": False,
                "message": f"Failed to attach: {error_msg}",
                "pid": pid
            }

    def attach_by_package(
        self,
        device_id: str,
        package_id: str,
        spawn_if_needed: bool = False,
        on_detached: Optional[Callable] = None
    ) -> Dict[str, Any]:
        frida_log = get_frida_logger(device_id)
        
        try:
            frida = self._get_frida()
            frida_log.info(f"Getting Frida device: {device_id}")
            
            device = frida.get_device(device_id, timeout=10)
            frida_log.info(f"Device found: {device.name} ({device.type})")
            
            frida_log.info(f"Searching for running process for package: {package_id}")
            processes = device.enumerate_processes()
            target_pid = None
            
            for p in processes:
                name = getattr(p, "name", "") or ""
                if name == package_id or name.startswith(f"{package_id}:"):
                    target_pid = getattr(p, "pid", None)
                    break
            
            if target_pid is not None:
                frida_log.info(f"Found running PID {target_pid} for package {package_id}, attaching")
                return self.attach(device_id, int(target_pid), on_detached=on_detached)
            
            if spawn_if_needed:
                frida_log.info(f"No running process found for {package_id}, spawning and attaching")
                return self.spawn_and_attach(device_id, package_id, on_detached=on_detached)
            
            return {
                "success": False,
                "message": f"No running process found for package {package_id}",
                "package_id": package_id
            }
        except Exception as e:
            error_msg = str(e)
            frida_log.error(f"Failed to attach by package {package_id}: {error_msg}")
            logger.error(f"Frida attach_by_package failed for {device_id}: {error_msg}")
            return {
                "success": False,
                "message": f"Failed to attach: {error_msg}",
                "package_id": package_id
            }
    
    def spawn_and_attach(
        self,
        device_id: str,
        package_id: str,
        on_detached: Optional[Callable] = None
    ) -> Dict[str, Any]:
        frida_log = get_frida_logger(device_id)
        
        with self._lock:
            existing = self._sessions.get(device_id)
            if existing:
                frida_log.info(f"Detaching from previous session before spawning {package_id}")
                self._detach_internal(device_id, frida_log)
        
        try:
            frida = self._get_frida()
            frida_log.info(f"Getting Frida device: {device_id}")
            
            device = frida.get_device(device_id, timeout=10)
            frida_log.info(f"Device found: {device.name} ({device.type})")
            
            frida_log.info(f"Spawning package: {package_id}")
            pid = device.spawn([package_id])
            frida_log.info(f"Package spawned with PID {pid}")
            
            frida_log.info(f"Attaching to spawned PID {pid}")
            session = device.attach(pid)
            
            frida_log.info(f"Resuming spawned process {pid}")
            device.resume(pid)
            
            def detached_handler(reason, crash):
                from device.workshop_tab.logging.frida_session_logger import get_operations_logger, get_aggregate_logger
                
                frida_log.warning(f"Session detached: {reason}")
                
                session_number = None
                with self._lock:
                    if device_id in self._sessions:
                        session_info = self._sessions.get(device_id)
                        session_number = session_info.get("session_number") if session_info else None
                        del self._sessions[device_id]
                
                if session_number:
                    try:
                        ops_logger = get_operations_logger(session_number)
                        agg_logger = get_aggregate_logger(session_number)
                        ops_logger.warning(f"[DETACHED] Reason: {reason}, Crash: {crash}")
                        agg_logger.warning(f"[DETACHED] {reason}")
                        
                        from device.workshop_tab.logging.aggregated_frida_logger import aggregated_frida_logger
                        aggregated_frida_logger.log_session_detached(session_number, str(reason))
                    except Exception as e:
                        logger.debug(f"Failed to log detachment: {e}")
                
                if on_detached:
                    try:
                        on_detached(device_id, pid, reason, crash)
                    except Exception as e:
                        logger.debug(f"on_detached callback failed: {e}")
            
            session.on('detached', detached_handler)
            
            from device.workshop_tab.logging.frida_session_logger import (
                create_session_logs, 
                cleanup_old_session_folders,
                get_operations_logger,
                get_aggregate_logger
            )
            
            self._session_counter += 1
            session_number = self._session_counter
            
            session_logs_folder = create_session_logs(session_number)
            cleanup_old_session_folders(keep_count=10)
            
            ops_logger = get_operations_logger(session_number)
            agg_logger = get_aggregate_logger(session_number)
            
            ops_logger.info(f"[SESSION_START] Spawned and attached to {package_id} (PID {pid}) on device {device_id}")
            ops_logger.info(f"  Device: {device.name} ({device.type})")
            ops_logger.info(f"  Session Number: {session_number}")
            
            agg_logger.info(f"[SPAWNED] {package_id} - PID {pid} - {device.name}")
            
            from device.workshop_tab.logging.aggregated_frida_logger import aggregated_frida_logger
            aggregated_frida_logger.log_session_start(session_number, device_id, pid)
            
            with self._lock:
                self._sessions[device_id] = {
                    "device": device,
                    "session": session,
                    "pid": pid,
                    "device_name": device.name,
                    "session_number": session_number,
                    "attached_at": time.time(),
                    "last_health_check": None,
                    "health_status": "healthy",
                    "session_logs_folder": session_logs_folder,
                    "spawned_package": package_id
                }
            
            frida_log.info(f"Successfully spawned and attached to {package_id} (PID {pid})")
            logger.info(f"Frida spawned {package_id} (PID {pid}) on {device_id}")
            
            return {
                "success": True,
                "message": f"Spawned and attached to {package_id}",
                "pid": pid,
                "device_name": device.name,
                "package_id": package_id
            }
            
        except Exception as e:
            error_msg = str(e)
            frida_log.error(f"Failed to spawn {package_id}: {error_msg}")
            logger.error(f"Frida spawn failed for {device_id}: {error_msg}")
            
            return {
                "success": False,
                "message": f"Failed to spawn: {error_msg}",
                "package_id": package_id
            }
    
    def detach(self, device_id: str) -> Dict[str, Any]:
        from device.workshop_tab.logging.frida_session_logger import get_operations_logger, get_aggregate_logger
        
        frida_log = get_frida_logger(device_id)
        
        session_to_detach = None
        pid = None
        session_number = None
        
        with self._lock:
            session_info = self._sessions.get(device_id)
            if not session_info:
                return {
                    "success": True,
                    "message": "No active session to detach"
                }
            
            pid = session_info.get("pid")
            session_number = session_info.get("session_number")
            session_to_detach = session_info.get("session")
            del self._sessions[device_id]
        
        result = False
        if session_to_detach:
            try:
                frida_log.info(f"Detaching from PID {pid}")
                session_to_detach.detach()
                result = True
            except Exception as e:
                frida_log.error(f"Error during detach: {e}")
                result = False
        
        if session_number:
            try:
                ops_logger = get_operations_logger(session_number)
                agg_logger = get_aggregate_logger(session_number)
                ops_logger.info(f"[DETACHED] Manual detach from PID {pid}")
                agg_logger.info(f"[DETACHED] Manual detach")
            except Exception as e:
                logger.debug(f"Failed to log manual detachment: {e}")
        
        if result:
            logger.info(f"Frida detached from PID {pid} on {device_id}")
            return {
                "success": True,
                "message": f"Detached from PID {pid}",
                "pid": pid
            }
        else:
            return {
                "success": False,
                "message": "Failed to detach cleanly",
                "pid": pid
            }
    
    def _detach_internal(self, device_id: str, frida_log) -> bool:
        session_info = self._sessions.get(device_id)
        if not session_info:
            return True
        
        try:
            session = session_info.get("session")
            if session:
                frida_log.info(f"Detaching from PID {session_info.get('pid')}")
                session.detach()
            
            del self._sessions[device_id]
            return True
            
        except Exception as e:
            frida_log.error(f"Error during detach: {e}")
            if device_id in self._sessions:
                del self._sessions[device_id]
            return False
    
    def get_status(self, device_id: str) -> Dict[str, Any]:
        with self._lock:
            session_info = self._sessions.get(device_id)
            
            if not session_info:
                return {
                    "attached": False,
                    "pid": None,
                    "device_name": None
                }
            
            session = session_info.get("session")
            is_valid = False
            try:
                if session:
                    is_valid = session.is_detached == False
            except:
                pass
            
            if not is_valid:
                del self._sessions[device_id]
                return {
                    "attached": False,
                    "pid": None,
                    "device_name": None,
                    "note": "Session was invalidated"
                }
            
            return {
                "attached": True,
                "pid": session_info.get("pid"),
                "device_name": session_info.get("device_name"),
                "health_status": session_info.get("health_status", "unknown"),
                "last_health_check": session_info.get("last_health_check"),
                "attached_at": session_info.get("attached_at"),
                "session_number": session_info.get("session_number")
            }
    
    def get_session(self, device_id: str):
        from device.workshop_tab.logging.frida_session_logger import get_operations_logger, log_health_check
        
        with self._lock:
            session_info = self._sessions.get(device_id)
            if not session_info:
                return None
            
            session_number = session_info.get("session_number")
            
            is_healthy, health_status, health_message = self._validate_session_health(session_info)
            
            if session_number:
                log_health_check(session_number, health_status, health_message)
            
            if not is_healthy:
                self._cleanup_zombie_session(device_id, health_status, session_info)
                return None
            
            pid = session_info.get("pid")
            if pid and not self._verify_pid_exists(device_id, pid):
                if session_number:
                    ops_logger = get_operations_logger(session_number)
                    ops_logger.error(f"[PID_MISMATCH] PID {pid} no longer exists on device")
                self._cleanup_zombie_session(device_id, "pid_mismatch", session_info)
                return None
            
            session_info["last_health_check"] = time.time()
            session_info["health_status"] = "healthy"
            
            return session_info.get("session")
    
    def get_device(self, device_id: str):
        with self._lock:
            session_info = self._sessions.get(device_id)
            if session_info:
                return session_info.get("device")
            return None
    
    def is_attached(self, device_id: str) -> bool:
        status = self.get_status(device_id)
        return status.get("attached", False)
    
    def cleanup_all(self):
        with self._lock:
            device_ids = list(self._sessions.keys())
        
        for device_id in device_ids:
            self.detach(device_id)
        
        logger.info("Cleaned up all Frida sessions")


frida_session_manager = FridaSessionManager()

