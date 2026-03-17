# Java class and method enumeration via Frida
from typing import Dict, Any, List, Callable, Optional, Tuple
from device.workshop_tab.logging.workshop_logger import get_discovery_logger
from device.workshop_tab.logging.aggregated_frida_logger import aggregated_frida_logger
from device.workshop_tab.discovery.script_compiler import script_compiler
from device.workshop_tab.frida_session.session_manager import frida_session_manager

class JavaDiscovery:
    def __init__(self, session, package_id: str, timestamp: str = None):
        self.session = session
        self.package_id = package_id
        self._logger = get_discovery_logger(package_id, timestamp)
        self._classes: List[str] = []
        self._class_data: List[Dict[str, Any]] = []
        self._errors: List[Dict[str, str]] = []
        self._cancelled = False
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
            return ("METHOD_EXTRACTION_FAILED", error_str)
    
    def cancel(self):
        self._cancelled = True
    
    def is_cancelled(self) -> bool:
        return self._cancelled
    
    def is_session_lost(self) -> bool:
        return self._session_lost
    
    def enumerate_classes(
        self,
        progress_callback: Optional[Callable[[int, str], None]] = None
    ) -> List[str]:
        self._logger.info("Starting Java class enumeration (names only)")
        self._classes = []
        
        # Get session number for aggregated logging       
        session_number = None
        for device_id, session_info in frida_session_manager._sessions.items():
            if session_info.get("session") == self.session:
                session_number = session_info.get("session_number")
                break
        
        received = {"done": False, "data": None}
        
        def on_message(message, data):
            if message["type"] == "send":
                payload = message["payload"]
                if payload.get("type") == "classes":
                    received["data"] = payload["data"]
                    received["done"] = True
                    self._logger.info(f"Received {len(payload['data'])} classes from Frida")
            elif message["type"] == "error":
                self._logger.error(f"Frida script error: {message.get('description', 'Unknown error')}")
                self._logger.error(f"Stack: {message.get('stack', 'No stack trace')}")
                received["done"] = True
        
        try:
            self._logger.info("Loading compiled Java enumeration script (with frida-java-bridge)")
            if session_number:
                aggregated_frida_logger.log_script_loaded(session_number, "enumerate_classes.ts", "discovery")
            
            script_code = script_compiler.compile("discovery", "enumerate_classes.ts")
            script = self.session.create_script(script_code)
            script.on("message", on_message)
            
            self._logger.info("Loading script...")
            script.load()
            self._logger.info("Script loaded, waiting for enumeration to complete...")
            
            import time
            start = time.time()
            while not received["done"]:
                time.sleep(0.1)
            
            elapsed = time.time() - start
            self._logger.info(f"Enumeration completed in {elapsed:.2f} seconds")
            
            script.unload()
            if session_number:
                aggregated_frida_logger.log_script_unloaded(session_number, "enumerate_classes.ts")
            
            if received["data"]:
                self._classes = received["data"]
                self._logger.info(f"Enumerated {len(self._classes)} Java classes")
                if session_number:
                    aggregated_frida_logger.log_performance_metric(session_number, "enumerate_classes", "duration", f"{elapsed:.2f}s")
                    aggregated_frida_logger.log_performance_metric(session_number, "enumerate_classes", "class_count", len(self._classes))
            else:
                self._logger.warning("No classes received from enumeration")
            
            if progress_callback:
                progress_callback(len(self._classes), "classes_enumerated")
            
        except Exception as e:
            self._logger.error(f"Class enumeration failed: {e}")
            self._errors.append({"phase": "enumerate_classes", "error": str(e)})
            if session_number:
                aggregated_frida_logger.log_script_error(session_number, "enumerate_classes.ts", str(e))
        
        return self._classes
    
    def enumerate_methods(
        self,
        classes: List[str],
        progress_callback: Optional[Callable[[int, int, str], None]] = None,
        save_callback: Optional[Callable[[str, Dict[str, Any]], None]] = None
    ) -> List[Dict[str, Any]]:
        self._logger.info(f"Starting method enumeration for {len(classes)} classes")
        self._class_data = []
        self._cancelled = False
        
        # Get session number for aggregated logging
        session_number = None
        for device_id, session_info in frida_session_manager._sessions.items():
            if session_info.get("session") == self.session:
                session_number = session_info.get("session_number")
                break
        
        if not classes:
            self._logger.warning("No classes to enumerate methods for")
            return self._class_data
        
        script = None
        try:
            self._logger.info("Loading method enumeration script (RPC-based)")
            if session_number:
                aggregated_frida_logger.log_script_loaded(session_number, "enumerate_methods.ts", "discovery")
            
            script_code = script_compiler.compile("discovery", "enumerate_methods.ts")
            script = self.session.create_script(script_code)
            script.load()
            self._logger.info("Method enumeration script loaded")
            
            import time
            start_time = time.time()
            total = len(classes)
            
            for idx, class_name in enumerate(classes):
                if self._cancelled:
                    self._logger.info(f"Method enumeration cancelled at {idx}/{total}")
                    break
                
                # Report progress more frequently for small batches, less for large
                report_interval = 1 if total < 20 else (5 if total < 100 else 10)
                if progress_callback and (idx % report_interval == 0 or idx == 0):
                    progress_callback(idx + 1, total, class_name)
                
                # Log progress to aggregated logger for large batches
                if session_number and total >= 50 and idx % 25 == 0 and idx > 0:
                    aggregated_frida_logger.log_operation_progress(session_number, "extract_methods", idx, total, class_name)
                
                try:
                    result = script.exports_sync.get_methods(class_name)
                    
                    if result.get("success"):
                        methods = result.get("methods", [])
                        extraction_status = "completed"
                        
                        # Log successful extraction to aggregated logger
                        if session_number:
                            native_count = sum(1 for m in methods if m.get("is_native", False))
                            aggregated_frida_logger.log_class_extracted(session_number, class_name, True, len(methods))
                            
                            # Log classes with 0 methods as warning (might indicate issues)
                            if len(methods) == 0:
                                aggregated_frida_logger.log_warning(session_number, f"[EXTRACT_ZERO] {class_name.split('.')[-1]} - No methods found")
                            
                            # Log native methods if found
                            if native_count > 0:
                                short_name = class_name.split('.')[-1] if '.' in class_name else class_name
                                aggregated_frida_logger.log_debug(session_number, f"[NATIVE_METHODS] {short_name} - {native_count} native methods")
                    else:
                        methods = []
                        error_msg = result.get("error", "Unknown error")
                        error_type_from_frida = result.get("error_type", "")
                        
                        # Map Frida error types to extraction status
                        if error_type_from_frida == "unable_to_load":
                            extraction_status = "unable_to_load"
                            error_type = "UNABLE_TO_LOAD"
                        elif error_type_from_frida == "method_extraction_failed":
                            extraction_status = "attempted"
                            error_type = "METHOD_EXTRACTION_FAILED"
                        else:
                            # Fallback for legacy error detection
                            if "ClassNotFoundException" in error_msg or "NoClassDefFoundError" in error_msg:
                                extraction_status = "unable_to_load"
                                error_type = "CLASS_NOT_FOUND"
                            else:
                                extraction_status = "attempted"
                                error_type = "METHOD_EXTRACTION_FAILED"
                        
                        self._errors.append({
                            "phase": "enumerate_methods",
                            "class": class_name,
                            "error": error_msg,
                            "error_type": error_type
                        })
                        
                        # Log extraction failure to aggregated logger
                        if session_number:
                            aggregated_frida_logger.log_class_extracted(session_number, class_name, False, 0, error_msg, error_type)
                    
                    class_result = {
                        "name": class_name,
                        "method_count": len(methods),
                        "methods": methods,
                        "extraction_status": extraction_status
                    }
                    self._class_data.append(class_result)
                    
                    # Per-class auto-save: Save immediately after each class's methods are extracted
                    if save_callback and result.get("success"):
                        try:
                            save_callback(class_name, class_result)
                            self._logger.debug(f"[AUTO-SAVE] Callback triggered for: {class_name}")
                        except Exception as save_err:
                            self._logger.warning(f"[AUTO-SAVE] Callback failed for {class_name}: {save_err}")
                    
                except Exception as e:
                    error_type, error_message = self._classify_error(e)
                    
                    self._errors.append({
                        "phase": "enumerate_methods",
                        "class": class_name,
                        "error": error_message,
                        "error_type": error_type
                    })
                    
                    if error_type in ["SESSION_DEAD", "SESSION_DETACHED", "TRANSPORT_ERROR"]:
                        self._session_lost = True
                        self._logger.error(f"Session lost during enumeration: {error_type}")
                        break
                    
                    self._class_data.append({
                        "name": class_name,
                        "method_count": 0,
                        "methods": [],
                        "extraction_status": "failed"
                    })
            
            if progress_callback:
                progress_callback(len(self._class_data), total, "complete")
            
            elapsed = time.time() - start_time
            self._logger.info(f"Enumerated methods for {len(self._class_data)} classes")
            total_methods = sum(c["method_count"] for c in self._class_data)
            self._logger.info(f"Total methods found: {total_methods}")
            
            # Log extraction summary to aggregated logger
            if session_number:
                success_count = sum(1 for c in self._class_data if c["method_count"] > 0 or len(c.get("methods", [])) > 0)
                error_count = len(self._errors)
                aggregated_frida_logger.log_extraction_summary(
                    session_number,
                    len(self._class_data),
                    total_methods,
                    success_count,
                    error_count,
                    elapsed
                )
                aggregated_frida_logger.log_performance_metric(session_number, "enumerate_methods", "duration", f"{elapsed:.2f}s")
                aggregated_frida_logger.log_performance_metric(session_number, "enumerate_methods", "classes_processed", len(self._class_data))
                aggregated_frida_logger.log_performance_metric(session_number, "enumerate_methods", "total_methods", total_methods)
            
        except Exception as e:
            self._logger.error(f"Method enumeration failed: {e}")
            self._errors.append({"phase": "enumerate_methods", "error": str(e)})
            if session_number:
                aggregated_frida_logger.log_script_error(session_number, "enumerate_methods.ts", str(e))
        finally:
            if script:
                try:
                    script.unload()
                    self._logger.info("Method enumeration script unloaded")
                    self._logger.info("[OPERATION_COMPLETE] Method enumeration finished")
                    if session_number:
                        aggregated_frida_logger.log_script_unloaded(session_number, "enumerate_methods.ts")
                except:
                    pass
        
        return self._class_data
    
    def get_errors(self) -> List[Dict[str, str]]:
        return self._errors.copy()
    
    def get_stats(self) -> Dict[str, Any]:
        total_methods = sum(c["method_count"] for c in self._class_data)
        native_methods = sum(
            1 for c in self._class_data
            for m in c.get("methods", [])
            if m.get("is_native", False)
        )
        
        return {
            "total_classes": len(self._classes),
            "classes_with_methods": len(self._class_data),
            "total_methods": total_methods,
            "native_methods": native_methods,
            "errors": len(self._errors)
        }
