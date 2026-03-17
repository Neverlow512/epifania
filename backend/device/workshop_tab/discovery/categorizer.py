# Classification engine for Java classes/methods and native modules/exports
import re
from typing import Dict, Any, List, Tuple, Optional
from device.workshop_tab.config.rules_manager import rules_manager
from device.workshop_tab.logging.workshop_logger import get_categorization_logger


class Categorizer:
    def __init__(self, package_id: str, timestamp: str = None):
        self.package_id = package_id
        self._rules = rules_manager.get_rules()
        self._enabled_categories = rules_manager.get_enabled_categories()
        self._logger = get_categorization_logger(package_id, timestamp)
        
        self._stats = {
            "classes": {
                "total": 0,
                "by_category": {},
                "obfuscated": 0
            },
            "methods": {
                "total": 0,
                "by_category": {},
                "by_confidence": {"high": 0, "medium": 0, "low": 0}
            },
            "modules": {
                "total": 0,
                "by_category": {}
            },
            "exports": {
                "total": 0,
                "by_category": {},
                "by_confidence": {"high": 0, "medium": 0, "low": 0}
            }
        }
    
    def categorize_method(self, method_name: str, class_name: str = None) -> Dict[str, Any]:
        method_lower = method_name.lower()
        
        for category_name, config in self._enabled_categories.items():
            for keyword in config.get("keywords", []):
                if keyword.lower() in method_lower:
                    confidence = "high" if len(keyword) > 3 else "medium"
                    self._update_method_stats(category_name, confidence)
                    return {
                        "method_category": category_name,
                        "method_confidence": confidence,
                        "method_category_reason": f"Keyword: {keyword}"
                    }
        
        self._update_method_stats("Unknown", "low")
        return {
            "method_category": "Unknown",
            "method_confidence": "low",
            "method_category_reason": "No patterns matched"
        }
    
    def categorize_class(self, class_name: str) -> Dict[str, Any]:
        if self._is_obfuscated(class_name):
            self._stats["classes"]["obfuscated"] += 1
            self._update_class_stats("Obfuscated")
            return {
                "class_category": "Obfuscated",
                "class_confidence": "low",
                "class_category_reason": "Obfuscation pattern detected"
            }
        
        for category_name, config in self._enabled_categories.items():
            match, reason = self._match_class_category(class_name, config)
            if match:
                confidence = config.get("confidence", "medium")
                self._update_class_stats(category_name)
                return {
                    "class_category": category_name,
                    "class_confidence": confidence,
                    "class_category_reason": reason
                }
        
        self._update_class_stats("Unknown")
        return {
            "class_category": "Unknown",
            "class_confidence": "low",
            "class_category_reason": "No patterns matched"
        }
    
    def categorize_class_with_methods(self, class_data: Dict[str, Any]) -> Dict[str, Any]:
        class_name = class_data.get("name", "")
        methods = class_data.get("methods", [])
        
        class_result = self.categorize_class(class_name)
        class_data["class_category"] = class_result["class_category"]
        class_data["class_confidence"] = class_result["class_confidence"]
        class_data["class_category_reason"] = class_result["class_category_reason"]
        
        method_category_summary = {}
        for method in methods:
            method_name = method.get("name", "")
            method_result = self.categorize_method(method_name, class_name)
            
            method["method_category"] = method_result["method_category"]
            method["method_confidence"] = method_result["method_confidence"]
            method["method_category_reason"] = method_result["method_category_reason"]
            
            cat = method_result["method_category"]
            method_category_summary[cat] = method_category_summary.get(cat, 0) + 1
        
        class_data["method_category_summary"] = method_category_summary
        
        return class_data
    
    def categorize_classes_batch(self, classes: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        for cls in classes:
            self.categorize_class_with_methods(cls)
        
        self._logger.info(f"Categorized {len(classes)} classes")
        self._logger.info(f"Class stats: {self._stats['classes']}")
        self._logger.info(f"Method stats: {self._stats['methods']}")
        
        return classes
    
    def categorize_module(self, module_name: str, module_path: str = None) -> Dict[str, Any]:
        module_lower = module_name.lower()
        
        for category_name, config in self._enabled_categories.items():
            for keyword in config.get("keywords", []):
                if keyword.lower() in module_lower:
                    confidence = config.get("confidence", "medium")
                    self._update_module_stats(category_name)
                    return {
                        "module_category": category_name,
                        "module_confidence": confidence,
                        "module_category_reason": f"Module name keyword: {keyword}"
                    }
        
        self._update_module_stats("Unknown")
        return {
            "module_category": "Unknown",
            "module_confidence": "low",
            "module_category_reason": "No patterns matched"
        }
    
    def categorize_export(self, export_name: str, module_name: str = None) -> Dict[str, Any]:
        export_lower = export_name.lower()
        
        for category_name, config in self._enabled_categories.items():
            for keyword in config.get("keywords", []):
                if keyword.lower() in export_lower:
                    confidence = "high" if len(keyword) > 3 else "medium"
                    self._update_export_stats(category_name, confidence)
                    return {
                        "export_category": category_name,
                        "export_confidence": confidence,
                        "export_category_reason": f"Keyword: {keyword}"
                    }
        
        self._update_export_stats("Unknown", "low")
        return {
            "export_category": "Unknown",
            "export_confidence": "low",
            "export_category_reason": "No patterns matched"
        }
    
    def categorize_module_with_exports(self, module_data: Dict[str, Any]) -> Dict[str, Any]:
        module_name = module_data.get("name", "")
        module_path = module_data.get("path", "")
        exports = module_data.get("exports", [])
        
        module_result = self.categorize_module(module_name, module_path)
        module_data["module_category"] = module_result["module_category"]
        module_data["module_confidence"] = module_result["module_confidence"]
        module_data["module_category_reason"] = module_result["module_category_reason"]
        
        export_category_summary = {}
        for export in exports:
            export_name = export.get("name", "")
            export_result = self.categorize_export(export_name, module_name)
            
            export["export_category"] = export_result["export_category"]
            export["export_confidence"] = export_result["export_confidence"]
            export["export_category_reason"] = export_result["export_category_reason"]
            
            cat = export_result["export_category"]
            export_category_summary[cat] = export_category_summary.get(cat, 0) + 1
        
        module_data["export_category_summary"] = export_category_summary
        module_data["export_count"] = len(exports)
        
        return module_data
    
    def categorize_modules_batch(self, modules: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        for module in modules:
            self.categorize_module_with_exports(module)
        
        self._logger.info(f"Categorized {len(modules)} modules")
        self._logger.info(f"Module stats: {self._stats['modules']}")
        self._logger.info(f"Export stats: {self._stats['exports']}")
        
        return modules
    
    def _match_class_category(self, class_name: str, config: Dict) -> Tuple[bool, Optional[str]]:
        for package in config.get("packages", []):
            if class_name.startswith(package):
                return True, f"Package prefix: {package}"
        
        class_lower = class_name.lower()
        for keyword in config.get("keywords", []):
            if keyword.lower() in class_lower:
                return True, f"Keyword in class name: {keyword}"
        
        return False, None
    
    def _is_obfuscated(self, class_name: str) -> bool:
        obf_config = self._rules.get("obfuscation_detection", {})
        min_single_char = obf_config.get("min_package_parts_single_char", 2)
        max_class_len = obf_config.get("max_class_name_length", 2)
        
        parts = class_name.split(".")
        if len(parts) > 1:
            single_char_parts = sum(1 for p in parts[:-1] if len(p) == 1)
            if single_char_parts >= min_single_char:
                return True
        
        class_simple = parts[-1] if parts else class_name
        if len(class_simple) <= max_class_len and class_simple.isalpha():
            if not class_simple[0].isupper():
                return True
            if len(class_simple) == 1:
                return True
        
        if re.match(r'^[a-z]{1,2}\.[a-z]{1,2}\.[a-z]{1,2}', class_name):
            return True
        
        return False
    
    def _update_class_stats(self, category: str):
        self._stats["classes"]["total"] += 1
        if category not in self._stats["classes"]["by_category"]:
            self._stats["classes"]["by_category"][category] = 0
        self._stats["classes"]["by_category"][category] += 1
    
    def _update_method_stats(self, category: str, confidence: str):
        self._stats["methods"]["total"] += 1
        if category not in self._stats["methods"]["by_category"]:
            self._stats["methods"]["by_category"][category] = 0
        self._stats["methods"]["by_category"][category] += 1
        
        if confidence in self._stats["methods"]["by_confidence"]:
            self._stats["methods"]["by_confidence"][confidence] += 1
    
    def _update_module_stats(self, category: str):
        self._stats["modules"]["total"] += 1
        if category not in self._stats["modules"]["by_category"]:
            self._stats["modules"]["by_category"][category] = 0
        self._stats["modules"]["by_category"][category] += 1
    
    def _update_export_stats(self, category: str, confidence: str):
        self._stats["exports"]["total"] += 1
        if category not in self._stats["exports"]["by_category"]:
            self._stats["exports"]["by_category"][category] = 0
        self._stats["exports"]["by_category"][category] += 1
        
        if confidence in self._stats["exports"]["by_confidence"]:
            self._stats["exports"]["by_confidence"][confidence] += 1
    
    def get_stats(self) -> Dict[str, Any]:
        return {
            "classes": self._stats["classes"].copy(),
            "methods": self._stats["methods"].copy(),
            "modules": self._stats["modules"].copy(),
            "exports": self._stats["exports"].copy()
        }
