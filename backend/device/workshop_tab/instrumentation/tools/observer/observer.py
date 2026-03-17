import json
import time
import threading
import traceback
from typing import List, Dict, Any, Optional
from datetime import datetime
from core.logger import get_logger
from device.workshop_tab.instrumentation.tools.observer.hook_manager import observer_hook_manager
from device.workshop_tab.instrumentation.tools.observer.script_generator import (
    generate_java_observer_script,
    generate_native_observer_script,
    generate_hook_id
)
from device.workshop_tab.instrumentation.tools.observer.logging.observer_logger import (
    create_observer_session,
    get_operations_logger,
    get_aggregated_logger,
    get_console_logger,
    get_hook_logger,
    update_summary,
    write_metadata
)
from device.workshop_tab.instrumentation.tools.observer.logging.log_paths import (
    generate_session_name
)

logger = get_logger(__name__, "device")


class Observer:
    def __init__(self, device_id: str, session):
        self.device_id = device_id
        self.session = session
        self._script = None
        self._script_code = None
        self._message_handlers = []
        self._session_path = None
        self._session_name = None
        self._timer_thread = None
        self._stop_timer = False
        self._hooks_map = {}
        self._stats_update_thread = None
        self._stop_stats_update = False
    
    def start_observation(
        self,
        app_package: str,
        hooks: List[dict],
        time_limit: Optional[int] = None
    ) -> dict:
        if not hooks:
            return {
                "success": False,
                "message": "No hooks provided"
            }
        
        for hook in hooks:
            if "type" not in hook or hook["type"] not in ["java", "native"]:
                return {
                    "success": False,
                    "message": f"Invalid hook type: {hook.get('type')}"
                }
            
            if hook["type"] == "java":
                if "class_name" not in hook or "method_name" not in hook:
                    return {
                        "success": False,
                        "message": "Java hooks require class_name and method_name"
                    }
            elif hook["type"] == "native":
                if "module_name" not in hook or "function_name" not in hook:
                    return {
                        "success": False,
                        "message": "Native hooks require module_name and function_name"
                    }
            
            if "id" not in hook:
                hook["id"] = generate_hook_id(hook)
        
        java_hooks = [h for h in hooks if h.get("type") == "java"]
        native_hooks = [h for h in hooks if h.get("type") == "native"]
        
        try:
            if java_hooks and native_hooks:
                return {
                    "success": False,
                    "message": "Cannot mix Java and Native hooks in same session"
                }
            
            if java_hooks:
                script_code, hooks_with_ids = generate_java_observer_script(java_hooks)
            else:
                script_code, hooks_with_ids = generate_native_observer_script(native_hooks)
            
            self._script_code = script_code
            self._session_name = generate_session_name()
            self._session_path = create_observer_session(app_package, self._session_name)
            
            for hook in hooks_with_ids:
                self._hooks_map[hook['id']] = {
                    'class_name': hook.get('class_name', ''),
                    'method_name': hook.get('method_name', '')
                }
            
            ops_logger = get_operations_logger(self._session_path)
            agg_logger = get_aggregated_logger(self._session_path)
            console_logger = get_console_logger(self._session_path)
            
            self._script = self.session.create_script(script_code)
            ops_logger.info(f"Observer script created, loading...")
            self._script.load()
            ops_logger.info("Observer script loaded, installing hooks...")
            
            try:
                result = self._script.exports_sync.install_hooks(hooks_with_ids)
                ops_logger.info(f"Hooks installation result: {result}")
            except Exception as e:
                ops_logger.error(f"Failed to install hooks: {e}")
                return {
                    "success": False,
                    "message": f"Failed to install hooks: {str(e)}"
                }
            
            def on_message(message, data):
                try:
                    console_logger.debug(f"RAW: {json.dumps(message, default=str)}")
                    if data:
                        console_logger.debug(f"DATA: {data}")
                    
                    if message.get("type") == "send":
                        payload = message.get("payload", {})
                        
                        if payload.get("type") == "hook_event":
                            hook_id = payload.get("hook_id")
                            event_type = payload.get("event_type")
                            timestamp = payload.get("timestamp")
                            
                            log_msg = f"[{hook_id}] {event_type.upper()}"
                            if event_type == "entry":
                                log_msg += f" - Args: {payload.get('args', [])}"
                            elif event_type == "exit":
                                log_msg += f" - Return: {payload.get('return_value')}, Duration: {payload.get('duration_ms')}ms"
                                if payload.get('error'):
                                    log_msg += f", Error: {payload.get('error')}"
                            
                            agg_logger.info(log_msg)
                            
                            hook_info = self._hooks_map.get(hook_id, {})
                            hook_logger = get_hook_logger(
                                self._session_path, 
                                hook_id,
                                hook_info.get('class_name', ''),
                                hook_info.get('method_name', '')
                            )
                            hook_logger.info(log_msg)
                            
                            if event_type == "exit":
                                observer_hook_manager.increment_hook_call_count(self.device_id, hook_id)
                                
                                # Track errors if present
                                if payload.get('error'):
                                    observer_hook_manager.increment_hook_error_count(self.device_id, hook_id)
                        else:
                            console_logger.info(f"Frida message: {message}")
                    elif message.get("type") == "error":
                        ops_logger.error(f"Frida script error: {message}")
                        console_logger.error(f"Error: {message}")
                except Exception as e:
                    logger.error(f"Error handling Frida message: {e}")
            
            self._script.on("message", on_message)
            
            session_result = observer_hook_manager.start_observer_session(
                self.device_id,
                app_package,
                hooks,
                self._session_path,
                self._script,
                time_limit,
                self._session_name,
                self._script_code
            )
            
            metadata = {
                "session_name": self._session_name,
                "app_package": app_package,
                "device_id": self.device_id,
                "start_time": datetime.now().isoformat(),
                "time_limit": time_limit,
                "hooks": hooks
            }
            write_metadata(self._session_path, metadata)
            
            if time_limit:
                self._start_timer(time_limit)
            
            self._start_stats_updater()
            
            return {
                "success": True,
                "message": "Observer started successfully",
                "session_name": self._session_name,
                "hooks_count": len(hooks),
                "session_path": str(self._session_path)
            }
            
        except Exception as e:
            logger.error(f"Failed to start observer: {e}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            return {
                "success": False,
                "message": f"Failed to start observer: {str(e)}"
            }
    
    def stop_observation(self) -> dict:
        try:
            if self._timer_thread:
                self._stop_timer = True
                self._timer_thread.join(timeout=2)
            
            if self._stats_update_thread:
                self._stop_stats_update = True
                self._stats_update_thread.join(timeout=2)
            
            if self._session_path:
                session_status = observer_hook_manager.get_session_status(self.device_id)
                if session_status:
                    top_hooks = observer_hook_manager.get_top_hooks(self.device_id, limit=10)
                    
                    summary = {
                        "session_start": datetime.fromtimestamp(session_status.get("start_time", 0)).isoformat(),
                        "last_update": datetime.now().isoformat(),
                        "status": "stopped",
                        "time_limit": session_status.get("time_limit"),
                        "elapsed": session_status.get("elapsed"),
                        "total_calls": session_status.get("total_calls", 0),
                        "total_errors": session_status.get("total_errors", 0),
                        "calls_per_second": session_status.get("calls_per_second", 0),
                        "active_hooks": session_status.get("active_hooks", 0),
                        "top_hooks": top_hooks,
                        "hooks": session_status.get("hooks", {})
                    }
                    update_summary(self._session_path, summary)
                    
                    stats_data = {
                        "session_start": summary["session_start"],
                        "last_update": summary["last_update"],
                        "status": "stopped",
                        "elapsed": summary["elapsed"],
                        "time_limit": summary["time_limit"],
                        "total_calls": summary["total_calls"],
                        "total_errors": summary["total_errors"],
                        "calls_per_second": summary["calls_per_second"],
                        "active_hooks": summary["active_hooks"],
                        "hooks_count": session_status.get("hooks_count", 0),
                        "top_hooks": top_hooks
                    }
                    
                    stats_file = self._session_path / "stats.json"
                    with open(stats_file, 'w') as f:
                        json.dump(stats_data, f, indent=2)
                
                ops_logger = get_operations_logger(self._session_path)
                ops_logger.info("Observer session stopped")
            
            result = observer_hook_manager.stop_observer_session(self.device_id)
            
            return result
        except Exception as e:
            logger.error(f"Failed to stop observer: {e}")
            return {
                "success": False,
                "message": f"Failed to stop observer: {str(e)}"
            }
    
    def _start_timer(self, time_limit: int):
        def timer_thread():
            time.sleep(time_limit)
            if not self._stop_timer:
                logger.info(f"Observer time limit reached for {self.device_id}")
                if self._session_path:
                    ops_logger = get_operations_logger(self._session_path)
                    ops_logger.info(f"Observer stopped: time limit of {time_limit}s reached")
                self.stop_observation()
        
        self._timer_thread = threading.Thread(target=timer_thread, daemon=True)
        self._timer_thread.start()
    
    def _start_stats_updater(self):
        def stats_update_thread():
            while not self._stop_stats_update:
                try:
                    if self._session_path and observer_hook_manager.is_session_active(self.device_id):
                        session_status = observer_hook_manager.get_session_status(self.device_id)
                        if session_status:
                            top_hooks = observer_hook_manager.get_top_hooks(self.device_id, limit=10)
                            
                            stats_data = {
                                "session_start": datetime.fromtimestamp(session_status.get("start_time", 0)).isoformat(),
                                "last_update": datetime.now().isoformat(),
                                "status": "active",
                                "elapsed": session_status.get("elapsed"),
                                "time_limit": session_status.get("time_limit"),
                                "total_calls": session_status.get("total_calls", 0),
                                "total_errors": session_status.get("total_errors", 0),
                                "calls_per_second": session_status.get("calls_per_second", 0),
                                "active_hooks": session_status.get("active_hooks", 0),
                                "hooks_count": session_status.get("hooks_count", 0),
                                "top_hooks": top_hooks
                            }
                            
                            stats_file = self._session_path / "stats.json"
                            with open(stats_file, 'w') as f:
                                json.dump(stats_data, f, indent=2)
                            
                            summary_data = {
                                **stats_data,
                                "hooks": session_status.get("hooks", {})
                            }
                            update_summary(self._session_path, summary_data)
                    
                    time.sleep(1)
                except Exception as e:
                    logger.error(f"Error updating stats: {e}")
        
        self._stats_update_thread = threading.Thread(target=stats_update_thread, daemon=True)
        self._stats_update_thread.start()
