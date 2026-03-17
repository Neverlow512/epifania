# Native module and export enumeration via Frida
from typing import Dict, Any, List, Callable, Optional, Tuple
from device.workshop_tab.logging.workshop_logger import get_discovery_logger
from device.workshop_tab.logging.aggregated_frida_logger import aggregated_frida_logger
from device.workshop_tab.discovery.script_loader import script_loader
from device.workshop_tab.frida_session.session_manager import frida_session_manager

class NativeDiscovery:
    def __init__(self, session, package_id: str, timestamp: str = None):
        self.session = session
        self.package_id = package_id
        self._logger = get_discovery_logger(package_id, timestamp)
        self._modules: List[Dict[str, Any]] = []
        self._errors: List[Dict[str, str]] = []
        self._session_lost = False
        self._frida = None
    
    def _get_frida(self):
        if self._frida is None:
            import frida
            self._frida = frida
        return self._frida
    
    def _classify_error(self, exception: Exception) -> Tuple[str, str]:
        frida = self._get_frida()
        error_str = str(exception)
        
        if isinstance(exception, frida.InvalidOperationError):
            if "destroyed" in error_str or "script has been destroyed" in error_str:
                return ("SESSION_DEAD", error_str)
            elif "detached" in error_str:
                return ("SESSION_DETACHED", error_str)
        elif isinstance(exception, frida.TransportError):
            return ("TRANSPORT_ERROR", error_str)
        else:
            return ("NATIVE_DISCOVERY_FAILED", error_str)
    
    def is_session_lost(self) -> bool:
        return self._session_lost
    
    def enumerate_modules(
        self,
        progress_callback: Optional[Callable[[int, str], None]] = None
    ) -> List[Dict[str, Any]]:
        self._logger.info("Starting native module enumeration")
        self._modules = []
        
        # Get session number for aggregated logging
        session_number = None
        for device_id, session_info in frida_session_manager._sessions.items():
            if session_info.get("session") == self.session:
                session_number = session_info.get("session_number")
                break
        
        if session_number:
            aggregated_frida_logger.log_native_discovery_start(session_number)
        
        try:
            script_code = script_loader.load_script("discovery", "enumerate_modules.js")
            
            if session_number:
                aggregated_frida_logger.log_script_loaded(session_number, "enumerate_modules.js", "discovery")
            
            received = {"done": False, "data": None}
            
            def on_message(message, data):
                if message["type"] == "send":
                    payload = message["payload"]
                    if payload.get("type") == "modules":
                        received["data"] = payload["data"]
                        received["done"] = True
            
            script = self.session.create_script(script_code)
            script.on("message", on_message)
            script.load()
            
            import time
            start = time.time()
            while not received["done"]:
                time.sleep(0.1)
            
            elapsed = time.time() - start
            self._logger.info(f"Module enumeration completed in {elapsed:.2f} seconds")
            
            script.unload()
            if session_number:
                aggregated_frida_logger.log_script_unloaded(session_number, "enumerate_modules.js")
            
            if received["data"]:
                for module in received["data"]:
                    module_data = {
                        "name": module["name"],
                        "path": module["path"],
                        "base_address": module["base"],
                        "size": module["size"],
                        "exports": []
                    }
                    self._modules.append(module_data)
            
            self._logger.info(f"Enumerated {len(self._modules)} native modules")
            
            # Log native discovery stats to aggregated logger
            if session_number:
                aggregated_frida_logger.log_performance_metric(session_number, "enumerate_modules", "duration", f"{elapsed:.2f}s")
                aggregated_frida_logger.log_performance_metric(session_number, "enumerate_modules", "module_count", len(self._modules))
            
            if progress_callback:
                progress_callback(len(self._modules), "modules_enumerated")
            
        except Exception as e:
            error_type, error_message = self._classify_error(e)
            self._logger.error(f"Module enumeration failed: {error_type} - {error_message}")
            self._errors.append({
                "phase": "enumerate_modules",
                "error": error_message,
                "error_type": error_type
            })
            if error_type in ["SESSION_DEAD", "SESSION_DETACHED", "TRANSPORT_ERROR"]:
                self._session_lost = True
                self._logger.error("Session lost during module enumeration")
            if session_number:
                aggregated_frida_logger.log_script_error(session_number, "enumerate_modules.js", error_message)
        
        return self._modules
    
    def enumerate_exports(
        self,
        modules: List[Dict[str, Any]],
        progress_callback: Optional[Callable[[int, int, str], None]] = None
    ) -> List[Dict[str, Any]]:
        self._logger.info(f"Starting export enumeration for {len(modules)} modules")
        
        # Get session number for aggregated logging
        session_number = None
        for device_id, session_info in frida_session_manager._sessions.items():
            if session_info.get("session") == self.session:
                session_number = session_info.get("session_number")
                break
        
        if not modules:
            self._logger.warning("No modules to enumerate exports for")
            return modules
        
        script = None
        try:
            script_code = script_loader.load_script("discovery", "enumerate_exports.js")
            script = self.session.create_script(script_code)
            script.load()
            self._logger.info("Export enumeration script loaded (RPC-based)")
            
            if session_number:
                aggregated_frida_logger.log_script_loaded(session_number, "enumerate_exports.js", "discovery")
            
            import time
            start_time = time.time()
            total = len(modules)
            
            for idx, module in enumerate(modules):
                if progress_callback and idx % 10 == 0:
                    progress_callback(idx, total, module.get("name", ""))
                
                module_name = module["name"]
                
                try:
                    result = script.exports_sync.get_exports(module_name)
                    
                    if result.get("success"):
                        exports_raw = result.get("exports", [])
                        exports = []
                        for export in exports_raw:
                            exports.append({
                                "name": export["name"],
                                "address": export["address"],
                                "type": export["type"]
                            })
                        module["exports"] = exports
                        module["export_count"] = len(exports)
                        
                        # Log native module processing to aggregated logger
                        if session_number:
                            aggregated_frida_logger.log_native_module(session_number, module_name, len(exports))
                    else:
                        module["exports"] = []
                        module["export_count"] = 0
                        error_msg = result.get("error", "Unknown error")
                        
                        error_type = "EXPORT_ENUMERATION_FAILED"
                        error_str_lower = error_msg.lower()
                        if "destroyed" in error_str_lower or "detached" in error_str_lower:
                            frida = self._get_frida()
                            if "destroyed" in error_str_lower:
                                error_type = "SESSION_DEAD"
                            elif "detached" in error_str_lower:
                                error_type = "SESSION_DETACHED"
                        
                        self._errors.append({
                            "phase": "enumerate_exports",
                            "module": module_name,
                            "error": error_msg,
                            "error_type": error_type
                        })
                        
                except Exception as e:
                    error_type, error_message = self._classify_error(e)
                    
                    self._errors.append({
                        "phase": "enumerate_exports",
                        "module": module_name,
                        "error": error_message,
                        "error_type": error_type
                    })
                    
                    if error_type in ["SESSION_DEAD", "SESSION_DETACHED", "TRANSPORT_ERROR"]:
                        self._session_lost = True
                        self._logger.error(f"Session lost during export enumeration at module {idx+1}/{total}: {error_type}")
                        self._logger.error(f"Returning partial results - {idx} modules processed before session loss")
                        break
                    
                    module["exports"] = []
                    module["export_count"] = 0
            
            elapsed = time.time() - start_time
            total_exports = sum(m.get("export_count", 0) for m in modules)
            self._logger.info(f"Enumerated {total_exports} exports across {len(modules)} modules")
            
            # Log native discovery completion to aggregated logger
            if session_number:
                stats = {
                    "module_count": len(modules),
                    "export_count": total_exports,
                    "duration": elapsed
                }
                aggregated_frida_logger.log_native_discovery_complete(session_number, stats)
            
        except Exception as e:
            error_type, error_message = self._classify_error(e)
            self._logger.error(f"Export enumeration failed: {error_type} - {error_message}")
            self._errors.append({
                "phase": "enumerate_exports",
                "error": error_message,
                "error_type": error_type
            })
            if error_type in ["SESSION_DEAD", "SESSION_DETACHED", "TRANSPORT_ERROR"]:
                self._session_lost = True
            if session_number:
                aggregated_frida_logger.log_script_error(session_number, "enumerate_exports.js", error_message)
        finally:
            if script:
                try:
                    script.unload()
                    self._logger.info("Export enumeration script unloaded")
                    self._logger.info("[OPERATION_COMPLETE] Export enumeration finished")
                    if session_number:
                        aggregated_frida_logger.log_script_unloaded(session_number, "enumerate_exports.js")
                except:
                    pass
        
        return modules
    
    def get_errors(self) -> List[Dict[str, str]]:
        return self._errors.copy()
    
    def get_stats(self) -> Dict[str, Any]:
        total_exports = sum(m.get("export_count", len(m.get("exports", []))) for m in self._modules)
        
        function_exports = sum(
            1 for m in self._modules
            for e in m.get("exports", [])
            if e.get("type") == "function"
        )
        
        return {
            "total_modules": len(self._modules),
            "total_exports": total_exports,
            "function_exports": function_exports,
            "errors": len(self._errors)
        }
