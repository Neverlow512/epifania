# Native module and export enumeration via Frida
from typing import Dict, Any, List, Callable, Optional
from device.workshop_tab.logging.workshop_logger import get_discovery_logger
from device.workshop_tab.discovery.script_loader import script_loader


class NativeDiscovery:
    def __init__(self, session, package_id: str, timestamp: str = None):
        self.session = session
        self.package_id = package_id
        self._logger = get_discovery_logger(package_id, timestamp)
        self._modules: List[Dict[str, Any]] = []
        self._errors: List[Dict[str, str]] = []
    
    def enumerate_modules(
        self,
        progress_callback: Optional[Callable[[int, str], None]] = None
    ) -> List[Dict[str, Any]]:
        self._logger.info("Starting native module enumeration")
        self._modules = []
        
        try:
            # Load the module enumeration script
            script_code = script_loader.load_script("discovery", "enumerate_modules.js")
            
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
            timeout = 30
            start = time.time()
            while not received["done"] and (time.time() - start) < timeout:
                time.sleep(0.1)
            
            script.unload()
            
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
            
            if progress_callback:
                progress_callback(len(self._modules), "modules_enumerated")
            
        except Exception as e:
            self._logger.error(f"Module enumeration failed: {e}")
            self._errors.append({"phase": "enumerate_modules", "error": str(e)})
        
        return self._modules
    
    def enumerate_exports(
        self,
        modules: List[Dict[str, Any]],
        progress_callback: Optional[Callable[[int, int, str], None]] = None
    ) -> List[Dict[str, Any]]:
        self._logger.info(f"Starting export enumeration for {len(modules)} modules")
        
        total = len(modules)
        for idx, module in enumerate(modules):
            if progress_callback and idx % 10 == 0:
                progress_callback(idx, total, module.get("name", ""))
            
            exports = self._get_exports_for_module(module["name"])
            module["exports"] = exports
            module["export_count"] = len(exports)
        
        total_exports = sum(m.get("export_count", 0) for m in modules)
        self._logger.info(f"Enumerated {total_exports} exports across {len(modules)} modules")
        
        return modules
    
    def _get_exports_for_module(self, module_name: str) -> List[Dict[str, Any]]:
        try:
            # Load the exports enumeration script with the module name
            script_code = script_loader.load_script(
                "discovery",
                "enumerate_exports.js",
                template_vars={"MODULE_NAME": module_name}
            )
            
            received = {"done": False, "data": None, "success": False}
            
            def on_message(message, data):
                if message["type"] == "send":
                    payload = message["payload"]
                    if payload.get("type") == "exports":
                        received["data"] = payload.get("data", [])
                        received["success"] = payload.get("success", False)
                        received["done"] = True
            
            script = self.session.create_script(script_code)
            script.on("message", on_message)
            script.load()
            
            import time
            timeout = 10
            start = time.time()
            while not received["done"] and (time.time() - start) < timeout:
                time.sleep(0.05)
            
            script.unload()
            
            if not received["success"]:
                return []
            
            export_data = []
            for export in received["data"]:
                export_data.append({
                    "name": export["name"],
                    "address": export["address"],
                    "type": export["type"]
                })
            
            return export_data
            
        except Exception as e:
            self._errors.append({
                "phase": "enumerate_exports",
                "module": module_name,
                "error": str(e)
            })
            return []
    
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

