# Java class and method enumeration via Frida
from typing import Dict, Any, List, Callable, Optional
from device.workshop_tab.logging.workshop_logger import get_discovery_logger
from device.workshop_tab.discovery.script_compiler import script_compiler


class JavaDiscovery:
    def __init__(self, session, package_id: str, timestamp: str = None):
        self.session = session
        self.package_id = package_id
        self._logger = get_discovery_logger(package_id, timestamp)
        self._classes: List[str] = []
        self._class_data: List[Dict[str, Any]] = []
        self._errors: List[Dict[str, str]] = []
    
    def enumerate_classes(
        self,
        progress_callback: Optional[Callable[[int, str], None]] = None
    ) -> List[str]:
        self._logger.info("Starting Java class enumeration")
        self._classes = []
        
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
            script_code = script_compiler.compile("discovery", "enumerate_classes.ts")
            script = self.session.create_script(script_code)
            script.on("message", on_message)
            
            self._logger.info("Loading script...")
            script.load()
            self._logger.info("Script loaded, waiting for enumeration to complete...")
            
            import time
            timeout = 60  # Increased timeout to 60 seconds
            start = time.time()
            while not received["done"] and (time.time() - start) < timeout:
                time.sleep(0.1)
            
            elapsed = time.time() - start
            self._logger.info(f"Enumeration waited {elapsed:.2f} seconds")
            
            script.unload()
            
            if received["data"]:
                self._classes = received["data"]
                self._logger.info(f"Enumerated {len(self._classes)} Java classes")
            else:
                self._logger.warning(f"No classes received from enumeration after {elapsed:.2f}s")
            
            if progress_callback:
                progress_callback(len(self._classes), "classes_enumerated")
            
        except Exception as e:
            self._logger.error(f"Class enumeration failed: {e}")
            self._errors.append({"phase": "enumerate_classes", "error": str(e)})
        
        return self._classes
    
    def enumerate_methods(
        self,
        classes: List[str],
        progress_callback: Optional[Callable[[int, int, str], None]] = None
    ) -> List[Dict[str, Any]]:
        self._logger.info(f"Starting method enumeration for {len(classes)} classes")
        self._class_data = []
        
        total = len(classes)
        for idx, class_name in enumerate(classes):
            if progress_callback and idx % 50 == 0:
                progress_callback(idx, total, class_name)
            
            methods = self._get_methods_for_class(class_name)
            
            self._class_data.append({
                "name": class_name,
                "method_count": len(methods),
                "methods": methods
            })
        
        self._logger.info(f"Enumerated methods for {len(self._class_data)} classes")
        total_methods = sum(c["method_count"] for c in self._class_data)
        self._logger.info(f"Total methods found: {total_methods}")
        
        return self._class_data
    
    def _get_methods_for_class(self, class_name: str) -> List[Dict[str, Any]]:
        received = {"done": False, "data": None, "success": False, "error": None}
        
        def on_message(message, data):
            if message["type"] == "send":
                payload = message["payload"]
                if payload.get("type") == "methods":
                    received["data"] = payload.get("data", [])
                    received["success"] = payload.get("success", False)
                    received["error"] = payload.get("error")
                    received["done"] = True
            elif message["type"] == "error":
                received["error"] = message.get("description", "Unknown error")
                received["done"] = True
        
        try:
            script_code = script_compiler.compile(
                "discovery", 
                "enumerate_methods.ts",
                template_vars={"CLASS_NAME": class_name}
            )
            script = self.session.create_script(script_code)
            script.on("message", on_message)
            script.load()
            
            import time
            timeout = 10
            start = time.time()
            while not received["done"] and (time.time() - start) < timeout:
                time.sleep(0.05)
            
            script.unload()
            
            if not received["success"] and received["error"]:
                self._errors.append({
                    "phase": "enumerate_methods",
                    "class": class_name,
                    "error": received["error"]
                })
            
            return received["data"] or []
            
        except Exception as e:
            self._errors.append({
                "phase": "enumerate_methods",
                "class": class_name,
                "error": str(e)
            })
            return []
    
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

