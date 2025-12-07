# Inclusion/exclusion filter for classes and modules
from typing import Dict, Any, List, Tuple
from device.workshop_tab.config.rules_manager import rules_manager


class DiscoveryFilter:
    def __init__(self, package_id: str, include_system_libs: bool = False):
        self.package_id = package_id
        self.include_system_libs = include_system_libs
        self._rules = rules_manager.get_rules()
        
        self.included_classes: List[Dict[str, Any]] = []
        self.skipped_classes: List[Dict[str, str]] = []
        self.included_modules: List[Dict[str, Any]] = []
        self.skipped_modules: List[Dict[str, str]] = []
    
    def should_include_class(self, class_name: str, class_path: str = None) -> Tuple[bool, str]:
        if class_name.startswith(self.package_id):
            return True, "app_package"
        
        if class_path and self.package_id in class_path:
            return True, "app_path"
        
        if not self.include_system_libs:
            for system_pkg in self._rules.get("system_packages", []):
                if class_name.startswith(system_pkg):
                    return False, f"system_package:{system_pkg}"
        
        return True, "included"
    
    def should_include_module(self, module_name: str, module_path: str) -> Tuple[bool, str]:
        if self.package_id in module_path:
            return True, "app_lib"
        
        if f"/data/app/" in module_path and self.package_id.replace(".", "") in module_path:
            return True, "app_data_path"
        
        if not self.include_system_libs:
            for system_path in self._rules.get("system_paths", []):
                if module_path.startswith(system_path):
                    return False, f"system_path:{system_path}"
        
        return True, "included"
    
    def filter_class(self, class_name: str, class_data: Dict[str, Any], class_path: str = None):
        include, reason = self.should_include_class(class_name, class_path)
        
        if include:
            class_data["source"] = "app" if reason in ["app_package", "app_path"] else "external"
            class_data["filter_reason"] = reason
            self.included_classes.append(class_data)
        else:
            self.skipped_classes.append({
                "name": class_name,
                "reason": reason
            })
        
        return include
    
    def filter_module(self, module_name: str, module_data: Dict[str, Any], module_path: str):
        include, reason = self.should_include_module(module_name, module_path)
        
        if include:
            module_data["is_system"] = reason not in ["app_lib", "app_data_path"]
            module_data["source"] = "app" if not module_data["is_system"] else "system"
            module_data["filter_reason"] = reason
            self.included_modules.append(module_data)
        else:
            self.skipped_modules.append({
                "name": module_name,
                "path": module_path,
                "reason": reason
            })
        
        return include
    
    def get_verification_stats(self) -> Dict[str, Any]:
        total_classes = len(self.included_classes) + len(self.skipped_classes)
        total_modules = len(self.included_modules) + len(self.skipped_modules)
        
        classes_check = f"{len(self.included_classes)} + {len(self.skipped_classes)} = {total_classes}"
        modules_check = f"{len(self.included_modules)} + {len(self.skipped_modules)} = {total_modules}"
        
        classes_ok = len(self.included_classes) + len(self.skipped_classes) == total_classes
        modules_ok = len(self.included_modules) + len(self.skipped_modules) == total_modules
        
        return {
            "total_classes_found": total_classes,
            "app_classes_included": len(self.included_classes),
            "system_classes_skipped": len(self.skipped_classes),
            "total_modules_found": total_modules,
            "app_modules_included": len(self.included_modules),
            "system_modules_skipped": len(self.skipped_modules),
            "system_libraries_included": self.include_system_libs,
            "verification": {
                "classes_check": f"{classes_check} ({'OK' if classes_ok else 'MISMATCH'})",
                "modules_check": f"{modules_check} ({'OK' if modules_ok else 'MISMATCH'})",
                "nothing_lost": classes_ok and modules_ok
            },
            "skipped_classes": self.skipped_classes[:100],
            "skipped_modules": self.skipped_modules[:50]
        }
    
    def reset(self):
        self.included_classes = []
        self.skipped_classes = []
        self.included_modules = []
        self.skipped_modules = []

