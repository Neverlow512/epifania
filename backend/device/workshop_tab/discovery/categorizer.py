# Classification engine for Java classes and native exports
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
            "total_categorized": 0,
            "by_category": {},
            "by_confidence": {"high": 0, "medium": 0, "low": 0},
            "obfuscated": 0,
            "unknown": 0
        }
    
    def categorize_class(self, class_name: str, methods: List[Dict] = None) -> Dict[str, Any]:
        if self._is_obfuscated(class_name):
            self._stats["obfuscated"] += 1
            self._logger.debug(f"Obfuscated: {class_name}")
            return {
                "category": "Obfuscated",
                "confidence": "low",
                "reason": "Obfuscation pattern detected"
            }
        
        for category_name, config in self._enabled_categories.items():
            match, reason = self._match_category(class_name, config)
            if match:
                confidence = config.get("confidence", "medium")
                self._update_stats(category_name, confidence)
                self._logger.debug(f"{category_name} ({confidence}): {class_name} - {reason}")
                return {
                    "category": category_name,
                    "confidence": confidence,
                    "reason": reason
                }
        
        if methods:
            for method in methods:
                method_name = method.get("name", "")
                for category_name, config in self._enabled_categories.items():
                    for keyword in config.get("keywords", []):
                        if keyword.lower() in method_name.lower():
                            self._update_stats(category_name, "medium")
                            reason = f"Method keyword: {keyword} in {method_name}"
                            self._logger.debug(f"{category_name} (medium): {class_name} - {reason}")
                            return {
                                "category": category_name,
                                "confidence": "medium",
                                "reason": reason
                            }
        
        self._stats["unknown"] += 1
        return {
            "category": "Unknown",
            "confidence": "low",
            "reason": "No patterns matched"
        }
    
    def categorize_export(self, export_name: str, module_name: str = None) -> Dict[str, Any]:
        for category_name, config in self._enabled_categories.items():
            for keyword in config.get("keywords", []):
                if keyword.lower() in export_name.lower():
                    confidence = config.get("confidence", "medium")
                    self._update_stats(category_name, confidence)
                    return {
                        "category": category_name,
                        "confidence": confidence,
                        "reason": f"Export keyword: {keyword}"
                    }
        
        self._stats["unknown"] += 1
        return {
            "category": "Unknown",
            "confidence": "low",
            "reason": "No patterns matched"
        }
    
    def _match_category(self, class_name: str, config: Dict) -> Tuple[bool, Optional[str]]:
        for package in config.get("packages", []):
            if class_name.startswith(package):
                return True, f"Package prefix: {package}"
        
        class_lower = class_name.lower()
        for keyword in config.get("keywords", []):
            if keyword.lower() in class_lower:
                return True, f"Keyword in class: {keyword}"
        
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
    
    def _update_stats(self, category: str, confidence: str):
        self._stats["total_categorized"] += 1
        
        if category not in self._stats["by_category"]:
            self._stats["by_category"][category] = 0
        self._stats["by_category"][category] += 1
        
        if confidence in self._stats["by_confidence"]:
            self._stats["by_confidence"][confidence] += 1
    
    def get_stats(self) -> Dict[str, Any]:
        return self._stats.copy()
    
    def categorize_classes_batch(self, classes: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        for cls in classes:
            class_name = cls.get("name", "")
            methods = cls.get("methods", [])
            
            result = self.categorize_class(class_name, methods)
            cls["category"] = result["category"]
            cls["confidence"] = result["confidence"]
            cls["reason"] = result["reason"]
        
        self._logger.info(f"Categorized {len(classes)} classes")
        self._logger.info(f"Stats: {self._stats}")
        
        return classes
    
    def categorize_exports_batch(self, modules: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        for module in modules:
            module_name = module.get("name", "")
            exports = module.get("exports", [])
            
            for export in exports:
                export_name = export.get("name", "")
                result = self.categorize_export(export_name, module_name)
                export["category"] = result["category"]
                export["confidence"] = result["confidence"]
        
        return modules

