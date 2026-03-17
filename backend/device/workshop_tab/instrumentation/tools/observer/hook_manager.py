import time
import threading
from pathlib import Path
from typing import Dict, Any, Optional
from core.logger import get_logger

logger = get_logger(__name__, "device")


class ObserverHookManager:
    def __init__(self):
        self._sessions: Dict[str, Dict[str, Any]] = {}
        self._lock = threading.Lock()
    
    def start_observer_session(
        self,
        device_id: str,
        app_package: str,
        hooks: list,
        session_path: Path,
        script_ref,
        time_limit: Optional[int] = None,
        session_name: str = "",
        script_code: str = ""
    ) -> dict:
        with self._lock:
            hooks_dict = {}
            for hook in hooks:
                hook_id = hook.get("id")
                if hook_id:
                    hooks_dict[hook_id] = {
                        "type": hook.get("type", "java"),
                        "class_name": hook.get("class_name", ""),
                        "method_name": hook.get("method_name", ""),
                        "signature": hook.get("signature", ""),
                        "return_type": hook.get("return_type", ""),
                        "parameters": hook.get("parameters", []),
                        "status": "active",
                        "call_count": 0,
                        "error_count": 0,
                        "last_call": None
                    }
            
            self._sessions[device_id] = {
                "session_name": session_name,
                "app_package": app_package,
                "session_path": session_path,
                "script_ref": script_ref,
                "script_code": script_code,
                "start_time": time.time(),
                "time_limit": time_limit,
                "hooks": hooks_dict,
                "status": "active"
            }
            
            logger.info(f"Started observer session for {device_id}, session: {session_name}")
            
            return {
                "success": True,
                "session_name": session_name,
                "app_package": app_package,
                "hooks_count": len(hooks_dict)
            }
    
    def stop_observer_session(self, device_id: str) -> dict:
        with self._lock:
            session_info = self._sessions.get(device_id)
            if not session_info:
                return {
                    "success": False,
                    "message": "No active observer session"
                }
            
            session_info["status"] = "stopped"
            
            try:
                script = session_info.get("script_ref")
                if script:
                    script.unload()
            except Exception as e:
                logger.error(f"Failed to unload observer script: {e}")
            
            session_name = session_info.get("session_name")
            del self._sessions[device_id]
            
            logger.info(f"Stopped observer session {session_name} for {device_id}")
            
            return {
                "success": True,
                "session_name": session_name,
                "message": "Observer session stopped"
            }
    
    def get_session_status(self, device_id: str) -> Optional[Dict[str, Any]]:
        with self._lock:
            session_info = self._sessions.get(device_id)
            if not session_info:
                return None
            
            current_time = time.time()
            start_time = session_info.get("start_time", 0)
            elapsed = current_time - start_time
            
            hooks = session_info.get("hooks", {})
            
            # Calculate overall session statistics
            total_calls = 0
            total_errors = 0
            active_hooks = 0
            
            # Calculate per-hook statistics and aggregate totals
            enhanced_hooks = {}
            for hook_id, hook_data in hooks.items():
                call_count = hook_data.get("call_count", 0)
                error_count = hook_data.get("error_count", 0)
                
                total_calls += call_count
                total_errors += error_count
                
                if call_count > 0:
                    active_hooks += 1
                
                # Calculate call rate (calls per second over session duration)
                call_rate = 0.0
                if elapsed > 0 and call_count > 0:
                    call_rate = round(call_count / elapsed, 2)
                
                enhanced_hooks[hook_id] = {
                    **hook_data,
                    "call_rate": call_rate
                }
            
            # Calculate overall calls per second
            calls_per_second = 0.0
            if elapsed > 0:
                calls_per_second = round(total_calls / elapsed, 2)
            
            return {
                "session_name": session_info.get("session_name"),
                "app_package": session_info.get("app_package"),
                "session_path": str(session_info.get("session_path")),
                "status": session_info.get("status"),
                "start_time": start_time,
                "elapsed": elapsed,
                "time_limit": session_info.get("time_limit"),
                "hooks_count": len(hooks),
                "active_hooks": active_hooks,
                "total_calls": total_calls,
                "total_errors": total_errors,
                "calls_per_second": calls_per_second,
                "hooks": enhanced_hooks
            }
    
    def increment_hook_call_count(self, device_id: str, hook_id: str):
        with self._lock:
            session_info = self._sessions.get(device_id)
            if not session_info:
                return
            
            hooks = session_info.get("hooks", {})
            if hook_id in hooks:
                hooks[hook_id]["call_count"] = hooks[hook_id].get("call_count", 0) + 1
                hooks[hook_id]["last_call"] = time.time()
    
    def increment_hook_error_count(self, device_id: str, hook_id: str):
        with self._lock:
            session_info = self._sessions.get(device_id)
            if not session_info:
                return
            
            hooks = session_info.get("hooks", {})
            if hook_id in hooks:
                hooks[hook_id]["error_count"] = hooks[hook_id].get("error_count", 0) + 1
    
    def update_hook_stats(self, device_id: str, hook_id: str, stats: Dict[str, Any]):
        with self._lock:
            session_info = self._sessions.get(device_id)
            if not session_info:
                return
            
            hooks = session_info.get("hooks", {})
            if hook_id in hooks:
                hooks[hook_id].update(stats)
                hooks[hook_id]["last_call"] = time.time()
    
    def is_session_active(self, device_id: str) -> bool:
        with self._lock:
            session_info = self._sessions.get(device_id)
            if not session_info:
                return False
            return session_info.get("status") == "active"
    
    def get_top_hooks(self, device_id: str, limit: int = 5) -> list:
        with self._lock:
            session_info = self._sessions.get(device_id)
            if not session_info:
                return []
            
            hooks = session_info.get("hooks", {})
            current_time = time.time()
            start_time = session_info.get("start_time", 0)
            elapsed = current_time - start_time
            
            hook_list = []
            for hook_id, hook_data in hooks.items():
                call_count = hook_data.get("call_count", 0)
                call_rate = round(call_count / elapsed, 2) if elapsed > 0 else 0
                hook_list.append({
                    "hook_id": hook_id,
                    "class_name": hook_data.get("class_name", ""),
                    "method_name": hook_data.get("method_name", ""),
                    "call_count": call_count,
                    "call_rate": call_rate,
                    "error_count": hook_data.get("error_count", 0)
                })
            
            hook_list.sort(key=lambda x: x["call_rate"], reverse=True)
            
            return hook_list[:limit]
    
    def get_script_code(self, device_id: str) -> Optional[str]:
        with self._lock:
            session_info = self._sessions.get(device_id)
            if not session_info:
                return None
            return session_info.get("script_code")
    
    def cleanup_expired_sessions(self):
        current_time = time.time()
        with self._lock:
            expired_devices = []
            for device_id, session_info in self._sessions.items():
                time_limit = session_info.get("time_limit")
                if time_limit:
                    start_time = session_info.get("start_time", 0)
                    if current_time - start_time > time_limit:
                        expired_devices.append(device_id)
            
            for device_id in expired_devices:
                logger.info(f"Observer session for {device_id} expired due to time limit")
                self.stop_observer_session(device_id)


observer_hook_manager = ObserverHookManager()
