# ClassLoader scanner - on-demand ClassLoader extraction for Java classes
import time
from typing import Dict, Any, List, Callable, Optional, Tuple
from device.workshop_tab.logging.workshop_logger import get_discovery_logger
from device.workshop_tab.logging.aggregated_frida_logger import aggregated_frida_logger
from device.workshop_tab.discovery.script_compiler import script_compiler
from device.workshop_tab.frida_session.session_manager import frida_session_manager


class ClassLoaderScanner:
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
            return ("CLASSLOADER_SCAN_FAILED", error_str)
    
    def cancel(self):
        self._cancelled = True
    
    def is_cancelled(self) -> bool:
        return self._cancelled
    
    def is_session_lost(self) -> bool:
        return self._session_lost
    
    def scan_classes(
        self,
        class_names: List[str],
        progress_callback: Optional[Callable[[int, int, str], None]] = None,
        save_callback: Optional[Callable[[str, Dict[str, Any]], None]] = None
    ) -> List[Dict[str, Any]]:
        self._logger.info(f"Starting ClassLoader scan for {len(class_names)} classes")
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
        
        try:
            self._logger.info("Loading ClassLoader scanner script (RPC-based)")
            if session_number:
                aggregated_frida_logger.log_script_loaded(session_number, "scan_classloader.ts", "operation")
            
            script_code = script_compiler.compile("discovery", "scan_classloader.ts")
            self._script = self.session.create_script(script_code)
            self._script.load()
            self._logger.info("ClassLoader scanner script loaded")
            
            start_time = time.time()
            total = len(class_names)
            
            for idx, class_name in enumerate(class_names):
                if self._cancelled:
                    self._logger.info(f"ClassLoader scan cancelled at {idx}/{total}")
                    break
                
                # Report progress more frequently for small batches, less for large
                report_interval = 1 if total < 20 else (5 if total < 100 else 10)
                if progress_callback and (idx % report_interval == 0 or idx == 0):
                    progress_callback(idx + 1, total, class_name)
                
                try:
                    result = self._script.exports_sync.scan_class_loader(class_name)
                    results.append(result)
                    
                    # Log scan result to aggregated logger
                    if session_number:
                        if result.get("success"):
                            aggregated_frida_logger.log_class_scanned(
                                session_number, 
                                class_name, 
                                True, 
                                result.get("is_from_apk", False), 
                                result.get("loader_type")
                            )
                        else:
                            aggregated_frida_logger.log_class_scanned(
                                session_number, 
                                class_name, 
                                False, 
                                False, 
                                None, 
                                result.get("error", "Unknown error")
                            )
                    
                    # Per-class auto-save: Save immediately after each class is scanned
                    if save_callback and result.get("success"):
                        try:
                            save_callback(class_name, result)
                            self._logger.debug(f"[AUTO-SAVE] Callback triggered for: {class_name}")
                        except Exception as save_err:
                            self._logger.warning(f"[AUTO-SAVE] Callback failed for {class_name}: {save_err}")
                    
                    if not result.get("success"):
                        self._errors.append({
                            "phase": "scan_classloader",
                            "class": class_name,
                            "error": result.get("error", "Unknown error")
                        })
                        
                except Exception as e:
                    error_type, error_message = self._classify_error(e)
                    
                    self._errors.append({
                        "phase": "scan_classloader",
                        "class": class_name,
                        "error": error_message,
                        "error_type": error_type
                    })
                    
                    if error_type in ["SESSION_DEAD", "SESSION_DETACHED", "TRANSPORT_ERROR"]:
                        self._session_lost = True
                        self._logger.error(f"Session lost during scan: {error_type}")
                        break
                    
                    results.append({
                        "success": False,
                        "name": class_name,
                        "loader_type": "unknown",
                        "loader_path": None,
                        "is_from_apk": False,
                        "error": error_message
                    })
            
            if progress_callback:
                progress_callback(len(results), total, "complete")
            
            elapsed = time.time() - start_time
            self._logger.info(f"Scanned ClassLoader for {len(results)} classes")
            apk_count = sum(1 for r in results if r.get("is_from_apk", False))
            self._logger.info(f"Classes from APK: {apk_count}, System: {len(results) - apk_count}")
            
            # Log scan summary to aggregated logger
            if session_number:
                error_count = sum(1 for r in results if not r.get("success"))
                aggregated_frida_logger.log_scan_summary(
                    session_number, 
                    "scan_classloader", 
                    len(results), 
                    apk_count, 
                    len(results) - apk_count, 
                    error_count, 
                    elapsed
                )
            
        except Exception as e:
            self._logger.error(f"ClassLoader scan failed: {e}")
            self._errors.append({"phase": "scan_classloader", "error": str(e)})
            if session_number:
                aggregated_frida_logger.log_script_error(session_number, "scan_classloader.ts", str(e))
        finally:
            if self._script:
                try:
                    self._script.unload()
                    self._logger.info("ClassLoader scanner script unloaded")
                    self._logger.info("[OPERATION_COMPLETE] ClassLoader scan finished")
                    if session_number:
                        aggregated_frida_logger.log_script_unloaded(session_number, "scan_classloader.ts")
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
