from typing import Dict, Any, List, Callable, Optional, Tuple
from device.workshop_tab.logging.workshop_logger import get_discovery_logger
from device.workshop_tab.logging.aggregated_frida_logger import aggregated_frida_logger
from device.workshop_tab.discovery.script_compiler import script_compiler
from device.workshop_tab.frida_session.session_manager import frida_session_manager

class ModifierScanner:
    def __init__(self, session, package_id: str, timestamp: str = None):
        self.session = session
        self.package_id = package_id
        self._logger = get_discovery_logger(package_id, timestamp)
        self._script = None
        self._cancelled = False
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
        elif "ClassNotFoundException" in error_str or "NoClassDefFoundError" in error_str:
            return ("CLASS_NOT_FOUND", error_str)
        else:
            return ("MODIFIER_SCAN_FAILED", error_str)
    
    def cancel(self):
        self._cancelled = True
    
    def is_cancelled(self) -> bool:
        return self._cancelled
    
    def is_session_lost(self) -> bool:
        return self._session_lost
    
    def scan_classes(
        self,
        class_names: List[str],
        scan_types: List[str],
        progress_callback: Optional[Callable[[int, int, str], None]] = None,
        save_callback: Optional[Callable[[str, Dict[str, Any]], None]] = None
    ) -> List[Dict[str, Any]]:
        self._logger.info(f"Starting modifier scan for {len(class_names)} classes")
        self._logger.info(f"Scan types: {', '.join(scan_types)}")
        self._cancelled = False
        results = []
        
        # Get session number for aggregated logging
        session_number = None
        for device_id, session_info in frida_session_manager._sessions.items():
            if session_info.get("session") == self.session:
                session_number = session_info.get("session_number")
                break
        
        if not class_names:
            self._logger.warning("No classes to scan")
            return results
        
        if not scan_types:
            self._logger.warning("No scan types specified")
            return results
        
        try:
            self._logger.info("Loading modifier scanner script (RPC-based)")
            if session_number:
                aggregated_frida_logger.log_script_loaded(session_number, "scan_modifiers.ts", "operation")
            
            script_code = script_compiler.compile("discovery", "scan_modifiers.ts")
            self._script = self.session.create_script(script_code)
            self._script.load()
            self._logger.info("Modifier scanner script loaded")
            
            import time
            start_time = time.time()
            total = len(class_names)
            
            for idx, class_name in enumerate(class_names):
                if self._cancelled:
                    self._logger.info(f"Modifier scan cancelled at {idx}/{total}")
                    break
                
                report_interval = 1 if total < 20 else (5 if total < 100 else 10)
                if progress_callback and (idx % report_interval == 0 or idx == 0):
                    progress_callback(idx + 1, total, class_name)
                
                try:
                    result = self._script.exports_sync.scan_modifiers(class_name, scan_types)
                    results.append(result)
                    
                    # Log modifier scan result to aggregated logger
                    if session_number:
                        if result.get("success"):
                            modifiers = {}
                            for scan_type in scan_types:
                                modifiers[scan_type] = result.get(scan_type, False)
                            aggregated_frida_logger.log_class_modifier_scanned(
                                session_number, 
                                class_name, 
                                True, 
                                modifiers
                            )
                        else:
                            aggregated_frida_logger.log_class_modifier_scanned(
                                session_number, 
                                class_name, 
                                False, 
                                None, 
                                result.get("error", "Unknown error")
                            )
                    
                    if save_callback and result.get("success"):
                        try:
                            save_callback(class_name, result)
                            self._logger.debug(f"[AUTO-SAVE] Callback triggered for: {class_name}")
                        except Exception as save_err:
                            self._logger.warning(f"[AUTO-SAVE] Callback failed for {class_name}: {save_err}")
                    
                    if not result.get("success"):
                        error_msg = result.get("error", "Unknown error")
                        error_type = "MODIFIER_SCAN_FAILED"
                        if "ClassNotFoundException" in error_msg or "NoClassDefFoundError" in error_msg:
                            error_type = "CLASS_NOT_FOUND"
                        
                        self._errors.append({
                            "phase": "scan_modifiers",
                            "class": class_name,
                            "error": error_msg,
                            "error_type": error_type
                        })
                        
                except Exception as e:
                    error_type, error_message = self._classify_error(e)
                    
                    self._errors.append({
                        "phase": "scan_modifiers",
                        "class": class_name,
                        "error": error_message,
                        "error_type": error_type
                    })
                    
                    if error_type in ["SESSION_DEAD", "SESSION_DETACHED", "TRANSPORT_ERROR"]:
                        self._session_lost = True
                        self._logger.error(f"Session lost during modifier scan at {idx+1}/{total}: {error_type}")
                        self._logger.error(f"Returning partial results - {len(results)} classes scanned before session loss")
                        break
                    
                    results.append({
                        "success": False,
                        "name": class_name,
                        "error": error_message
                    })
            
            if progress_callback:
                progress_callback(len(results), total, "complete")
            
            elapsed = time.time() - start_time
            self._logger.info(f"Scanned modifiers for {len(results)} classes")
            
            # Log modifier scan summary to aggregated logger
            if session_number:
                success_count = sum(1 for r in results if r.get("success"))
                error_count = len(results) - success_count
                aggregated_frida_logger.log_operation_complete(
                    session_number, 
                    "scan_modifiers", 
                    success_count, 
                    len(results), 
                    elapsed
                )
            
        except Exception as e:
            error_type, error_message = self._classify_error(e)
            self._logger.error(f"Modifier scan failed: {error_type} - {error_message}")
            self._errors.append({
                "phase": "scan_modifiers",
                "error": error_message,
                "error_type": error_type
            })
            if error_type in ["SESSION_DEAD", "SESSION_DETACHED", "TRANSPORT_ERROR"]:
                self._session_lost = True
            if session_number:
                aggregated_frida_logger.log_script_error(session_number, "scan_modifiers.ts", error_message)
        finally:
            if self._script:
                try:
                    self._script.unload()
                    self._logger.info("Modifier scanner script unloaded")
                    self._logger.info("[OPERATION_COMPLETE] Modifier scan finished")
                    if session_number:
                        aggregated_frida_logger.log_script_unloaded(session_number, "scan_modifiers.ts")
                except:
                    pass
                self._script = None
        
        return results
    
    def get_errors(self) -> List[Dict[str, str]]:
        return self._errors.copy()
    
    def get_stats(self) -> Dict[str, Any]:
        return {
            "errors": len(self._errors)
        }
